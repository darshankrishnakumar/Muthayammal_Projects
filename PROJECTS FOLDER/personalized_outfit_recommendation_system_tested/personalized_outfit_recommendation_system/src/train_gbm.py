"""Stage 4: Gradient Boosting Classifier Pipeline for Clothing Category Preference Prediction."""

import os
import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

import config

FEATURE_COLUMNS = [
    "body_shape",
    "skin_tone",
    "undertone",
    "preferred_style",
    "preferred_occasion",
    "preferred_colour",
    "budget_max",
]

CATEGORICAL_FEATURES = [
    "body_shape",
    "skin_tone",
    "undertone",
    "preferred_style",
    "preferred_occasion",
    "preferred_colour",
]

NUMERICAL_FEATURES = ["budget_max"]

TARGET_COLUMN = "preferred_clothing_category"


def build_pipeline() -> Tuple[ColumnTransformer, GradientBoostingClassifier]:
    """Constructs the ColumnTransformer and GradientBoostingClassifier."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ("num", "passthrough", NUMERICAL_FEATURES),
        ]
    )
    clf = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        random_state=42,
    )
    return preprocessor, clf


def train_gbm_model(
    csv_path: str = config.TRAINING_DATA_PATH,
    model_save_path: str = config.GBM_MODEL_PATH,
    eval_save_path: str = config.EVAL_METRICS_PATH,
) -> Dict[str, Any]:
    """Trains Gradient Boosting model using leakage-safe pipeline on 80/20 stratified split."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Training dataset not found at: {csv_path}")

    df = pd.read_csv(csv_path)

    # Validate non-emptiness
    if len(df) < 50:
        raise ValueError("Insufficient training samples for reliable cross-validation.")

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    # Stratified 80/20 split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    preprocessor, clf = build_pipeline()

    # Fit preprocessor only on train set
    X_train_trans = preprocessor.fit_transform(X_train)
    clf.fit(X_train_trans, y_train)

    # Evaluate on held-out test split
    X_test_trans = preprocessor.transform(X_test)
    y_pred = clf.predict(X_test_trans)

    acc = float(accuracy_score(y_test, y_pred))
    macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    conf_mat = confusion_matrix(y_test, y_pred).tolist()
    labels = sorted(list(set(y_test)))

    # Persist fitted pipeline
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    full_pipeline = {
        "preprocessor": preprocessor,
        "classifier": clf,
        "classes": clf.classes_.tolist(),
        "trained_on": "synthetic_demonstration_records",
        "random_state": 42,
    }
    joblib.dump(full_pipeline, model_save_path)

    # Persist evaluation metrics
    os.makedirs(os.path.dirname(eval_save_path), exist_ok=True)
    eval_metrics = {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "classes": labels,
        "confusion_matrix": conf_mat,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "classification_report": report,
        "data_provenance": "Synthetic academic demonstration data. Model illustrates predictive workflow.",
    }

    with open(eval_save_path, "w") as f:
        json.dump(eval_metrics, f, indent=2)

    return eval_metrics


def predict_category(
    features: Dict[str, Any], model_path: str = config.GBM_MODEL_PATH
) -> Tuple[str, float]:
    """Performs inference using saved pipeline. Returns (predicted_category, confidence)."""
    if not os.path.exists(model_path):
        return "All", 0.0

    pipeline = joblib.load(model_path)
    preprocessor = pipeline["preprocessor"]
    clf = pipeline["classifier"]

    input_df = pd.DataFrame([{
        "body_shape": str(features.get("body_shape", "Rectangle / Hourglass")),
        "skin_tone": str(features.get("skin_tone", "Medium")),
        "undertone": str(features.get("undertone", "Warm")),
        "preferred_style": str(features.get("preferred_style", "Classic")),
        "preferred_occasion": str(features.get("preferred_occasion", "Casual")),
        "preferred_colour": str(features.get("preferred_colour", "Blue")),
        "budget_max": float(features.get("budget_max", 5000.0)),
    }])

    trans = preprocessor.transform(input_df)
    probs = clf.predict_proba(trans)[0]
    top_idx = int(np.argmax(probs))
    pred_class = clf.classes_[top_idx]
    confidence = float(probs[top_idx])

    return pred_class, confidence
