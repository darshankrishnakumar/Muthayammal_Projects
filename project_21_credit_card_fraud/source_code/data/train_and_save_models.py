import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
import joblib

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(DATA_DIR, "..", "backend"))

def generate_and_train():
    np.random.seed(42)
    n_samples = 10000
    fraud_ratio = 0.025  # 2.5% fraud rate
    n_fraud = int(n_samples * fraud_ratio)
    n_normal = n_samples - n_fraud

    # 1. Normal transactions
    X_normal = np.random.normal(0.0, 1.0, (n_normal, 30))
    X_normal[:, 0] = np.random.uniform(0, 86400, n_normal)    # Time
    X_normal[:, 1] = np.random.exponential(68.5, n_normal)    # Amount
    y_normal = np.zeros(n_normal, dtype=int)

    # 2. Fraudulent transactions (characteristic shifts in V14, V4, V12, V10, V17, Amount)
    X_fraud = np.random.normal(0.0, 1.2, (n_fraud, 30))
    # Time clustered at night hours
    X_fraud[:, 0] = np.random.choice([np.random.uniform(1000, 18000), np.random.uniform(72000, 86400)], n_fraud)
    # Amounts either micro carding tests or luxury jewelry
    X_fraud[:, 1] = np.random.choice([
        np.random.uniform(0.85, 4.50),
        np.random.uniform(1200.0, 5200.0)
    ], n_fraud)
    X_fraud[:, 2 + 13] = np.random.normal(-5.5, 1.4, n_fraud) # V14 strongly negative
    X_fraud[:, 2 + 3]  = np.random.normal(4.3, 1.1, n_fraud)  # V4 strongly positive
    X_fraud[:, 2 + 11] = np.random.normal(-4.6, 1.3, n_fraud) # V12 negative
    X_fraud[:, 2 + 9]  = np.random.normal(-3.9, 1.2, n_fraud) # V10 negative
    X_fraud[:, 2 + 16] = np.random.normal(-3.5, 1.3, n_fraud) # V17 negative
    y_fraud = np.ones(n_fraud, dtype=int)

    X = np.vstack([X_normal, X_fraud])
    y = np.concatenate([y_normal, y_fraud])

    # Shuffle
    indices = np.arange(n_samples)
    np.random.shuffle(indices)
    X = X[indices]
    y = y[indices]

    columns = ['Time', 'Amount'] + [f'V{i}' for i in range(1, 29)]
    df = pd.DataFrame(X, columns=columns)
    df['Class'] = y

    csv_path = os.path.join(DATA_DIR, "creditcard_transactions.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ Generated dataset saved to {csv_path} ({n_samples} records, {n_fraud} fraud)")

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    # 1. Random Forest Classifier
    print("Training Random Forest Classifier (100 estimators)...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, class_weight='balanced', random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict_proba(X_test)[:, 1]
    rf_auc = roc_auc_score(y_test, rf_preds)
    rf_pr_auc = average_precision_score(y_test, rf_preds)
    print(f"Random Forest AUC-ROC: {rf_auc:.4f}, PR-AUC: {rf_pr_auc:.4f}")
    joblib.dump(rf, os.path.join(BACKEND_DIR, "rf_fraud_model.joblib"))

    # 2. Gradient Boosting Classifier
    print("Training Gradient Boosting Classifier (100 estimators)...")
    gbm = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    gbm.fit(X_train, y_train)
    gbm_preds = gbm.predict_proba(X_test)[:, 1]
    gbm_auc = roc_auc_score(y_test, gbm_preds)
    print(f"Gradient Boosting AUC-ROC: {gbm_auc:.4f}")
    joblib.dump(gbm, os.path.join(BACKEND_DIR, "gbm_fraud_model.joblib"))

    # 3. Neural Network Classifier (MLP)
    print("Training Neural Network Classifier (MLP 64-32)...")
    mlp = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=200, random_state=42)
    mlp.fit(X_train, y_train)
    mlp_preds = mlp.predict_proba(X_test)[:, 1]
    mlp_auc = roc_auc_score(y_test, mlp_preds)
    print(f"Neural Network AUC-ROC: {mlp_auc:.4f}")
    joblib.dump(mlp, os.path.join(BACKEND_DIR, "neural_fraud_model.joblib"))

    print("✅ All 3 ML/DL models successfully trained and serialized to backend!")

if __name__ == '__main__':
    generate_and_train()
