"""
Training script for Child Gait Prediction.
Phase 1 Baseline: RandomForestClassifier(n_estimators=100, random_state=42).
Adheres strictly to zero-leakage and reproducibility requirements.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Optional
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Ensure src modules are resolvable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessing import inspect_dataset, GaitDataPreprocessor, INTENDED_FEATURES
from src.evaluate import evaluate_classifier, print_evaluation_summary

DEFAULT_DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "dataset.csv"
)
DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "gait_random_forest.joblib"
)
DEFAULT_METRICS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "experiment_log.json"
)


def train_baseline_model(
    dataset_path: str = DEFAULT_DATASET_PATH,
    model_output_path: str = DEFAULT_MODEL_PATH,
    target_column: Optional[str] = None,
    random_seed: int = 42,
):
    """
    Executes the training and evaluation pipeline on a provided real dataset.
    """
    if not os.path.exists(dataset_path):
        print(f"[STOP] Dataset not found at: {dataset_path}")
        print("A real dataset is required before training can begin.")
        print(f"Please place your dataset file at: {dataset_path}")
        return False

    print(f"\n[1/5] Inspecting Dataset: {dataset_path}")
    report = inspect_dataset(dataset_path, target_col=target_column)
    report.print_summary()

    if not report.is_suitable:
        print("\n[STOP] The dataset is currently unsuitable for training.")
        print(f"Reason: {report.suitability_summary}")
        print("Please review and resolve dataset discrepancies before training.")
        return False

    df = pd.read_csv(dataset_path)

    # Use resolved target and features
    actual_target = report.candidate_target_column
    feature_cols = report.available_required_features

    print(f"\n[2/5] Preparing Features & Target")
    print(f"Target:   {actual_target}")
    print(f"Features: {feature_cols}")

    X = df[feature_cols]
    y = df[actual_target]

    # Check stratification feasibility
    stratify = y if y.value_counts().min() >= 3 else None

    # Step 1: Split into Train (70%) and Temp (30%)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=random_seed, stratify=stratify
    )

    # Step 2: Split Temp into Validation (15%) and Held-out Test (15%)
    temp_stratify = y_temp if (stratify is not None and y_temp.value_counts().min() >= 2) else None
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=random_seed, stratify=temp_stratify
    )

    print(f"Data Splits: Train={len(X_train)} | Val={len(X_val)} | Test={len(X_test)}")

    # Step 3: Leakage-free preprocessing (Fit on train only)
    print("\n[3/5] Fitting Preprocessor on Training Split")
    preprocessor = GaitDataPreprocessor(feature_names=feature_cols)
    preprocessor.fit(X_train, y_train)

    X_train_proc = preprocessor.transform_features(X_train)
    y_train_proc = preprocessor.transform_labels(y_train)

    X_val_proc = preprocessor.transform_features(X_val)
    y_val_proc = preprocessor.transform_labels(y_val)

    X_test_proc = preprocessor.transform_features(X_test)
    y_test_proc = preprocessor.transform_labels(y_test)

    # Step 4: Baseline Model Training (Random Forest)
    print("\n[4/5] Training Random Forest Baseline Classifier")
    start_time = time.time()
    rf = RandomForestClassifier(
        n_estimators=100,
        random_state=random_seed,
    )
    rf.fit(X_train_proc, y_train_proc)
    train_duration = time.time() - start_time
    print(f"Training completed in {train_duration:.3f} seconds.")

    # Validation check
    val_acc = rf.score(X_val_proc, y_val_proc)
    print(f"Validation Set Accuracy: {val_acc:.4f} ({val_acc * 100:.2f}%)")

    # Step 5: Test Set Evaluation
    print("\n[5/5] Evaluating on Final Held-Out Test Set")
    class_names = [str(c) for c in preprocessor.label_encoder.classes_]
    test_results = evaluate_classifier(
        rf, X_test_proc, y_test_proc, target_names=class_names
    )
    print_evaluation_summary(test_results)

    # Save artifact bundle
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    bundle = {
        "model": rf,
        "preprocessor": preprocessor,
        "feature_names": feature_cols,
        "class_labels": class_names,
        "algorithm": "RandomForestClassifier",
        "n_estimators": 100,
        "random_seed": random_seed,
        "trained_at": datetime.now().isoformat(),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "test_accuracy": test_results["accuracy"],
    }
    joblib.dump(bundle, model_output_path)
    print(f"\nTrained model bundle successfully saved to: {model_output_path}")

    # Save experiment log for reproducibility
    experiment_log = {
        "timestamp": datetime.now().isoformat(),
        "dataset_file": os.path.basename(dataset_path),
        "dataset_rows": len(df),
        "features_used": feature_cols,
        "target_column": actual_target,
        "classes": class_names,
        "splits": {
            "train": len(X_train),
            "val": len(X_val),
            "test": len(X_test),
        },
        "random_seed": random_seed,
        "hyperparameters": {"n_estimators": 100, "random_state": random_seed},
        "training_time_seconds": round(train_duration, 4),
        "evaluation_metrics": {
            "accuracy": test_results["accuracy"],
            "precision_macro": test_results["precision_macro"],
            "recall_macro": test_results["recall_macro"],
            "f1_macro": test_results["f1_macro"],
            "roc_auc_ovr_macro": test_results.get("roc_auc_ovr_macro"),
            "confusion_matrix": test_results["confusion_matrix"],
        },
    }

    with open(DEFAULT_METRICS_PATH, "w") as f:
        json.dump(experiment_log, f, indent=2)
    print(f"Experiment log saved to: {DEFAULT_METRICS_PATH}")

    return True


if __name__ == "__main__":
    data_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATASET_PATH
    train_baseline_model(dataset_path=data_file)
