import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, IsolationForest, RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

def train_and_evaluate():
    print("=== PROJECT-002: Network Intrusion Detection & Anomaly Model Training ===")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_path = os.path.join(base_dir, "datasets", "KDDTest+.txt")
    clean_csv_path = os.path.join(base_dir, "datasets", "nsl_kdd_clean.csv")
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)

    columns = [
        'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
        'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
        'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
        'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login',
        'count', 'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate',
        'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count',
        'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
        'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
        'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate',
        'label', 'difficulty'
    ]

    print(f"Loading raw dataset from {raw_data_path}...")
    df = pd.read_csv(raw_data_path, names=columns)
    print(f"Loaded {len(df)} connection records.")

    # Standard attack mapping to 5 classes
    attack_map = {
        'normal': 'Normal',
        'neptune': 'DoS', 'back': 'DoS', 'smurf': 'DoS', 'pod': 'DoS', 'teardrop': 'DoS',
        'land': 'DoS', 'apache2': 'DoS', 'mailbomb': 'DoS', 'processtable': 'DoS', 'udpstorm': 'DoS',
        'portsweep': 'Probe', 'ipsweep': 'Probe', 'nmap': 'Probe', 'satan': 'Probe', 'mscan': 'Probe', 'saint': 'Probe',
        'guess_passwd': 'R2L', 'ftp_write': 'R2L', 'imap': 'R2L', 'phf': 'R2L', 'multihop': 'R2L',
        'warezmaster': 'R2L', 'warezclient': 'R2L', 'spy': 'R2L', 'xlock': 'R2L', 'xsnoop': 'R2L',
        'snmpguess': 'R2L', 'snmpgetattack': 'R2L', 'httptunnel': 'R2L', 'sendmail': 'R2L', 'named': 'R2L',
        'buffer_overflow': 'U2R', 'rootkit': 'U2R', 'loadmodule': 'U2R', 'perl': 'U2R',
        'sqlattack': 'U2R', 'xterm': 'U2R', 'ps': 'U2R'
    }

    df['attack_category'] = df['label'].map(lambda x: attack_map.get(x, 'DoS'))
    df['is_intrusion'] = (df['attack_category'] != 'Normal').astype(int)

    # Save cleaned dataset
    df.to_csv(clean_csv_path, index=False)
    print(f"Saved structured dataset to {clean_csv_path}")

    # Feature definitions
    num_cols = [
        'duration', 'src_bytes', 'dst_bytes', 'wrong_fragment', 'urgent', 'hot',
        'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted',
        'num_root', 'num_file_creations', 'num_shells', 'num_access_files',
        'count', 'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
        'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
        'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
        'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
        'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
        'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate'
    ]
    cat_cols = ['protocol_type', 'service', 'flag']

    feature_cols = num_cols + cat_cols
    X = df[feature_cols]
    y_cat = df['attack_category']
    y_binary = df['is_intrusion']

    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y_cat)
    joblib.dump(le, os.path.join(models_dir, "label_encoder.joblib"))

    # Train-test split
    X_train, X_test, y_train, y_test, y_bin_train, y_bin_test = train_test_split(
        X, y_encoded, y_binary, test_size=0.2, random_state=42, stratify=y_encoded
    )

    print(f"Training split: {X_train.shape[0]} samples, Testing split: {X_test.shape[0]} samples.")

    # Preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)
        ]
    )

    print("Fitting preprocessor...")
    X_train_trans = preprocessor.fit_transform(X_train)
    X_test_trans = preprocessor.transform(X_test)
    joblib.dump(preprocessor, os.path.join(models_dir, "nsl_preprocessor.joblib"))
    print(f"Transformed feature vector shape: {X_train_trans.shape}")

    # 1. Random Forest Classifier
    print("Training Random Forest Classifier (100 trees)...")
    rf_clf = RandomForestClassifier(n_estimators=100, max_depth=16, n_jobs=-1, random_state=42)
    rf_clf.fit(X_train_trans, y_train)
    rf_preds = rf_clf.predict(X_test_trans)
    rf_acc = accuracy_score(y_test, rf_preds)
    rf_f1_macro = f1_score(y_test, rf_preds, average='macro')
    rf_f1_weighted = f1_score(y_test, rf_preds, average='weighted')
    print(f"Random Forest Accuracy: {rf_acc:.4f}, Weighted F1: {rf_f1_weighted:.4f}")
    joblib.dump(rf_clf, os.path.join(models_dir, "rf_nids_classifier.joblib"))

    # 2. Extra Trees Classifier
    print("Training Extra Trees Classifier (100 trees)...")
    et_clf = ExtraTreesClassifier(n_estimators=100, max_depth=16, n_jobs=-1, random_state=42)
    et_clf.fit(X_train_trans, y_train)
    et_preds = et_clf.predict(X_test_trans)
    et_acc = accuracy_score(y_test, et_preds)
    et_f1_weighted = f1_score(y_test, et_preds, average='weighted')
    print(f"Extra Trees Accuracy: {et_acc:.4f}, Weighted F1: {et_f1_weighted:.4f}")
    joblib.dump(et_clf, os.path.join(models_dir, "et_nids_classifier.joblib"))

    # 3. Isolation Forest for Anomaly / Zero-Day Detection
    print("Training Isolation Forest Anomaly Detector...")
    # Fit on training set
    iso_forest = IsolationForest(n_estimators=100, contamination=0.18, random_state=42, n_jobs=-1)
    iso_forest.fit(X_train_trans)
    # IsolationForest returns -1 for anomaly, 1 for inlier
    iso_raw_preds = iso_forest.predict(X_test_trans)
    iso_anomaly_preds = (iso_raw_preds == -1).astype(int)  # 1 = intrusion/anomaly, 0 = normal
    iso_acc = accuracy_score(y_bin_test, iso_anomaly_preds)
    iso_recall = recall_score(y_bin_test, iso_anomaly_preds)
    print(f"Isolation Forest Anomaly Detection Accuracy: {iso_acc:.4f}, Intrusion Recall: {iso_recall:.4f}")
    joblib.dump(iso_forest, os.path.join(models_dir, "isolation_forest_anomaly.joblib"))

    # Detailed Classification Report
    class_names = list(le.classes_)
    report = classification_report(y_test, rf_preds, target_names=class_names, output_dict=True)
    cm = confusion_matrix(y_test, rf_preds).tolist()

    metrics = {
        "dataset_name": "NSL-KDD Network Intrusion Benchmark",
        "total_records": len(df),
        "train_samples": int(X_train.shape[0]),
        "test_samples": int(X_test.shape[0]),
        "features_count": int(X_train_trans.shape[1]),
        "classes": class_names,
        "random_forest": {
            "accuracy": round(float(rf_acc), 4),
            "macro_f1": round(float(rf_f1_macro), 4),
            "weighted_f1": round(float(rf_f1_weighted), 4),
            "classification_report": report,
            "confusion_matrix": cm
        },
        "extra_trees": {
            "accuracy": round(float(et_acc), 4),
            "weighted_f1": round(float(et_f1_weighted), 4)
        },
        "isolation_forest": {
            "accuracy": round(float(iso_acc), 4),
            "intrusion_recall": round(float(iso_recall), 4),
            "contamination": 0.18
        }
    }

    metrics_file = os.path.join(models_dir, "nids_metrics.json")
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {metrics_file}")
    print("All models successfully trained, evaluated, and saved!")

if __name__ == "__main__":
    train_and_evaluate()
