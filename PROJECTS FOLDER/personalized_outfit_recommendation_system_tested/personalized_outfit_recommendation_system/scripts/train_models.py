"""Stage 4/5: Script to train GBM and build TF-IDF search indices."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.train_gbm import train_gbm_model
from src.text_recommender import TFIDFSearchEngine


def main():
    print("=" * 60)
    print("STAGE 4 & 5: MODEL TRAINING & INDEXING")
    print("=" * 60)

    # 1. Train Gradient Boosting Classifier
    print("[1/2] Training GradientBoostingClassifier on held-out stratified split...")
    metrics = train_gbm_model()
    print(f"      Accuracy on Test Split: {metrics['accuracy'] * 100:.2f}%")
    print(f"      Macro-F1 Score:         {metrics['macro_f1']:.4f}")
    print(f"      Saved Pipeline to:      {config.GBM_MODEL_PATH}")

    # 2. Build and save TF-IDF document matrix
    print("[2/2] Fitting and caching TF-IDF vectorizer and document matrix...")
    engine = TFIDFSearchEngine()
    engine.fit_and_save()
    print(f"      Saved Vectorizer to:    {config.TFIDF_VECTORIZER_PATH}")
    print(f"      Saved Matrix to:        {config.TFIDF_MATRIX_PATH}")
    print("=" * 60)
    print("Training and Indexing Complete!")


if __name__ == "__main__":
    main()
