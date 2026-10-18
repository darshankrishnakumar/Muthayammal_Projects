"""Stage 5: TF-IDF Search Engine for Lexical Clothing Search and Ranking."""

import os
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import scipy.sparse as sp

import config

TEXT_FIELDS = [
    "item_name",
    "description",
    "category",
    "subcategory",
    "primary_color",
    "secondary_color",
    "occasion",
    "style_tags",
    "fabric",
    "pattern",
    "fit",
    "season",
    "body_shape_tags",
    "undertone_color_tags",
]


class TFIDFSearchEngine:
    """TF-IDF Lexical Feature Matcher with n-gram support and constraint filtering."""

    def __init__(
        self,
        catalogue_path: str = config.CATALOGUE_PATH,
        vectorizer_path: str = config.TFIDF_VECTORIZER_PATH,
        matrix_path: str = config.TFIDF_MATRIX_PATH,
    ):
        self.catalogue_path = catalogue_path
        self.vectorizer_path = vectorizer_path
        self.matrix_path = matrix_path
        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self._load_or_fit()

    def _build_document_corpus(self, df: pd.DataFrame) -> List[str]:
        corpus = []
        for _, row in df.iterrows():
            parts = [str(row[f]) for f in TEXT_FIELDS if f in row and pd.notna(row[f])]
            doc = " ".join(parts).lower()
            corpus.append(doc)
        return corpus

    def _load_or_fit(self):
        if not os.path.exists(self.catalogue_path):
            return

        self.df = pd.read_csv(self.catalogue_path)

        if os.path.exists(self.vectorizer_path) and os.path.exists(self.matrix_path):
            self.vectorizer = joblib.load(self.vectorizer_path)
            self.tfidf_matrix = sp.load_npz(self.matrix_path)
        else:
            self.fit_and_save()

    def fit_and_save(self):
        """Fits TfidfVectorizer on catalogue and saves vectorizer and sparse matrix."""
        if self.df is None or len(self.df) == 0:
            if os.path.exists(self.catalogue_path):
                self.df = pd.read_csv(self.catalogue_path)
            else:
                return

        corpus = self._build_document_corpus(self.df)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=5000,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

        os.makedirs(os.path.dirname(self.vectorizer_path), exist_ok=True)
        joblib.dump(self.vectorizer, self.vectorizer_path)
        sp.save_npz(self.matrix_path, self.tfidf_matrix)

    def search(
        self,
        query: str,
        category: str = None,
        max_budget: float = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """Searches catalog using TF-IDF cosine similarity with mandatory constraint filtering."""
        if self.vectorizer is None or self.tfidf_matrix is None:
            self._load_or_fit()

        if self.df is None or len(self.df) == 0:
            return []

        if not query or query.strip() == "":
            query = "comfortable stylish outfit"

        # 1. Transform query
        query_vec = self.vectorizer.transform([query.lower()])

        # 2. Compute cosine similarities
        raw_sims = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        # 3. Apply hard filters (Budget, Category)
        candidates = []
        for idx, score in enumerate(raw_sims):
            row = self.df.iloc[idx]

            # Mandatory category filter
            if category and category != "All":
                if str(row["category"]).strip().lower() != category.strip().lower():
                    continue

            # Mandatory budget filter
            if max_budget and max_budget > 0:
                if float(row["price"]) > max_budget:
                    continue

            candidates.append({
                "item_id": row["item_id"],
                "item_name": row["item_name"],
                "category": row["category"],
                "price": float(row["price"]),
                "primary_color": row["primary_color"],
                "occasion": row["occasion"],
                "image_path": row["image_path"],
                "tfidf_score": float(score),
            })

        # Sort by similarity
        candidates.sort(key=lambda x: x["tfidf_score"], reverse=True)
        return candidates[:top_k]
