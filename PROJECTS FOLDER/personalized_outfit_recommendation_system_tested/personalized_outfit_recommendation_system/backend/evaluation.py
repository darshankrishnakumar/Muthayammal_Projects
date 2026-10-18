"""Model Evaluation Utilities for Gradient Boosting."""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report


def evaluate_classifier(y_true, y_pred, classes: List[str]) -> Dict[str, Any]:
    """Computes comprehensive evaluation metrics on held-out test data."""
    acc = float(accuracy_score(y_true, y_pred))
    
    # Macro and Weighted metrics
    p_w, r_w, f1_w, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )
    p_m, r_m, f1_m, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    
    # Per-class report dictionary
    report = classification_report(
        y_true, y_pred, labels=classes, output_dict=True, zero_division=0
    )

    return {
        "accuracy": round(acc, 4),
        "precision_weighted": round(float(p_w), 4),
        "recall_weighted": round(float(r_w), 4),
        "f1_weighted": round(float(f1_w), 4),
        "precision_macro": round(float(p_m), 4),
        "recall_macro": round(float(r_m), 4),
        "f1_macro": round(float(f1_m), 4),
        "confusion_matrix": cm.tolist(),
        "classes": list(classes),
        "classification_report": report,
        "sample_count": len(y_true),
    }
