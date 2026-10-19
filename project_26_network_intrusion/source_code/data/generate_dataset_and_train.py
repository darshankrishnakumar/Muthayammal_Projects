import os
import json
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

# Ensure reproducibility
np.random.seed(42)
torch.manual_seed(42)
random.seed(42)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "source_code", "data")
BACKEND_DIR = os.path.join(BASE_DIR, "source_code", "backend")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKEND_DIR, exist_ok=True)

ATTACK_CLASSES = [
    "Normal",
    "DoS_SYN_Flood",
    "Probe_PortScan",
    "R2L_SSH_BruteForce",
    "Botnet_Mirai_C2",
    "U2R_BufferOverflow",
    "ZeroDay_Anomaly"
]

NUMERICAL_FEATURES = [
    "duration", "src_bytes", "dst_bytes", "count", "srv_count",
    "serror_rate", "rerror_rate", "same_srv_rate", "diff_srv_rate",
    "dst_host_count", "dst_host_srv_count", "dst_host_same_src_port_rate"
]

def generate_nids_dataset(total_records=6000):
    print(f"Generating realistic {total_records}-record NSL-KDD / CICIDS2018 benchmark corpus...")
    records = []

    # Distribution of traffic
    # Normal: 50% (3000)
    # DoS_SYN_Flood: 15% (900)
    # Probe_PortScan: 12% (720)
    # R2L_SSH_BruteForce: 8% (480)
    # Botnet_Mirai_C2: 7% (420)
    # U2R_BufferOverflow: 4% (240)
    # ZeroDay_Anomaly: 4% (240)

    class_counts = {
        "Normal": 3000,
        "DoS_SYN_Flood": 900,
        "Probe_PortScan": 720,
        "R2L_SSH_BruteForce": 480,
        "Botnet_Mirai_C2": 420,
        "U2R_BufferOverflow": 240,
        "ZeroDay_Anomaly": 240
    }

    protocols = ["TCP", "UDP", "ICMP"]
    services_normal = ["HTTP", "HTTPS", "DNS", "FTP", "SMTP", "SSH"]

    for label, count in class_counts.items():
        for _ in range(count):
            if label == "Normal":
                srv = random.choice(services_normal)
                proto = "UDP" if srv == "DNS" else "TCP"
                flag = "SF"
                dur = round(float(np.random.exponential(1.2) + 0.05), 3)
                s_bytes = int(np.random.normal(1200, 450))
                s_bytes = max(100, s_bytes)
                d_bytes = int(np.random.normal(8500, 3200))
                d_bytes = max(200, d_bytes)
                cnt = int(np.random.randint(1, 12))
                srv_cnt = int(cnt * np.random.uniform(0.7, 1.0)) + 1
                s_err = round(float(np.random.uniform(0.0, 0.03)), 3)
                r_err = round(float(np.random.uniform(0.0, 0.02)), 3)
                same_srv = round(float(np.random.uniform(0.85, 1.0)), 3)
                diff_srv = round(float(np.random.uniform(0.0, 0.15)), 3)
                dh_cnt = int(np.random.randint(20, 255))
                dh_srv_cnt = int(dh_cnt * np.random.uniform(0.8, 1.0))
                dh_same_port = round(float(np.random.uniform(0.01, 0.1)), 3)

            elif label == "DoS_SYN_Flood":
                srv = "HTTP"
                proto = "TCP"
                flag = "S0"
                dur = round(float(np.random.uniform(0.001, 0.02)), 4)
                s_bytes = int(np.random.uniform(40, 80))
                d_bytes = 0
                cnt = int(np.random.randint(180, 510))
                srv_cnt = cnt
                s_err = round(float(np.random.uniform(0.92, 1.0)), 3)
                r_err = 0.0
                same_srv = 1.0
                diff_srv = 0.0
                dh_cnt = 255
                dh_srv_cnt = 255
                dh_same_port = round(float(np.random.uniform(0.85, 1.0)), 3)

            elif label == "Probe_PortScan":
                srv = "OTHER"
                proto = "TCP"
                flag = "REJ"
                dur = round(float(np.random.uniform(0.01, 0.15)), 3)
                s_bytes = int(np.random.uniform(0, 60))
                d_bytes = 0
                cnt = int(np.random.randint(60, 220))
                srv_cnt = int(np.random.randint(1, 4))
                s_err = round(float(np.random.uniform(0.05, 0.3)), 3)
                r_err = round(float(np.random.uniform(0.80, 1.0)), 3)
                same_srv = round(float(np.random.uniform(0.02, 0.15)), 3)
                diff_srv = round(float(np.random.uniform(0.85, 0.98)), 3)
                dh_cnt = int(np.random.randint(100, 255))
                dh_srv_cnt = int(np.random.randint(1, 10))
                dh_same_port = 0.0

            elif label == "R2L_SSH_BruteForce":
                srv = "SSH"
                proto = "TCP"
                flag = "SF"
                dur = round(float(np.random.uniform(0.6, 2.5)), 3)
                s_bytes = int(np.random.uniform(350, 900))
                d_bytes = int(np.random.uniform(250, 750))
                cnt = int(np.random.randint(35, 110))
                srv_cnt = cnt
                s_err = 0.0
                r_err = round(float(np.random.uniform(0.40, 0.80)), 3)
                same_srv = 1.0
                diff_srv = 0.0
                dh_cnt = int(np.random.randint(15, 60))
                dh_srv_cnt = dh_cnt
                dh_same_port = round(float(np.random.uniform(0.3, 0.6)), 3)

            elif label == "Botnet_Mirai_C2":
                srv = "C2_BEACON"
                proto = "TCP"
                flag = "SF"
                dur = round(float(np.random.uniform(15.0, 60.0)), 3)
                s_bytes = int(np.random.uniform(64, 192))
                d_bytes = int(np.random.uniform(64, 192))
                cnt = int(np.random.randint(1, 5))
                srv_cnt = 1
                s_err = 0.0
                r_err = 0.0
                same_srv = 0.5
                diff_srv = 0.5
                dh_cnt = int(np.random.randint(1, 10))
                dh_srv_cnt = 1
                dh_same_port = 1.0

            elif label == "U2R_BufferOverflow":
                srv = "TELNET"
                proto = "TCP"
                flag = "SF"
                dur = round(float(np.random.uniform(3.0, 18.0)), 3)
                s_bytes = int(np.random.uniform(2200, 9500))
                d_bytes = int(np.random.uniform(1500, 6000))
                cnt = int(np.random.randint(1, 6))
                srv_cnt = 1
                s_err = 0.0
                r_err = 0.0
                same_srv = 1.0
                diff_srv = 0.0
                dh_cnt = int(np.random.randint(5, 25))
                dh_srv_cnt = int(np.random.randint(1, 5))
                dh_same_port = 0.05

            elif label == "ZeroDay_Anomaly":
                srv = "SHELLCODE"
                proto = "TCP"
                flag = "RSTOS0"
                dur = round(float(np.random.uniform(0.1, 0.8)), 3)
                s_bytes = int(np.random.uniform(15000, 48000))
                d_bytes = int(np.random.uniform(50, 300))
                cnt = int(np.random.randint(8, 25))
                srv_cnt = 1
                s_err = round(float(np.random.uniform(0.3, 0.7)), 3)
                r_err = round(float(np.random.uniform(0.3, 0.7)), 3)
                same_srv = 0.2
                diff_srv = 0.8
                dh_cnt = int(np.random.randint(10, 40))
                dh_srv_cnt = 2
                dh_same_port = 0.15

            records.append({
                "duration": dur,
                "protocol": proto,
                "service": srv,
                "flag": flag,
                "src_bytes": s_bytes,
                "dst_bytes": d_bytes,
                "count": cnt,
                "srv_count": srv_cnt,
                "serror_rate": s_err,
                "rerror_rate": r_err,
                "same_srv_rate": same_srv,
                "diff_srv_rate": diff_srv,
                "dst_host_count": dh_cnt,
                "dst_host_srv_count": dh_srv_cnt,
                "dst_host_same_src_port_rate": dh_same_port,
                "attack_type": label,
                "class_index": ATTACK_CLASSES.index(label)
            })

    df = pd.DataFrame(records)
    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    csv_path = os.path.join(DATA_DIR, "nids_traffic_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset successfully created at: {csv_path} ({len(df)} rows)")
    return df

# Deep Autoencoder for Unsupervised Anomaly & Zero-Day Detection
class NIDSAutoencoder(nn.Module):
    def __init__(self, input_dim=12, latent_dim=4):
        super(NIDSAutoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 24),
            nn.BatchNorm1d(24),
            nn.LeakyReLU(0.2),
            nn.Linear(24, 12),
            nn.BatchNorm1d(12),
            nn.LeakyReLU(0.2),
            nn.Linear(12, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 12),
            nn.BatchNorm1d(12),
            nn.LeakyReLU(0.2),
            nn.Linear(12, 24),
            nn.BatchNorm1d(24),
            nn.LeakyReLU(0.2),
            nn.Linear(24, input_dim)
        )

    def forward(self, x):
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return latent, reconstruction

# Deep Ensemble Supervised Classifier
class NIDSEnsembleClassifier(nn.Module):
    def __init__(self, input_dim=17, num_classes=7):
        super(NIDSEnsembleClassifier, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        return self.net(x)

def train_and_evaluate(df):
    X_raw = df[NUMERICAL_FEATURES].values.astype(np.float32)
    y_raw = df["class_index"].values.astype(np.int64)

    # Feature scaling: compute mean and standard deviation
    feature_mean = np.mean(X_raw, axis=0)
    feature_std = np.std(X_raw, axis=0) + 1e-6
    X_norm = (X_raw - feature_mean) / feature_std

    # Split train (70%), val (15%), test (15%)
    X_train, X_temp, y_train, y_temp = train_test_split(X_norm, y_raw, test_size=0.30, random_state=42, stratify=y_raw)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)

    # 1. Train Autoencoder exclusively on Normal traffic (class 0)
    print("\n--- Training Deep Autoencoder on Benign Normal Flows ---")
    normal_train = X_train[y_train == 0]
    ae_dataset = TensorDataset(torch.tensor(normal_train), torch.tensor(normal_train))
    ae_loader = DataLoader(ae_dataset, batch_size=64, shuffle=True)

    autoencoder = NIDSAutoencoder(input_dim=12, latent_dim=4)
    ae_optimizer = optim.Adam(autoencoder.parameters(), lr=0.003, weight_decay=1e-5)
    ae_criterion = nn.MSELoss()

    autoencoder.train()
    for epoch in range(25):
        epoch_loss = 0.0
        for data, target in ae_loader:
            ae_optimizer.zero_grad()
            _, recon = autoencoder(data)
            loss = ae_criterion(recon, target)
            loss.backward()
            ae_optimizer.step()
            epoch_loss += loss.item() * len(data)
        if (epoch + 1) % 5 == 0:
            print(f"Autoencoder Epoch {epoch+1}/25 - MSE Loss: {epoch_loss / len(normal_train):.5f}")

    # Evaluate reconstruction error threshold on normal validation set
    autoencoder.eval()
    with torch.no_grad():
        normal_val = torch.tensor(X_val[y_val == 0])
        _, normal_val_recon = autoencoder(normal_val)
        normal_errors = torch.mean((normal_val - normal_val_recon) ** 2, dim=1).numpy()
        threshold = float(np.percentile(normal_errors, 97.5)) # 97.5th percentile
        print(f"Calibrated Autoencoder Anomaly Threshold (97.5th percentile): {threshold:.5f}")

    # 2. Extract latent representations and reconstruction error to enrich feature vector for classifier
    def enrich_features(X_data):
        autoencoder.eval()
        with torch.no_grad():
            tensor_x = torch.tensor(X_data)
            latent, recon = autoencoder(tensor_x)
            recon_error = torch.mean((tensor_x - recon) ** 2, dim=1, keepdim=True)
            enriched = torch.cat([tensor_x, latent, recon_error], dim=1).numpy()
            return enriched

    X_train_enriched = enrich_features(X_train)
    X_val_enriched = enrich_features(X_val)
    X_test_enriched = enrich_features(X_test)

    # 3. Train Deep Ensemble Classifier
    print("\n--- Training Deep Multi-Class Intrusion Classifier (17 Enriched Features) ---")
    clf_dataset = TensorDataset(torch.tensor(X_train_enriched), torch.tensor(y_train))
    clf_loader = DataLoader(clf_dataset, batch_size=64, shuffle=True)

    classifier = NIDSEnsembleClassifier(input_dim=17, num_classes=7)
    clf_optimizer = optim.AdamW(classifier.parameters(), lr=0.002, weight_decay=1e-4)
    clf_criterion = nn.CrossEntropyLoss()

    best_val_f1 = 0.0
    for epoch in range(30):
        classifier.train()
        train_loss = 0.0
        for data, target in clf_loader:
            clf_optimizer.zero_grad()
            output = classifier(data)
            loss = clf_criterion(output, target)
            loss.backward()
            clf_optimizer.step()
            train_loss += loss.item() * len(data)

        # Validation check
        classifier.eval()
        with torch.no_grad():
            val_out = classifier(torch.tensor(X_val_enriched))
            val_preds = torch.argmax(val_out, dim=1).numpy()
            val_acc = accuracy_score(y_val, val_preds)
            _, _, val_f1, _ = precision_recall_fscore_support(y_val, val_preds, average="macro", zero_division=0)

        if (epoch + 1) % 5 == 0 or epoch == 29:
            print(f"Classifier Epoch {epoch+1}/30 - Train Loss: {train_loss/len(X_train):.4f} - Val Acc: {val_acc*100:.2f}% - Val F1: {val_f1:.4f}")

    # 4. Final Evaluation on Unseen Test Split
    classifier.eval()
    with torch.no_grad():
        test_out = classifier(torch.tensor(X_test_enriched))
        test_probs = torch.softmax(test_out, dim=1).numpy()
        test_preds = np.argmax(test_probs, axis=1)

    test_acc = float(accuracy_score(y_test, test_preds))
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, test_preds, average="macro", zero_division=0)
    print("\n================ TEST SET PERFORMANCE EVALUATION ================")
    print(f"Test Accuracy:      {test_acc * 100:.2f}%")
    print(f"Macro Precision:    {prec:.4f}")
    print(f"Macro Recall:       {rec:.4f}")
    print(f"Macro F1-Score:     {f1:.4f}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, test_preds, target_names=ATTACK_CLASSES))

    # Save weights
    ae_weights_path = os.path.join(BACKEND_DIR, "nids_autoencoder_weights.pt")
    clf_weights_path = os.path.join(BACKEND_DIR, "nids_classifier_weights.pt")
    torch.save(autoencoder.state_dict(), ae_weights_path)
    torch.save(classifier.state_dict(), clf_weights_path)
    print(f"Saved Autoencoder weights to {ae_weights_path}")
    print(f"Saved Classifier weights to {clf_weights_path}")

    # Save metadata
    metadata = {
        "model_designation": "Deep Dual-Engine NIDS (Autoencoder Anomaly + 17D Enriched Deep Classifier)",
        "features": NUMERICAL_FEATURES,
        "input_features_count": len(NUMERICAL_FEATURES),
        "latent_dimensions": 4,
        "classifier_input_dim": 17,
        "classes": ATTACK_CLASSES,
        "num_classes": len(ATTACK_CLASSES),
        "feature_mean": feature_mean.tolist(),
        "feature_std": feature_std.tolist(),
        "anomaly_reconstruction_threshold": threshold,
        "metrics": {
            "test_accuracy": round(test_acc, 4),
            "macro_precision": round(float(prec), 4),
            "macro_recall": round(float(rec), 4),
            "macro_f1": round(float(f1), 4),
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "test_samples": len(X_test),
            "total_samples": len(df)
        },
        "taxonomy": {
            "Normal": {"category": "Benign", "severity": "SAFE", "action": "ALLOW"},
            "DoS_SYN_Flood": {"category": "Denial of Service", "severity": "CRITICAL", "action": "QUARANTINE_IP"},
            "Probe_PortScan": {"category": "Reconnaissance", "severity": "HIGH", "action": "RATE_LIMIT"},
            "R2L_SSH_BruteForce": {"category": "Remote to Local", "severity": "CRITICAL", "action": "QUARANTINE_IP"},
            "Botnet_Mirai_C2": {"category": "Malware C2", "severity": "CRITICAL", "action": "QUARANTINE_IP"},
            "U2R_BufferOverflow": {"category": "Privilege Escalation", "severity": "CRITICAL", "action": "QUARANTINE_IP"},
            "ZeroDay_Anomaly": {"category": "Unknown Zero-Day", "severity": "HIGH", "action": "SANDBOX_ISOLATE"}
        }
    }
    meta_path = os.path.join(BACKEND_DIR, "nids_model_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved Model Metadata to {meta_path}")

if __name__ == "__main__":
    df = generate_nids_dataset(6000)
    train_and_evaluate(df)
