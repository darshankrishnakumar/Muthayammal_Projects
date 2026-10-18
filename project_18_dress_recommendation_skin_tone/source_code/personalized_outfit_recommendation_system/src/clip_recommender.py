"""Stage 6: Pretrained CLIP Visual Feature Extractor and Embedding Caching."""

import os
from typing import Dict, Any, List, Optional, Tuple
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
    import open_clip
except Exception:
    open_clip = None

try:
    from openvino.runtime import Core
    ie = Core()
except Exception:
    ie = None


class CLIPVisualRecommender:
    """Pretrained OpenCLIP ViT-B-32 visual feature extractor with offline caching."""

    def __init__(self, cache_path: str = config.CLIP_CACHE_PATH):
        self.cache_path = cache_path
        self.model = None
        self.preprocess = None
        self.ov_compiled = self._try_load_openvino()
        self.cached_embeddings: Dict[str, np.ndarray] = {}
        self.cached_ids: List[str] = []
        self._load_cache()

        if self.ov_compiled is None:
            self._try_load_openclip()

    def _try_load_openvino(self):
        if ie is not None and os.path.exists(config.OV_CLIP_PATH):
            try:
                return ie.compile_model(config.OV_CLIP_PATH, "CPU")
            except Exception:
                return None
        return None

    def _try_load_openclip(self):
        if torch is not None and open_clip is not None:
            try:
                model, _, preprocess = open_clip.create_model_and_transforms(
                    config.OPEN_CLIP_MODEL_NAME, pretrained=config.OPEN_CLIP_PRETRAINED
                )
                model.eval()
                self.model = model
                self.preprocess = preprocess
            except Exception:
                self.model = None

    def is_available(self) -> bool:
        """Returns True if a neural network backend (OpenVINO or OpenCLIP) is loaded."""
        return (self.ov_compiled is not None) or (self.model is not None)

    def extract_embedding_from_image(self, pil_or_array) -> Optional[np.ndarray]:
        """Extracts normalized 512-dim embedding vector."""
        if not self.is_available() or pil_or_array is None:
            return None

        # Convert to PIL Image
        if isinstance(pil_or_array, np.ndarray):
            if len(pil_or_array.shape) == 3 and pil_or_array.shape[2] == 3:
                rgb = cv2.cvtColor(pil_or_array, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb)
            else:
                return None
        else:
            pil_img = pil_or_array

        # 1. OpenCLIP PyTorch path
        if self.model is not None and self.preprocess is not None and torch is not None:
            try:
                tensor = self.preprocess(pil_img).unsqueeze(0)
                with torch.no_grad():
                    emb = self.model.encode_image(tensor).cpu().numpy().astype(np.float32)
                    norm = emb / np.linalg.norm(emb)
                    return norm.reshape(1, -1)
            except Exception:
                pass

        # 2. OpenVINO path
        if self.ov_compiled is not None:
            try:
                img_resized = pil_img.resize((224, 224))
                arr = np.array(img_resized).astype(np.float32) / 255.0
                arr_t = np.expand_dims(arr.transpose(2, 0, 1), 0)
                out_layer = self.ov_compiled.output(0)
                emb = self.ov_compiled([arr_t])[out_layer].astype(np.float32)
                norm = emb / np.linalg.norm(emb)
                return norm.reshape(1, -1)
            except Exception:
                pass

        return None

    def _load_cache(self):
        """Loads cached embeddings from disk."""
        if os.path.exists(self.cache_path):
            try:
                data = np.load(self.cache_path, allow_pickle=True)
                self.cached_ids = list(data["ids"])
                matrix = data["embeddings"]
                for i, item_id in enumerate(self.cached_ids):
                    self.cached_embeddings[item_id] = matrix[i].reshape(1, -1)
            except Exception:
                self.cached_embeddings = {}
                self.cached_ids = []

    def compute_similarity(self, ref_embedding: np.ndarray, item_id: str) -> float:
        """Calculates cosine similarity between reference embedding and cached catalog item."""
        if ref_embedding is None or item_id not in self.cached_embeddings:
            return 0.5  # Neutral fallback

        cat_emb = self.cached_embeddings[item_id]
        raw_sim = float(cosine_similarity(ref_embedding, cat_emb)[0][0])
        # Rescale [-1, 1] to [0, 1]
        norm_score = max(0.0, min(1.0, (raw_sim + 1.0) / 2.0))
        return norm_score
