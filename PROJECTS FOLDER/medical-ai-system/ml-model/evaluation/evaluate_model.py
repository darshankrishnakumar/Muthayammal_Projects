"""
Evaluation Module for 1D CNN Arrhythmia Classification.

Computes:
- Per-class and Macro Precision
- Per-class and Macro Recall (Sensitivity)
- Per-class Specificity: TN / (TN + FP)
- Macro-F1 Score
- Confusion Matrix (normalized & counts)
- Saves confusion_matrix.png and evaluation_metrics.json
"""

import os
import sys
import json
import numpy as np
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    confusion_matrix,
    classification_report
)

# Add root directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

from preprocessing.ecg_pipeline import AAMI_CLASSES, AAMI_CODES


def compute_specificity(y_true, y_pred, num_classes=5):
    """
    Compute per-class specificity = True Negatives / (True Negatives + False Positives).
    """
    cm = confusion_matrix(y_true, y_pred, labels=list(range(num_classes)))
    specificities = {}
    for i in range(num_classes):
        # All elements not in row i and column i are TN
        tn = np.sum(np.delete(np.delete(cm, i, axis=0), i, axis=1))
        # FP is column i without row i
        fp = np.sum(cm[:, i]) - cm[i, i]
        denom = tn + fp
        spec = float(tn / denom) if denom > 0 else 0.0
        specificities[i] = spec
    return specificities, cm


def evaluate_predictions(y_true, y_pred, y_pred_probs, output_dir):
    """
    Compute complete clinical evaluation metrics and save results to output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    num_classes = len(AAMI_CLASSES)

    accuracy = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    macro_precision = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    macro_recall = float(recall_score(y_true, y_pred, average="macro", zero_division=0))

    per_class_precision = precision_score(y_true, y_pred, average=None, labels=list(range(num_classes)), zero_division=0)
    per_class_recall = recall_score(y_true, y_pred, average=None, labels=list(range(num_classes)), zero_division=0)
    per_class_f1 = f1_score(y_true, y_pred, average=None, labels=list(range(num_classes)), zero_division=0)
    specificities, cm = compute_specificity(y_true, y_pred, num_classes=num_classes)

    class_metrics = {}
    for i in range(num_classes):
        code = AAMI_CODES[i]
        name = AAMI_CLASSES[i]
        support = int(np.sum(y_true == i))
        class_metrics[code] = {
            "name": name,
            "support": support,
            "precision": round(float(per_class_precision[i]), 4),
            "recall_sensitivity": round(float(per_class_recall[i]), 4),
            "specificity": round(float(specificities[i]), 4),
            "f1_score": round(float(per_class_f1[i]), 4)
        }

    macro_specificity = float(np.mean(list(specificities.values())))

    metrics_summary = {
        "overall_accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "macro_precision": round(macro_precision, 4),
        "macro_recall_sensitivity": round(macro_recall, 4),
        "macro_specificity": round(macro_specificity, 4),
        "total_test_samples": int(len(y_true)),
        "per_class_metrics": class_metrics,
        "confusion_matrix": cm.tolist()
    }

    # Print clinical metrics table
    print("\n" + "=" * 80)
    print("CLINICAL EVALUATION METRICS (Independent Patient Test Set)")
    print("=" * 80)
    print(f"Overall Accuracy:  {accuracy * 100:.2f}%")
    print(f"Macro-F1 Score:    {macro_f1:.4f}")
    print(f"Macro Precision:   {macro_precision:.4f}")
    print(f"Macro Recall/Sens: {macro_recall:.4f}")
    print(f"Macro Specificity: {macro_specificity:.4f}")
    print("-" * 80)
    print(f"{'Class':<6} | {'Name':<30} | {'Support':<8} | {'Prec':<7} | {'Recall':<7} | {'Spec':<7} | {'F1'}")
    print("-" * 80)
    for i in range(num_classes):
        code = AAMI_CODES[i]
        m = class_metrics[code]
        print(f"{code:<6} | {m['name']:<30} | {m['support']:<8} | {m['precision']:<7.4f} | {m['recall_sensitivity']:<7.4f} | {m['specificity']:<7.4f} | {m['f1_score']:.4f}")
    print("=" * 80)

    # Save metrics JSON
    json_path = os.path.join(output_dir, "evaluation_metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)
    print(f"[OK] Evaluation metrics saved to: {json_path}")

    # Plot & save confusion matrix
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.figure(figsize=(8, 6))
        labels = [AAMI_CODES[i] for i in range(num_classes)]
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=labels,
            yticklabels=labels,
            cbar=True
        )
        plt.title("1D CNN Arrhythmia Classification — Test Confusion Matrix")
        plt.xlabel("Predicted Class")
        plt.ylabel("True Class (PhysioNet Annotations)")
        plt.tight_layout()

        plot_path = os.path.join(output_dir, "confusion_matrix.png")
        plt.savefig(plot_path, dpi=200)
        plt.close()
        print(f"[OK] Confusion matrix plot saved to: {plot_path}")
    except Exception as e:
        print(f"Notice: Confusion matrix plot skipped: {e}")

    return metrics_summary
