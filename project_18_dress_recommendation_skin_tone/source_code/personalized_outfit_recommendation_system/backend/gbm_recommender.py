"""Gradient Boosting Classifier for Predicting Preferred Clothing Category.

Uses scikit-learn Pipeline with ColumnTransformer for leakage-safe
preprocessing and GradientBoostingClassifier.
"""

import json
import os
from typing import Dict, Any, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import config
from backend.evaluation import evaluate_classifier

FEATURE_CATEGORICAL = [
    "body_shape",
    "skin_tone",
    "undertone",
    "preferred_style",
    "preferred_occasion",
    "preferred_colour",
]
FEATURE_NUMERIC = ["budget_max"]
ALL_FEATURES = FEATURE_CATEGORICAL + FEATURE_NUMERIC
TARGET_COLUMN = "preferred_clothing_category"


def validate_input_features(features_dict: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validates that required features are present and formatted correctly."""
    if not isinstance(features_dict, dict):
        return False, "Features must be provided as a dictionary."

    for feat in ALL_FEATURES:
        if feat not in features_dict:
            return False, f"Missing required feature: '{feat}'"

    try:
        val = float(features_dict["budget_max"])
        if val < 0:
            return False, "budget_max must be non-negative."
    except (ValueError, TypeError):
        return False, "budget_max must be a numeric value."

    return True, None


def train_model(
    dataset_path: str = config.TRAINING_DATA_PATH,
    save_path: str = config.MODEL_SAVE_PATH,
    eval_save_path: str = config.EVAL_METRICS_PATH,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Trains GradientBoostingClassifier using leakage-safe Pipeline and evaluates on held-out test data."""
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Training dataset not found at: {dataset_path}")

    df = pd.read_csv(dataset_path)

    # Validate columns
    missing_cols = [c for c in ALL_FEATURES + [TARGET_COLUMN] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing required columns: {missing_cols}")

    # Drop any nulls
    df = df.dropna(subset=ALL_FEATURES + [TARGET_COLUMN]).reset_index(drop=True)

    X = df[ALL_FEATURES]
    y = df[TARGET_COLUMN]

    classes = np.unique(y)
    if len(classes) < 2:
        raise ValueError("Dataset requires at least 2 target classes to train.")

    # Stratified 80/20 train-test split
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=random_state, stratify=y
        )
    except ValueError:
        # Fallback to non-stratified if rare class count is too low
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=random_state
        )

    # Build leakage-safe pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), FEATURE_CATEGORICAL),
            ("num", StandardScaler(), FEATURE_NUMERIC),
        ]
    )

    clf = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        random_state=random_state,
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", clf),
    ])

    # Fit pipeline strictly on training data
    pipeline.fit(X_train, y_train)

    # Evaluate on held-out test split
    y_pred = pipeline.predict(X_test)
    eval_results = evaluate_classifier(y_test, y_pred, classes=pipeline.classes_)
    eval_results["train_samples"] = len(X_train)
    eval_results["test_samples"] = len(X_test)
    eval_results["total_samples"] = len(df)
    eval_results["dataset_path"] = dataset_path

    # Save model pipeline
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(pipeline, save_path)

    # Save evaluation metrics
    os.makedirs(os.path.dirname(eval_save_path), exist_ok=True)
    with open(eval_save_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    return eval_results


def load_model(model_path: str = config.MODEL_SAVE_PATH) -> Optional[Pipeline]:
    """Loads fitted Gradient Boosting pipeline from disk."""
    if not os.path.exists(model_path):
        return None
    try:
        pipeline = joblib.load(model_path)
        return pipeline
    except Exception as e:
        print(f"[WARNING] Failed to load GBM model from {model_path}: {e}")
        return None


def predict_preferred_category(
    features_dict: Dict[str, Any],
    model: Optional[Pipeline] = None,
) -> Tuple[Optional[str], Optional[float]]:
    """Predicts the preferred clothing category from input profile features.

    Returns:
        (predicted_category, confidence_score) or (None, None)
    """
    valid, err = validate_input_features(features_dict)
    if not valid:
        return None, None

    if model is None:
        model = load_model()

    if model is None:
        return None, None

    # Construct single-row DataFrame
    input_df = pd.DataFrame([{
        feat: features_dict[feat] for feat in ALL_FEATURES
    }])

    try:
        pred = model.predict(input_df)[0]
        # Calculate maximum class probability
        probs = model.predict_proba(input_df)[0]
        conf = float(np.max(probs))
        return str(pred), round(conf, 4)
    except Exception as e:
        print(f"[WARNING] Prediction error: {e}")
        return None, None


def return_prediction_results(
    features_dict: Dict[str, Any],
    model: Optional[Pipeline] = None,
) -> Dict[str, Any]:
    """Returns a full result dictionary including predictions, top probabilities, and disclaimers."""
    valid, err = validate_input_features(features_dict)
    if not valid:
        return {"success": False, "error": err}

    if model is None:
        model = load_model()

    if model is None:
        return {
            "success": False,
            "error": "Model not trained yet. Run train_model() first.",
        }

    input_df = pd.DataFrame([{
        feat: features_dict[feat] for feat in ALL_FEATURES
    }])

    pred = model.predict(input_df)[0]
    probs = model.predict_proba(input_df)[0]
    classes = model.classes_

    # Sort probabilities
    prob_list = [
        {"category": cls, "probability": round(float(p), 4)}
        for cls, p in zip(classes, probs)
    ]
    prob_list.sort(key=lambda x: x["probability"], reverse=True)

    return {
        "success": True,
        "predicted_category": str(pred),
        "confidence": prob_list[0]["probability"],
        "top_predictions": prob_list[:3],
        "disclaimer": (
            "The predicted category reflects stylistic preference tendencies "
            "learned from profile attributes, not an absolute guarantee of fit."
        ),
    }


def report_evaluation_metrics(eval_path: str = config.EVAL_METRICS_PATH) -> Optional[Dict[str, Any]]:
    """Reads saved offline evaluation metrics."""
    if not os.path.exists(eval_path):
        return None
    try:
        with open(eval_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None
