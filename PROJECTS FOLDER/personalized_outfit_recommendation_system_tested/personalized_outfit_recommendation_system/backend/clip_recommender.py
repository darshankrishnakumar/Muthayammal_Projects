"""CLIP Visual Recommender Module.

Extracts deep visual embeddings using OpenVINO if compiled XML model
is present, with high-performance PyTorch open_clip as native fallback.
"""

import os
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import config

try:
    import torch
except Exception:
    torch = None

try:
    from openvino.runtime import Core
    ie = Core()
except Exception:
    ie = None


class CLIPRecommender:
    """Extracts CLIP visual embeddings and computes image-to-image similarity."""

    def __init__(self):
        self.ov_compiled = self._load_ov_model()
        self.pt_model = None
        self.pt_preprocess = None
        if self.ov_compiled is None:
            self._load_pytorch_model()
        self.embedding_cache: Dict[str, np.ndarray] = {}

    def _load_ov_model(self):
        """Attempts to load OpenVINO compiled model."""
        if ie is not None and os.path.exists(config.OV_CLIP_PATH):
            try:
                compiled = ie.compile_model(config.OV_CLIP_PATH, "GPU")
                print(f"[INFO] CLIP OpenVINO loaded on GPU")
                return compiled
            except Exception:
                try:
                    compiled = ie.compile_model(config.OV_CLIP_PATH, "CPU")
                    print(f"[INFO] CLIP OpenVINO loaded on CPU")
                    return compiled
                except Exception as e:
                    print(f"[WARNING] OpenVINO compilation failed: {e}")
                    return None
        return None

    def _load_pytorch_model(self):
        """Loads PyTorch open_clip model as robust fallback."""
        try:
            import open_clip
            model, _, preprocess = open_clip.create_model_and_transforms(
                config.OPEN_CLIP_MODEL_NAME, pretrained=config.OPEN_CLIP_PRETRAINED
            )
            model.eval()
            self.pt_model = model
            self.pt_preprocess = preprocess
            print(f"[INFO] Loaded PyTorch open_clip ({config.OPEN_CLIP_MODEL_NAME})")
        except Exception as e:
            print(f"[WARNING] PyTorch open_clip loading failed: {e}")

    def get_embedding(self, img_bgr: np.ndarray) -> Optional[np.ndarray]:
        """Generates normalized (1, 512) CLIP embedding vector."""
        if img_bgr is None or img_bgr.size == 0:
            return None

        # 1. OpenVINO inference
        if self.ov_compiled is not None:
            try:
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                img_resized = cv2.resize(img_rgb, (224, 224)).astype(np.float32) / 255.0
                img_transposed = np.expand_dims(img_resized.transpose(2, 0, 1), 0)
                output_layer = self.ov_compiled.output(0)
                emb = self.ov_compiled([img_transposed])[output_layer].astype(np.float32)
                norm = emb / np.linalg.norm(emb)
                return norm.reshape(1, -1)
            except Exception as e:
                print(f"[WARNING] OpenVINO embedding failed: {e}")

        # 2. PyTorch open_clip inference
        if self.pt_model is not None and self.pt_preprocess is not None:
            try:
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img_rgb)
                tensor = self.pt_preprocess(pil_img).unsqueeze(0)
                with torch.no_grad():
                    emb = self.pt_model.encode_image(tensor).cpu().numpy().astype(np.float32)
                    norm = emb / np.linalg.norm(emb)
                    return norm.reshape(1, -1)
            except Exception as e:
                print(f"[WARNING] PyTorch CLIP embedding failed: {e}")

        return None

    def get_image_embedding_from_file(self, img_path: str) -> Optional[np.ndarray]:
        """Returns cached embedding from an image file path."""
        abs_path = os.path.join(config.BASE_DIR, img_path) if not os.path.isabs(img_path) else img_path
        if abs_path in self.embedding_cache:
            return self.embedding_cache[abs_path]

        if not os.path.exists(abs_path):
            return None

        img = cv2.imread(abs_path)
        if img is None:
            return None

        emb = self.get_embedding(img)
        if emb is not None:
            self.embedding_cache[abs_path] = emb
        return emb

    def compute_visual_similarity(
        self,
        user_img_bgr: np.ndarray,
        catalogue_image_paths: List[str],
    ) -> np.ndarray:
        """Computes visual cosine similarities for a list of catalogue image paths.

        Returns:
            1D numpy array of normalized scores in [0.0, 1.0].
        """
        n_items = len(catalogue_image_paths)
        user_emb = self.get_embedding(user_img_bgr)
        if user_emb is None:
            # Return neutral baseline if user image or CLIP unavailable
            return np.full(n_items, 0.5, dtype=float)

        scores = np.zeros(n_items, dtype=float)
        for i, path in enumerate(catalogue_image_paths):
            cat_emb = self.get_image_embedding_from_file(path)
            if cat_emb is not None:
                sim = float(cosine_similarity(user_emb, cat_emb)[0][0])
                # Map [-1.0, 1.0] cosine to [0.0, 1.0] scale
                normalized_sim = np.clip((sim + 1.0) / 2.0, 0.0, 1.0)
                scores[i] = normalized_sim
            else:
                scores[i] = 0.5

        return scores
