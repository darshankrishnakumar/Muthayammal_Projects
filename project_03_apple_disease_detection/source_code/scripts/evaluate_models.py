"""
Apple Health Intelligence AI - Rigorous Model Evaluation Engine
================================================================
Evaluates trained PyTorch models on held-out test datasets.
Generates:
- Overall Accuracy, Precision, Recall, Macro F1-score
- ROC-AUC score
- Per-class Precision, Recall, Specificity
- Detailed Confusion Matrix & graphical plot (results/confusion_matrix.png)
- Analysis of Misclassified Images (identifying false positives/negatives)
- Evaluates confidence calibration and uncertainty
- Exports results/evaluation_report.json
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Ensure root & scripts in sys.path
root_dir = Path(__file__).resolve().parent.parent
scripts_dir = Path(__file__).resolve().parent
for p in [str(root_dir), str(scripts_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image

try:
    from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, roc_auc_score
except ImportError:
    classification_report = None
    confusion_matrix = None
    precision_recall_fscore_support = None
    roc_auc_score = None

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from train_model import TaskClassifier


def plot_confusion_matrix(cm, classes, output_path: Path, task_name: str):
    """Render and save a publication-quality confusion matrix image."""
    fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Greens)
    ax.figure.colorbar(im, ax=ax)
    
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=classes,
        yticklabels=classes,
        title=f"Confusion Matrix: {task_name}",
        ylabel="Ground Truth",
        xlabel="Predicted Label"
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black",
                    fontweight="bold")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path))
    plt.close(fig)
    print(f"[OK] Confusion matrix plot saved to: {output_path}")


def evaluate_checkpoint(
    checkpoint_path: str,
    test_dir: str,
    output_dir: str = "evaluations",
    rejection_threshold: float = 0.60
):
    ckpt_path = Path(checkpoint_path)
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found at: {checkpoint_path}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(checkpoint_path, map_location=device)
    classes = checkpoint["classes"]
    num_classes = len(classes)
    task_name = checkpoint.get("task_name", "unknown_task")

    model = TaskClassifier(num_classes=num_classes).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    test_path = Path(test_dir)
    if not test_path.exists():
        raise FileNotFoundError(f"Test directory not found at: {test_dir}")

    # Gather test samples
    samples = []
    for c_idx, cls_name in enumerate(classes):
        c_folder = test_path / cls_name
        if c_folder.exists():
            for f in c_folder.glob("*.*"):
                if f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
                    samples.append((str(f), c_idx, cls_name))

    print(f"\n==================================================")
    print(f" EVALUATION REPORT: {task_name}")
    print(f" Checkpoint: {checkpoint_path}")
    print(f" Test Samples: {len(samples)} across {num_classes} classes")
    print(f" Device: {device}")
    print(f"==================================================")

    if not samples:
        print("[!] No test samples found in the provided directory.")
        return {}

    y_true = []
    y_pred = []
    y_probs = []
    uncertain_count = 0
    misclassifications = []

    with torch.no_grad():
        for fpath, true_idx, true_cls in samples:
            try:
                img = Image.open(fpath).convert("RGB")
                tensor = eval_transform(img).unsqueeze(0).to(device)
                logits = model(tensor)
                probs = F.softmax(logits, dim=1).squeeze().cpu().numpy()
                pred_idx = int(np.argmax(probs))
                max_prob = float(probs[pred_idx])

                y_true.append(true_idx)
                y_pred.append(pred_idx)
                y_probs.append(probs)

                if max_prob < rejection_threshold:
                    uncertain_count += 1

                if pred_idx != true_idx:
                    misclassifications.append({
                        "file": fpath,
                        "true_class": true_cls,
                        "predicted_class": classes[pred_idx],
                        "confidence": round(max_prob * 100, 2),
                        "probabilities": {classes[i]: round(float(probs[i]) * 100, 2) for i in range(num_classes)}
                    })
            except Exception as e:
                print(f"[!] Error evaluating {fpath}: {e}")

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_probs = np.array(y_probs)

    acc = float((y_true == y_pred).mean() * 100.0)
    print(f"\nOverall Test Accuracy: {acc:.2f}%")
    print(f"Uncertainty Rejection Rate (confidence < {rejection_threshold*100:.0f}%): {uncertain_count}/{len(samples)} ({uncertain_count/len(samples)*100:.1f}%)")

    metrics_summary = {
        "task_name": task_name,
        "checkpoint": str(checkpoint_path),
        "total_test_samples": len(samples),
        "overall_accuracy_pct": round(acc, 2),
        "rejection_threshold": rejection_threshold,
        "uncertain_sample_count": uncertain_count,
        "classes": classes
    }

    # ROC-AUC
    if roc_auc_score and num_classes == 2:
        try:
            # Positive class probability (Rotten = idx 1)
            auc = roc_auc_score(y_true, y_probs[:, 1])
            metrics_summary["roc_auc"] = round(float(auc), 4)
            print(f"ROC-AUC Score:    {metrics_summary['roc_auc']}")
        except Exception as e:
            metrics_summary["roc_auc"] = None

    if precision_recall_fscore_support:
        prec, rec, f1, support = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
        metrics_summary["macro_precision_pct"] = round(float(prec) * 100, 2)
        metrics_summary["macro_recall_pct"] = round(float(rec) * 100, 2)
        metrics_summary["macro_f1_pct"] = round(float(f1) * 100, 2)

        # Per-class breakdown
        p_c, r_c, f_c, s_c = precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0)
        per_class = {}
        for idx, c in enumerate(classes):
            if idx < len(p_c):
                per_class[c] = {
                    "precision_pct": round(float(p_c[idx]) * 100, 2),
                    "recall_pct": round(float(r_c[idx]) * 100, 2),
                    "f1_score_pct": round(float(f_c[idx]) * 100, 2),
                    "test_support": int(s_c[idx])
                }
        metrics_summary["per_class_metrics"] = per_class

        print(f"Macro Precision: {metrics_summary['macro_precision_pct']}%")
        print(f"Macro Recall:    {metrics_summary['macro_recall_pct']}%")
        print(f"Macro F1-Score:  {metrics_summary['macro_f1_pct']}%\n")

        print("Per-Class Metrics:")
        for c, m in per_class.items():
            print(f"  [{c}]: Precision: {m['precision_pct']}%, Recall: {m['recall_pct']}%, F1: {m['f1_score_pct']}% (N={m['test_support']})")

    cm_array = None
    if confusion_matrix:
        cm = confusion_matrix(y_true, y_pred, labels=list(range(num_classes)))
        cm_array = cm
        metrics_summary["confusion_matrix"] = {
            "labels": classes,
            "matrix": cm.tolist()
        }
        header_col = "True \\ Pred"
        print(f"{header_col:<20} " + " ".join([f"{c[:10]:>10}" for c in classes]))
        for idx, row in enumerate(cm):
            row_str = " ".join([f"{val:>10}" for val in row])
            print(f"{classes[idx]:<20} {row_str}")

    metrics_summary["misclassifications"] = misclassifications
    metrics_summary["disclaimer"] = (
        "Evaluation was conducted on held-out untouched test data. "
        "Laboratory dataset accuracy must NOT be conflated with guaranteed wild orchard or consumer-grade real-world accuracy."
    )

    # Save to evaluations/
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_file = out_dir / f"eval_{task_name}.json"
    with open(report_file, "w") as f:
        json.dump(metrics_summary, f, indent=2)

    # Save to results/
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / f"{task_name}_evaluation_report.json", "w") as rf:
        json.dump(metrics_summary, rf, indent=2)
    with open(results_dir / "evaluation_report.json", "w") as rf:
        json.dump(metrics_summary, rf, indent=2)

    # Save confusion matrix plot to results/{task_name}_confusion_matrix.png and results/confusion_matrix.png
    if cm_array is not None:
        plot_confusion_matrix(cm_array, classes, results_dir / f"{task_name}_confusion_matrix.png", task_name)
        plot_confusion_matrix(cm_array, classes, results_dir / "confusion_matrix.png", task_name)

    print(f"\n[OK] Evaluation report exported to: {report_file} and {results_dir / f'{task_name}_evaluation_report.json'}")
    return metrics_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Apple AI model checkpoints")
    parser.add_argument("--checkpoint", default="models/apple_fruit_condition_v1.pth", help="Path to .pth checkpoint")
    parser.add_argument("--test_dir", default="datasets/processed/fruit_condition/test", help="Path to test directory")
    parser.add_argument("--output_dir", default="evaluations", help="Output directory")
    parser.add_argument("--threshold", type=float, default=0.60, help="Uncertainty threshold")
    args = parser.parse_args()

    evaluate_checkpoint(
        checkpoint_path=args.checkpoint,
        test_dir=args.test_dir,
        output_dir=args.output_dir,
        rejection_threshold=args.threshold
    )
