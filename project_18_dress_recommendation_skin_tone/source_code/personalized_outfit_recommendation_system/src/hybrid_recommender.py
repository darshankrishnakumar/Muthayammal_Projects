"""Stage 9: Hybrid Multi-Modal Ensemble Recommendation Engine."""

from typing import Dict, Any, List, Optional, Tuple
import os
import pandas as pd
import numpy as np

import config
from src.text_recommender import TFIDFSearchEngine
from src.clip_recommender import CLIPVisualRecommender
from src.train_gbm import predict_category
from src.attribute_rules import calculate_attribute_compatibility_score


class HybridOutfitRecommender:
    """Ensemble recommender harmonizing TF-IDF, CLIP, GBM, and Attribute rules."""

    def __init__(self, catalogue_path: str = config.CATALOGUE_PATH):
        self.catalogue_path = catalogue_path
        self.df = pd.read_csv(catalogue_path) if os.path.exists(catalogue_path) else None
        self.text_engine = TFIDFSearchEngine(catalogue_path=catalogue_path)
        self.clip_engine = CLIPVisualRecommender()

    def reload_catalogue(self):
        """Reloads catalogue and reinits text index."""
        if os.path.exists(self.catalogue_path):
            self.df = pd.read_csv(self.catalogue_path)
            self.text_engine = TFIDFSearchEngine(catalogue_path=self.catalogue_path)

    def recommend(
        self,
        query_text: Optional[str] = None,
        reference_image_bgr: Optional[np.ndarray] = None,
        skin_tone: Optional[str] = "Medium",
        undertone: Optional[str] = "Warm",
        body_shape: Optional[str] = "Rectangle / Hourglass",
        preferred_category: Optional[str] = None,
        preferred_occasion: Optional[str] = None,
        preferred_colors: Optional[List[str]] = None,
        preferred_styles: Optional[List[str]] = None,
        preferred_fit: Optional[str] = None,
        budget_max: Optional[float] = None,
        weights: Optional[Dict[str, float]] = None,
        top_k: int = 6,
    ) -> Dict[str, Any]:
        """Calculates multi-modal hybrid ensemble scores and returns ranked outfit recommendations."""
        if self.df is None or len(self.df) == 0:
            self.reload_catalogue()
            if self.df is None or len(self.df) == 0:
                return {"recommendations": [], "total_candidates": 0, "gbm_prediction": ("All", 0.0)}

        # 1. Weights configuration & Dynamic Renormalization
        if weights is None:
            w_dict = dict(config.DEFAULT_WEIGHTS)
        else:
            w_dict = dict(weights)

        w_tfidf = float(w_dict.get("tfidf", 0.30))
        w_clip = float(w_dict.get("clip", 0.30))
        w_gbm = float(w_dict.get("gbm", 0.25))
        w_attr = float(w_dict.get("attributes", 0.15))

        # Check if reference image is present for CLIP
        has_ref_image = reference_image_bgr is not None and reference_image_bgr.size > 0
        ref_clip_emb = None
        if has_ref_image and self.clip_engine.is_available():
            ref_clip_emb = self.clip_engine.extract_embedding_from_image(reference_image_bgr)

        if ref_clip_emb is None:
            # Reallocate CLIP weight proportionally across other 3 signals
            remaining = w_tfidf + w_gbm + w_attr
            if remaining > 0:
                w_tfidf += w_clip * (w_tfidf / remaining)
                w_gbm += w_clip * (w_gbm / remaining)
                w_attr += w_clip * (w_attr / remaining)
            w_clip = 0.0

        total_w = w_tfidf + w_clip + w_gbm + w_attr
        if total_w > 0:
            w_tfidf /= total_w
            w_clip /= total_w
            w_gbm /= total_w
            w_attr /= total_w

        # 2. Run GBM demographic category affinity prediction
        gbm_features = {
            "body_shape": body_shape,
            "skin_tone": skin_tone,
            "undertone": undertone,
            "preferred_style": preferred_styles[0] if preferred_styles else "Classic",
            "preferred_occasion": preferred_occasion if preferred_occasion else "Casual",
            "preferred_colour": preferred_colors[0] if preferred_colors else "Blue",
            "budget_max": budget_max if budget_max else 5000.0,
        }
        gbm_cat, gbm_conf = predict_category(gbm_features)

        # 3. TF-IDF Textual Search Matrix & Raw Scores
        search_query = query_text if query_text and query_text.strip() != "" else (
            f"{preferred_occasion or 'Casual'} {preferred_styles[0] if preferred_styles else ''} "
            f"{preferred_colors[0] if preferred_colors else ''} {body_shape or ''}"
        )
        # Search text candidates
        tfidf_res = self.text_engine.search(
            query=search_query,
            category=preferred_category,
            max_budget=budget_max,
            top_k=len(self.df),
        )
        tfidf_dict = {r["item_id"]: r["tfidf_score"] for r in tfidf_res}

        # 4. Score every eligible candidate
        ranked_candidates = []
        for _, row in self.df.iterrows():
            item_id = str(row["item_id"])
            price = float(row["price"])
            category = str(row["category"])

            # Mandatory hard filters
            if preferred_category and preferred_category != "All":
                if category.strip().lower() != preferred_category.strip().lower():
                    continue

            if budget_max and budget_max > 0:
                if price > budget_max:
                    continue

            # Component scores in [0.0, 1.0]
            s_tfidf = tfidf_dict.get(item_id, 0.0)
            s_clip = self.clip_engine.compute_similarity(ref_clip_emb, item_id) if ref_clip_emb is not None else 0.5
            s_gbm = 1.0 if category.lower() == gbm_cat.lower() else (0.5 if gbm_cat == "All" else 0.2)
            s_attr, reasons = calculate_attribute_compatibility_score(
                item=row.to_dict(),
                skin_tone=skin_tone,
                undertone=undertone,
                body_shape=body_shape,
                preferred_colors=preferred_colors,
                preferred_styles=preferred_styles,
                preferred_occasion=preferred_occasion,
                preferred_fit=preferred_fit,
                budget_max=budget_max,
            )

            # Final ensemble score
            final_score = (w_tfidf * s_tfidf) + (w_clip * s_clip) + (w_gbm * s_gbm) + (w_attr * s_attr)
            final_score = round(max(0.0, min(1.0, final_score)), 4)

            # Human-readable summary
            summary_reason = " • ".join(reasons[:3])

            ranked_candidates.append({
                "item_id": item_id,
                "item_name": row["item_name"],
                "category": category,
                "price": price,
                "primary_color": row["primary_color"],
                "occasion": row["occasion"],
                "fit": row.get("fit", "Regular Fit"),
                "fabric": row.get("fabric", "Cotton"),
                "image_path": row["image_path"],
                "description": row["description"],
                "final_score": final_score,
                "component_scores": {
                    "tfidf": round(s_tfidf, 3),
                    "clip": round(s_clip, 3),
                    "gbm": round(s_gbm, 3),
                    "attributes": round(s_attr, 3),
                },
                "summary_reason": summary_reason,
            })

        # Sort by final score
        ranked_candidates.sort(key=lambda x: x["final_score"], reverse=True)

        return {
            "recommendations": ranked_candidates[:top_k],
            "total_candidates": len(ranked_candidates),
            "gbm_prediction": (gbm_cat, gbm_conf),
            "weights_used": {
                "tfidf": round(w_tfidf, 2),
                "clip": round(w_clip, 2),
                "gbm": round(w_gbm, 2),
                "attributes": round(w_attr, 2),
            },
            "has_visual_clip": ref_clip_emb is not None,
        }
