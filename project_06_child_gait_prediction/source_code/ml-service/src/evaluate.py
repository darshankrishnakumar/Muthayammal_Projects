"""
Model evaluation module for Child Gait Prediction.
Calculates real metrics on held-out test data without fabrication.
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
)


def evaluate_classifier(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    target_names: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Evaluates a trained classifier on held-out test data.
    Computes strict metrics without artificial inflation.
    """
    y_pred = model.predict(X_test)

    # Core multiclass metrics
    acc = float(accuracy_score(y_test, y_pred))
    prec_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
    prec_weighted = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    rec_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
    rec_weighted = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1_macro = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(
        y_test,
        y_pred,
        target_names=target_names,
        zero_division=0,
        output_dict=True,
    )
    report_text = classification_report(
        y_test,
        y_pred,
        target_names=target_names,
        zero_division=0,
    )

    # Multiclass ROC-AUC (One-vs-Rest) if probabilities are accessible
    roc_auc = None
    if hasattr(model, "predict_proba"):
        try:
            y_proba = model.predict_proba(X_test)
            # Only compute if test set contains multiple classes
            if len(np.unique(y_test)) > 1:
                roc_auc = float(
                    roc_auc_score(
                        y_test,
                        y_proba,
                        multi_class="ovr",
                        average="macro",
                    )
                )
        except Exception as e:
            print(f"[Notice] ROC-AUC calculation skipped: {e}")

    results = {
        "accuracy": acc,
        "precision_macro": prec_macro,
        "precision_weighted": prec_weighted,
        "recall_macro": rec_macro,
        "recall_weighted": rec_weighted,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "roc_auc_ovr_macro": roc_auc,
        "confusion_matrix": cm,
        "classification_report_dict": report,
        "classification_report_text": report_text,
    }

    return results


def print_evaluation_summary(results: Dict[str, Any]):
    print("=" * 60)
    print("HELD-OUT TEST SET EVALUATION RESULTS")
    print("=" * 60)
    print(f"Accuracy:           {results['accuracy']:.4f} ({results['accuracy'] * 100:.2f}%)")
    print(f"Precision (Macro):  {results['precision_macro']:.4f}")
    print(f"Recall (Macro):     {results['recall_macro']:.4f}")
    print(f"F1-Score (Macro):   {results['f1_macro']:.4f}")
    print(f"F1-Score (Weight):  {results['f1_weighted']:.4f}")
    if results.get("roc_auc_ovr_macro") is not None:
        print(f"ROC-AUC (OvR Macro): {results['roc_auc_ovr_macro']:.4f}")
    print("\nConfusion Matrix:")
    for row in results["confusion_matrix"]:
        print(f"  {row}")
    print("\nDetailed Classification Report:")
    print(results["classification_report_text"])
    print("=" * 60)
