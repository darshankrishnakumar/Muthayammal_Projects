import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def train_churn_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "Telco-Customer-Churn.csv")
    if not os.path.exists(data_path):
        data_path = os.path.join(
            os.path.dirname(base_dir),
            "Customer-Survival-Analysis-and-Churn-Prediction-master",
            "Telco-Customer-Churn.csv",
        )

    print(f"Loading telecom dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Raw dataset shape: {df.shape}")

    # Data cleaning & validation
    # Fix TotalCharges whitespace / missing values
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].astype(str).str.strip(), errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"] * df["tenure"])
    df["TotalCharges"] = df["TotalCharges"].fillna(0.0)

    # Encode target: Yes -> 1, No -> 0
    df["Churn"] = df["Churn"].apply(lambda x: 1 if str(x).strip().lower() == "yes" else 0)

    numeric_features = ["tenure", "MonthlyCharges", "TotalCharges"]
    categorical_features = [
        "gender",
        "SeniorCitizen",
        "Partner",
        "Dependents",
        "PhoneService",
        "MultipleLines",
        "InternetService",
        "OnlineSecurity",
        "OnlineBackup",
        "DeviceProtection",
        "TechSupport",
        "StreamingTV",
        "StreamingMovies",
        "Contract",
        "PaperlessBilling",
        "PaymentMethod",
    ]

    all_features = numeric_features + categorical_features
    X = df[all_features].copy()
    y = df["Churn"].copy()

    # 80:20 Train-Test split stratified on Churn
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Training records: {len(X_train)}, Testing records: {len(X_test)}")

    # Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_features,
            ),
        ]
    )

    # Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight="balanced",
    )

    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", rf_model)])

    print("Fitting Random Forest Pipeline...")
    pipeline.fit(X_train, y_train)

    # Evaluation on held-out test data
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    roc_auc = float(roc_auc_score(y_test, y_prob))
    cm = confusion_matrix(y_test, y_pred).tolist()

    metrics = {
        "model": "Random Forest Classifier",
        "datasetSource": "Telco-Customer-Churn.csv (IBM Telecom Dataset)",
        "trainRecordCount": int(len(X_train)),
        "testRecordCount": int(len(X_test)),
        "totalRecordCount": int(len(df)),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1Score": round(f1, 4),
        "rocAuc": round(roc_auc, 4),
        "confusionMatrix": {
            "trueNegative": cm[0][0],
            "falsePositive": cm[0][1],
            "falseNegative": cm[1][0],
            "truePositive": cm[1][1],
        },
        "featureNames": all_features,
    }

    print("--- EVALUATION METRICS ---")
    print(json.dumps(metrics, indent=2))

    # Persistence
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)

    pipeline_path = os.path.join(models_dir, "churn_pipeline.joblib")
    metrics_path = os.path.join(models_dir, "metrics.json")

    joblib.dump(pipeline, pipeline_path)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved pipeline artifact to: {pipeline_path}")
    print(f"Saved evaluation metrics to: {metrics_path}")
    return pipeline, metrics


if __name__ == "__main__":
    train_churn_model()
