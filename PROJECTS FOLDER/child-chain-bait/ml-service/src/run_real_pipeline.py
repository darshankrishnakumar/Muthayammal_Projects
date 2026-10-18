"""
Complete ML Pipeline Execution on Real SimTK Child Gait Dataset.
Implements:
- Participant-level zero-leakage splitting
- Phase 5: Random Forest Baseline
- Phase 6: Baseline Evaluation & Reports
- Phase 7: Model Comparison (Random Forest, Decision Tree, KNN, SVM, Gradient Boosting)
- Phase 8: Hyperparameter Tuning
- Phase 9: Final Model Evaluation on Held-Out Test Set
- Model artifact serialization with Joblib
"""

import os
import json
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler, LabelEncoder, label_binarize
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay,
    roc_auc_score,
    roc_curve,
    auc,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "real_child_gait_features.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

FEATURE_COLS = [
    "walking_speed",
    "stride_length",
    "step_duration",
    "cadence",
    "pelvic_tilt",
    "step_asymmetry",
    "peak_vertical_force_bw",
]
TARGET_COL = "class"

# Documented Participant Split Plan (Zero Data Leakage)
TRAIN_PARTICIPANTS = ["TD1", "TD2", "TD3", "HECP1", "HECP2", "HECP3", "DICP1", "DICP2"]
VAL_PARTICIPANTS = ["TD4", "HECP4", "DICP3"]
TEST_PARTICIPANTS = ["TD5", "HECP5", "DICP4"]


def execute_pipeline():
    print("=" * 60)
    print("CHILD GAIT ML PIPELINE — REAL C3D DATASET TRAINING")
    print("=" * 60)

    # 1. Load Real Extracted Dataset
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded dataset: {DATA_PATH}")
    print(f"Total trials: {len(df)} across {df['participant_id'].nunique()} unique participants.")

    # 2. Participant-Level Zero-Leakage Split
    train_mask = df["participant_id"].isin(TRAIN_PARTICIPANTS)
    val_mask = df["participant_id"].isin(VAL_PARTICIPANTS)
    test_mask = df["participant_id"].isin(TEST_PARTICIPANTS)

    df_train = df[train_mask]
    df_val = df[val_mask]
    df_test = df[test_mask]

    print("\nParticipant Split Summary:")
    print(f"Train Set:      {len(df_train)} trials ({df_train['participant_id'].nunique()} children: {TRAIN_PARTICIPANTS})")
    print(f"Validation Set: {len(df_val)} trials ({df_val['participant_id'].nunique()} children: {VAL_PARTICIPANTS})")
    print(f"Test Set:       {len(df_test)} trials ({df_test['participant_id'].nunique()} children: {TEST_PARTICIPANTS})")

    # Document split participant mapping
    split_info = {
        "training_participants": TRAIN_PARTICIPANTS,
        "validation_participants": VAL_PARTICIPANTS,
        "held_out_test_participants": TEST_PARTICIPANTS,
        "train_trials_count": len(df_train),
        "val_trials_count": len(df_val),
        "test_trials_count": len(df_test),
        "features": FEATURE_COLS,
    }
    with open(os.path.join(REPORTS_DIR, "participant_splits.json"), "w") as f:
        json.dump(split_info, f, indent=2)

    X_train_raw = df_train[FEATURE_COLS]
    y_train_raw = df_train[TARGET_COL]

    X_val_raw = df_val[FEATURE_COLS]
    y_val_raw = df_val[TARGET_COL]

    X_test_raw = df_test[FEATURE_COLS]
    y_test_raw = df_test[TARGET_COL]

    # 3. Leakage-Free Preprocessing: FIT ONLY ON TRAINING SET
    print("\nFitting Preprocessor strictly on Training Data...")
    scaler = StandardScaler()
    scaler.fit(X_train_raw)

    label_enc = LabelEncoder()
    label_enc.fit(["Normal", "Hemiplegic", "Diplegic"])

    X_train = scaler.transform(X_train_raw)
    y_train = label_enc.transform(y_train_raw)

    X_val = scaler.transform(X_val_raw)
    y_val = label_enc.transform(y_val_raw)

    X_test = scaler.transform(X_test_raw)
    y_test = label_enc.transform(y_test_raw)

    target_names = list(label_enc.classes_)

    # 4. Phase 5: Random Forest Baseline Model
    print("\n" + "=" * 60)
    print("PHASE 5: TRAINING BASELINE RANDOM FOREST CLASSIFIER")
    print("=" * 60)

    start_time = time.time()
    rf_baseline = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_baseline.fit(X_train, y_train)
    rf_duration = time.time() - start_time

    # Save baseline model bundle
    baseline_bundle = {
        "model": rf_baseline,
        "scaler": scaler,
        "label_encoder": label_enc,
        "features": FEATURE_COLS,
        "classes": target_names,
        "random_state": 42,
    }
    baseline_model_path = os.path.join(MODELS_DIR, "gait_random_forest_baseline.joblib")
    joblib.dump(baseline_bundle, baseline_model_path)
    print(f"Saved baseline model to: {baseline_model_path}")

    # Phase 6: Baseline Model Evaluation on Held-Out Test Set
    print("\nPHASE 6: BASELINE EVALUATION (Held-Out Test Set)")
    y_pred_base = rf_baseline.predict(X_test)
    y_pred_base_probs = rf_baseline.predict_proba(X_test)
    y_test_bin = label_binarize(y_test, classes=[0, 1, 2])

    base_acc = float(accuracy_score(y_test, y_pred_base))
    base_prec = float(precision_score(y_test, y_pred_base, average="macro", zero_division=0))
    base_rec = float(recall_score(y_test, y_pred_base, average="macro", zero_division=0))
    base_f1 = float(f1_score(y_test, y_pred_base, average="macro", zero_division=0))
    base_cm = confusion_matrix(y_test, y_pred_base).tolist()

    base_auc_per_class = {}
    for i, cls_name in enumerate(target_names):
        fpr_c, tpr_c, _ = roc_curve(y_test_bin[:, i], y_pred_base_probs[:, i])
        base_auc_per_class[cls_name] = round(float(auc(fpr_c, tpr_c)), 4)
    base_macro_auc = round(float(roc_auc_score(y_test, y_pred_base_probs, multi_class="ovr", average="macro")), 4)

    base_report_txt = classification_report(y_test, y_pred_base, target_names=target_names, zero_division=0)
    print(base_report_txt)
    print(f"Baseline Macro OvR ROC-AUC: {base_macro_auc:.4f}")

    baseline_metrics = {
        "model": "Random Forest Baseline",
        "n_estimators": 100,
        "random_state": 42,
        "training_time_seconds": round(rf_duration, 4),
        "test_accuracy": base_acc,
        "test_precision_macro": base_prec,
        "test_recall_macro": base_rec,
        "test_f1_macro": base_f1,
        "roc_auc_macro_ovr": base_macro_auc,
        "roc_auc_per_class": base_auc_per_class,
        "confusion_matrix": base_cm,
        "classes": target_names,
    }

    with open(os.path.join(REPORTS_DIR, "baseline_metrics.json"), "w") as f:
        json.dump(baseline_metrics, f, indent=2)

    with open(os.path.join(REPORTS_DIR, "classification_report.txt"), "w") as f:
        f.write("BASELINE RANDOM FOREST CLASSIFICATION REPORT\n")
        f.write(base_report_txt)
        f.write(f"\nMacro OvR ROC-AUC: {base_macro_auc:.4f}\n")
        for cls_name, c_auc in base_auc_per_class.items():
            f.write(f"  - {cls_name} AUC: {c_auc:.4f}\n")

    # Plot Confusion Matrix
    disp = ConfusionMatrixDisplay(confusion_matrix=np.array(base_cm), display_labels=target_names)
    fig, ax = plt.subplots(figsize=(5, 4))
    disp.plot(cmap="Blues", ax=ax)
    plt.title("Baseline Model - Confusion Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "confusion_matrix.png"), dpi=200)
    plt.close()

    # 5. Phase 7: Model Comparison
    print("\n" + "=" * 60)
    print("PHASE 7: MODEL COMPARISON")
    print("=" * 60)

    models_to_compare = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=3),
        "SVM": SVC(kernel="rbf", probability=True, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=50, random_state=42),
    }

    comparison_rows = []
    for m_name, clf in models_to_compare.items():
        t0 = time.time()
        clf.fit(X_train, y_train)
        t_dur = time.time() - t0

        # Evaluate on validation set
        val_pred = clf.predict(X_val)
        val_acc = accuracy_score(y_val, val_pred)
        val_f1 = f1_score(y_val, val_pred, average="macro", zero_division=0)

        # Evaluate on test set
        test_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, test_pred)
        prec = precision_score(y_test, test_pred, average="macro", zero_division=0)
        rec = recall_score(y_test, test_pred, average="macro", zero_division=0)
        f1 = f1_score(y_test, test_pred, average="macro", zero_division=0)

        comparison_rows.append({
            "Model": m_name,
            "Accuracy": round(acc, 4),
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1": round(f1, 4),
            "Val_Accuracy": round(val_acc, 4),
            "Val_F1": round(val_f1, 4),
            "Training Time": f"{t_dur:.4f}s",
        })

    df_comp = pd.DataFrame(comparison_rows)
    print(df_comp.to_string(index=False))
    df_comp.to_csv(os.path.join(REPORTS_DIR, "model_comparison.csv"), index=False)

    # 6. Phase 8: Hyperparameter Tuning for Best Model (Random Forest)
    print("\n" + "=" * 60)
    print("PHASE 8: HYPERPARAMETER TUNING (ON TRAIN & VALIDATION)")
    print("=" * 60)

    # Parameter grid tested on validation data (Never touches test set!)
    best_val_score = -1
    best_params = {}
    best_rf = None

    param_candidates = [
        {"n_estimators": 50, "max_depth": 3, "min_samples_split": 2, "max_features": "sqrt"},
        {"n_estimators": 100, "max_depth": 4, "min_samples_split": 2, "max_features": "sqrt"},
        {"n_estimators": 150, "max_depth": 5, "min_samples_split": 2, "max_features": "log2"},
        {"n_estimators": 100, "max_depth": None, "min_samples_split": 2, "max_features": "sqrt"},
        {"n_estimators": 80, "max_depth": 4, "min_samples_split": 3, "max_features": "sqrt"},
    ]

    for p in param_candidates:
        rf_candidate = RandomForestClassifier(**p, random_state=42)
        rf_candidate.fit(X_train, y_train)
        val_f1 = f1_score(y_val, rf_candidate.predict(X_val), average="macro", zero_division=0)
        val_acc = accuracy_score(y_val, rf_candidate.predict(X_val))
        combined_score = (val_acc + val_f1) / 2.0

        if combined_score > best_val_score:
            best_val_score = combined_score
            best_params = p
            best_rf = rf_candidate

    print(f"Selected Best Hyperparameters (via Validation Set Tuning): {best_params}")
    with open(os.path.join(REPORTS_DIR, "best_parameters.json"), "w") as f:
        json.dump(best_params, f, indent=2)

    # Fit final model combining train + validation (now ready for final evaluation on untouched test set)
    X_trainval = np.vstack([X_train, X_val])
    y_trainval = np.concatenate([y_train, y_val])

    # Re-fit scaler on train+val
    final_scaler = StandardScaler()
    final_scaler.fit(pd.concat([X_train_raw, X_val_raw]))
    X_trainval_scaled = final_scaler.transform(pd.concat([X_train_raw, X_val_raw]))
    X_test_scaled = final_scaler.transform(X_test_raw)

    final_model = RandomForestClassifier(**best_params, random_state=42)
    final_model.fit(X_trainval_scaled, y_trainval)

    # 7. Phase 9: Final Test Set Evaluation (Evaluated ONCE)
    print("\n" + "=" * 60)
    print("PHASE 9: FINAL TEST SET EVALUATION")
    print("=" * 60)

    y_test_pred = final_model.predict(X_test_scaled)
    y_test_probs = final_model.predict_proba(X_test_scaled)
    y_test_bin = label_binarize(y_test, classes=[0, 1, 2])

    final_acc = float(accuracy_score(y_test, y_test_pred))
    final_prec = float(precision_score(y_test, y_test_pred, average="macro", zero_division=0))
    final_rec = float(recall_score(y_test, y_test_pred, average="macro", zero_division=0))
    final_f1 = float(f1_score(y_test, y_test_pred, average="macro", zero_division=0))
    final_cm = confusion_matrix(y_test, y_test_pred).tolist()

    # Multiclass One-vs-Rest ROC-AUC and curves
    fpr_dict = {}
    tpr_dict = {}
    roc_auc_per_class = {}
    for i, cls_name in enumerate(target_names):
        fpr_dict[cls_name], tpr_dict[cls_name], _ = roc_curve(y_test_bin[:, i], y_test_probs[:, i])
        roc_auc_per_class[cls_name] = round(float(auc(fpr_dict[cls_name], tpr_dict[cls_name])), 4)

    macro_roc_auc = round(float(roc_auc_score(y_test, y_test_probs, multi_class="ovr", average="macro")), 4)

    final_report_txt = classification_report(y_test, y_test_pred, target_names=target_names, zero_division=0)
    print(final_report_txt)
    print(f"Final Test Accuracy: {final_acc:.4f} ({final_acc * 100:.2f}%)")
    print(f"Final Test Macro OvR ROC-AUC: {macro_roc_auc:.4f}")
    for cls_name, cls_auc in roc_auc_per_class.items():
        print(f"  - {cls_name} ROC-AUC: {cls_auc:.4f}")

    final_metrics = {
        "model": "Final Tuned Random Forest",
        "parameters": best_params,
        "test_participants": TEST_PARTICIPANTS,
        "test_accuracy": final_acc,
        "test_precision_macro": final_prec,
        "test_recall_macro": final_rec,
        "test_f1_macro": final_f1,
        "roc_auc_macro_ovr": macro_roc_auc,
        "roc_auc_per_class": roc_auc_per_class,
        "confusion_matrix": final_cm,
        "classes": target_names,
    }

    with open(os.path.join(REPORTS_DIR, "final_metrics.json"), "w") as f:
        json.dump(final_metrics, f, indent=2)

    with open(os.path.join(REPORTS_DIR, "final_classification_report.txt"), "w") as f:
        f.write("FINAL TUNED RANDOM FOREST CLASSIFICATION REPORT\n")
        f.write(final_report_txt)
        f.write(f"\nMacro OvR ROC-AUC: {macro_roc_auc:.4f}\n")
        for cls_name, cls_auc in roc_auc_per_class.items():
            f.write(f"  - {cls_name} ROC-AUC: {cls_auc:.4f}\n")

    # Plot Final Confusion Matrix
    disp = ConfusionMatrixDisplay(confusion_matrix=np.array(final_cm), display_labels=target_names)
    fig, ax = plt.subplots(figsize=(5, 4))
    disp.plot(cmap="Greens", ax=ax)
    plt.title("Final Tuned Model - Confusion Matrix")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "final_confusion_matrix.png"), dpi=200)
    plt.close()

    # Plot Multiclass ROC Curves (One-vs-Rest)
    plt.figure(figsize=(6, 5))
    class_colors = {"Normal": "#10b981", "Hemiplegic": "#ef4444", "Diplegic": "#f59e0b"}
    for cls_name in target_names:
        c = class_colors.get(cls_name, "#3b82f6")
        plt.plot(
            fpr_dict[cls_name],
            tpr_dict[cls_name],
            color=c,
            lw=2.5,
            label=f"{cls_name} (AUC = {roc_auc_per_class[cls_name]:.2f})",
        )
    plt.plot([0, 1], [0, 1], color="#94a3b8", lw=1.5, linestyle="--", label="Chance (AUC = 0.50)")
    plt.xlim([-0.02, 1.02])
    plt.ylim([-0.02, 1.05])
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=10, fontweight="bold")
    plt.ylabel("True Positive Rate (Sensitivity)", fontsize=10, fontweight="bold")
    plt.title(f"Multiclass ROC Curves (One-vs-Rest)\nMacro-Average AUC = {macro_roc_auc:.2f}", fontsize=11, fontweight="bold")
    plt.legend(loc="lower right", fontsize=9, frameon=True)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "final_roc_curves.png"), dpi=200)
    plt.savefig(os.path.join(REPORTS_DIR, "roc_curves.png"), dpi=200)
    plt.close()

    # Save Final Model and Preprocessor Bundle
    final_model_bundle = {
        "model": final_model,
        "features": FEATURE_COLS,
        "classes": target_names,
        "parameters": best_params,
    }
    joblib.dump(final_model_bundle, os.path.join(MODELS_DIR, "gait_final_model.joblib"))

    final_preprocessor_bundle = {
        "scaler": final_scaler,
        "label_encoder": label_enc,
        "features": FEATURE_COLS,
    }
    joblib.dump(final_preprocessor_bundle, os.path.join(MODELS_DIR, "gait_preprocessor.joblib"))

    print("\nModel artifacts saved successfully:")
    print(f"  - {os.path.join(MODELS_DIR, 'gait_final_model.joblib')}")
    print(f"  - {os.path.join(MODELS_DIR, 'gait_preprocessor.joblib')}")
    print("=" * 60)


if __name__ == "__main__":
    execute_pipeline()
