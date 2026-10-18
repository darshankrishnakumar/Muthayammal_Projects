"""Hybrid Recommendation Engine.

Combines TF-IDF textual matching, CLIP visual similarity,
Gradient Boosting preference prediction, and rule-based attribute compatibility.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import config
from backend.dataset_loader import load_catalogue
from backend.tfidf_recommender import TFIDFRecommender
from backend.clip_recommender import CLIPRecommender
from backend.gbm_recommender import predict_preferred_category


class HybridRecommendationEngine:
    """Multi-modal recommendation engine combining TF-IDF, CLIP, and Gradient Boosting."""

    def __init__(self, catalogue_df: Optional[pd.DataFrame] = None):
        if catalogue_df is None:
            self.catalogue = load_catalogue()
        else:
            self.catalogue = catalogue_df.copy().reset_index(drop=True)

        self.tfidf_engine = TFIDFRecommender(self.catalogue)
        self.clip_engine = CLIPRecommender()

    def calculate_attribute_compatibility(
        self,
        row: pd.Series,
        skin_tone: Optional[str] = None,
        undertone: Optional[str] = None,
        body_shape: Optional[str] = None,
    ) -> float:
        """Calculates a heuristic compatibility score in [0.0, 1.0] between outfit metadata and physical profile."""
        score = 0.5  # neutral baseline
        bonuses = 0.0
        checks = 0

        # 1. Skin tone compatibility check
        if skin_tone and skin_tone != "Unknown":
            checks += 1
            suitable_tones = str(row.get("suitable_skin_tones", "")).lower()
            if skin_tone.lower() in suitable_tones or "all" in suitable_tones:
                bonuses += 1.0
            else:
                bonuses += 0.2

        # 2. Undertone compatibility check
        if undertone and undertone != "Unknown":
            checks += 1
            suitable_unders = str(row.get("suitable_undertones", "")).lower()
            if undertone.lower() in suitable_unders or "all" in suitable_unders:
                bonuses += 1.0
            else:
                bonuses += 0.2

        # 3. Body shape compatibility check
        if body_shape and body_shape != "Unknown":
            checks += 1
            compat_shapes = str(row.get("compatible_body_shapes", "")).lower()
            if body_shape.lower() in compat_shapes or "all" in compat_shapes:
                bonuses += 1.0
            else:
                bonuses += 0.2

        if checks > 0:
            return float(np.clip(bonuses / checks, 0.0, 1.0))
        return score

    def recommend(
        self,
        user_img_bgr: Optional[np.ndarray] = None,
        query_text: Optional[str] = None,
        preferred_styles: Optional[str] = None,
        preferred_colours: Optional[str] = None,
        preferred_occasions: Optional[str] = None,
        preferred_categories: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        skin_tone: Optional[str] = None,
        undertone: Optional[str] = None,
        body_shape: Optional[str] = None,
        weights: Optional[Dict[str, float]] = None,
        top_k: int = 6,
    ) -> Dict[str, Any]:
        """Runs the hybrid recommendation pipeline and returns ranked candidates."""
        if weights is None:
            weights = dict(config.DEFAULT_WEIGHTS)

        # Normalize weights
        w_tfidf = float(weights.get("tfidf", 0.40))
        w_clip = float(weights.get("clip", 0.25))
        w_gbm = float(weights.get("gbm", 0.20))
        w_attr = float(weights.get("attributes", 0.15))

        # Check if CLIP is usable (needs user image)
        has_user_image = user_img_bgr is not None and user_img_bgr.size > 0
        if not has_user_image:
            # Reallocate clip weight proportionally across other components
            remaining_w = w_tfidf + w_gbm + w_attr
            if remaining_w > 0:
                w_tfidf += w_clip * (w_tfidf / remaining_w)
                w_gbm += w_clip * (w_gbm / remaining_w)
                w_attr += w_clip * (w_attr / remaining_w)
            w_clip = 0.0

        total_weight = w_tfidf + w_clip + w_gbm + w_attr
        if total_weight > 0:
            w_tfidf /= total_weight
            w_clip /= total_weight
            w_gbm /= total_weight
            w_attr /= total_weight

        # 1. Run Gradient Boosting Model prediction
        features_dict = {
            "body_shape": body_shape if body_shape else "Unknown",
            "skin_tone": skin_tone if skin_tone else "Unknown",
            "undertone": undertone if undertone else "Unknown",
            "preferred_style": preferred_styles.split(",")[0].strip() if preferred_styles else "Classic",
            "preferred_occasion": preferred_occasions.split(",")[0].strip() if preferred_occasions else "Casual",
            "preferred_colour": preferred_colours.split(",")[0].strip() if preferred_colours else "Blue",
            "budget_max": float(budget_max) if budget_max and budget_max > 0 else 5000.0,
        }
        gbm_pred_category, gbm_confidence = predict_preferred_category(features_dict)

        # 2. Compute TF-IDF text similarity
        query_string = self.tfidf_engine.build_query_string(
            user_query_text=query_text,
            preferred_styles=preferred_styles,
            preferred_colours=preferred_colours,
            preferred_occasions=preferred_occasions,
            preferred_categories=preferred_categories,
            skin_tone=skin_tone,
            undertone=undertone,
            body_shape=body_shape,
        )
        tfidf_scores = self.tfidf_engine.compute_similarity(query_string)

        # 3. Compute CLIP visual similarity
        cat_paths = self.catalogue["image_path"].tolist()
        if has_user_image and w_clip > 0:
            clip_scores = self.clip_engine.compute_visual_similarity(user_img_bgr, cat_paths)
        else:
            clip_scores = np.zeros(len(self.catalogue), dtype=float)

        # 4. Rank items and apply constraints
        candidates = []
        for idx in range(len(self.catalogue)):
            row = self.catalogue.iloc[idx]
            price = float(row.get("price", 0.0))

            # Hard filter: Budget
            if budget_min is not None and price < budget_min:
                continue
            if budget_max is not None and budget_max > 0 and price > budget_max:
                continue

            # Hard filter: Category (if user explicitly provided a category filter)
            if preferred_categories and preferred_categories != "All":
                selected_cats = [c.strip().lower() for c in preferred_categories.split(",")]
                if row["category"].strip().lower() not in selected_cats:
                    continue

            # Hard filter: Occasion (if user selected specific occasion)
            if preferred_occasions and preferred_occasions != "All":
                selected_occ = [o.strip().lower() for o in preferred_occasions.split(",")]
                if row["occasion"].strip().lower() not in selected_occ:
                    continue

            s_tfidf = float(tfidf_scores[idx])
            s_clip = float(clip_scores[idx]) if has_user_image else 0.0

            # GBM Category alignment score
            s_gbm = 0.0
            if gbm_pred_category is not None:
                if str(row["category"]).strip().lower() == gbm_pred_category.strip().lower():
                    s_gbm = float(gbm_confidence) if gbm_confidence else 1.0
                elif str(row.get("garment_type", "")).strip().lower() in gbm_pred_category.strip().lower():
                    s_gbm = 0.5 * (float(gbm_confidence) if gbm_confidence else 1.0)

            # Attribute compatibility
            s_attr = self.calculate_attribute_compatibility(
                row, skin_tone=skin_tone, undertone=undertone, body_shape=body_shape
            )

            # Final weighted composite score
            final_score = (
                w_tfidf * s_tfidf +
                w_clip * s_clip +
                w_gbm * s_gbm +
                w_attr * s_attr
            )
            final_score = float(np.clip(final_score, 0.0, 1.0))

            # Explain recommendation reasons
            reasons = []
            if s_tfidf > 0.15:
                reasons.append("Strong textual alignment with style preferences")
            if has_user_image and s_clip > 0.65:
                reasons.append("Visually harmonious aesthetic matching photo embedding")
            if s_gbm > 0.4:
                reasons.append(f"Matches ML predicted category ({gbm_pred_category})")
            if s_attr >= 0.7:
                reasons.append(f"Tailored for {skin_tone or 'your'} skin tone & {body_shape or 'silhouette'}")
            reasons.append(f"Ideal for {row['occasion']} ({row['style']} style)")

            candidates.append({
                "outfit_id": row["outfit_id"],
                "outfit_name": row["outfit_name"],
                "category": row["category"],
                "garment_type": row["garment_type"],
                "description": row["description"],
                "dominant_colour": row["dominant_colour"],
                "occasion": row["occasion"],
                "style": row["style"],
                "season": row["season"],
                "price": price,
                "image_path": row["image_path"],
                "final_score": round(final_score, 4),
                "component_scores": {
                    "tfidf_score": round(s_tfidf, 4),
                    "clip_score": round(s_clip, 4) if has_user_image else None,
                    "gbm_score": round(s_gbm, 4),
                    "attribute_score": round(s_attr, 4),
                },
                "recommendation_reasons": reasons,
                "summary_reason": " • ".join(reasons[:3]),
            })

        # Rank descending
        candidates.sort(key=lambda x: x["final_score"], reverse=True)

        return {
            "query_string": query_string,
            "gbm_predicted_category": gbm_pred_category,
            "gbm_confidence": gbm_confidence,
            "applied_weights": {
                "tfidf": round(w_tfidf, 3),
                "clip": round(w_clip, 3),
                "gbm": round(w_gbm, 3),
                "attributes": round(w_attr, 3),
            },
            "recommendations": candidates[:top_k],
            "total_candidates": len(candidates),
        }
