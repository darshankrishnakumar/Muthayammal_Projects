"""TF-IDF Recommendation Engine for Clothing Catalogue.

Uses Scikit-learn's TfidfVectorizer and cosine_similarity to match
textual clothing attributes with user preferences.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFRecommender:
    """TF-IDF content-based recommender for clothing catalog."""

    def __init__(self, catalogue_df: pd.DataFrame):
        self.df = catalogue_df.copy().reset_index(drop=True)
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            token_pattern=r"(?u)\b\w+\b"
        )
        self.corpus: List[str] = []
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        """Constructs rich searchable text representation and fits TF-IDF once."""
        corpus = []
        for _, row in self.df.iterrows():
            parts = [
                str(row.get("category", "")),
                str(row.get("garment_type", "")),
                str(row.get("outfit_name", "")),
                str(row.get("description", "")),
                f"colour {row.get('dominant_colour', '')}",
                f"occasion {row.get('occasion', '')}",
                f"style {row.get('style', '')}",
                f"season {row.get('season', '')}",
                f"skin {row.get('suitable_skin_tones', '')}",
                f"undertone {row.get('suitable_undertones', '')}",
                f"body {row.get('compatible_body_shapes', '')}",
            ]
            corpus.append(" ".join(parts).lower())

        self.corpus = corpus
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def build_query_string(
        self,
        user_query_text: Optional[str] = None,
        preferred_styles: Optional[str] = None,
        preferred_colours: Optional[str] = None,
        preferred_occasions: Optional[str] = None,
        preferred_categories: Optional[str] = None,
        skin_tone: Optional[str] = None,
        undertone: Optional[str] = None,
        body_shape: Optional[str] = None,
    ) -> str:
        """Constructs a normalized search query from free text and profile preferences."""
        terms = []
        if user_query_text:
            terms.append(str(user_query_text).strip())
        if preferred_styles:
            terms.append(f"style {preferred_styles}")
        if preferred_colours:
            terms.append(f"colour {preferred_colours}")
        if preferred_occasions:
            terms.append(f"occasion {preferred_occasions}")
        if preferred_categories:
            terms.append(str(preferred_categories))
        if skin_tone and skin_tone != "Unknown":
            terms.append(f"skin {skin_tone}")
        if undertone and undertone != "Unknown":
            terms.append(f"undertone {undertone}")
        if body_shape and body_shape != "Unknown":
            terms.append(f"body {body_shape}")

        if not terms:
            terms.append("stylish casual formal comfortable classic")

        return " ".join(terms).lower()

    def compute_similarity(self, query_string: str) -> np.ndarray:
        """Computes cosine similarity between query and catalogue items.

        Returns a 1D numpy array of similarity scores in [0, 1].
        """
        if not query_string or self.tfidf_matrix is None:
            return np.zeros(len(self.df), dtype=float)

        query_vec = self.vectorizer.transform([query_string])
        sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        # Ensure values bounded in [0, 1]
        sims = np.clip(sims, 0.0, 1.0)
        return sims

    def recommend(
        self,
        query_string: str,
        category_filter: Optional[str] = None,
        occasion_filter: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        top_k: int = 5,
    ) -> List[Dict]:
        """Ranks catalogue items by TF-IDF similarity subject to hard constraint filters."""
        sims = self.compute_similarity(query_string)
        results = []

        for idx, score in enumerate(sims):
            row = self.df.iloc[idx]

            # Hard filter: category
            if category_filter and category_filter != "All":
                if str(row["category"]).strip().lower() != category_filter.strip().lower():
                    continue

            # Hard filter: occasion
            if occasion_filter and occasion_filter != "All":
                if str(row["occasion"]).strip().lower() != occasion_filter.strip().lower():
                    continue

            # Hard filter: budget
            price = float(row.get("price", 0.0))
            if budget_min is not None and price < budget_min:
                continue
            if budget_max is not None and budget_max > 0 and price > budget_max:
                continue

            # Build reasons for recommendation
            reasons = []
            if score > 0.15:
                reasons.append(f"High keyword relevance to '{query_string[:30]}...'")
            reasons.append(f"Matches {row['style']} aesthetic for {row['occasion']} wear")
            if row.get("dominant_colour"):
                reasons.append(f"Complementary {row['dominant_colour']} palette")

            results.append({
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
                "tfidf_similarity_score": round(float(score), 4),
                "recommendation_reason": " • ".join(reasons),
            })

        results.sort(key=lambda x: x["tfidf_similarity_score"], reverse=True)
        return results[:top_k]
