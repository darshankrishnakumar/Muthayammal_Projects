#!/usr/bin/env python3
"""
AI-Based IoT Device Anomaly Detection for Smart Home Security
Dataset Generator & Dual PyTorch Model Trainer

Generates 5,500 realistic IoT network flow records across 6 device profiles and 6 traffic states.
Trains and serializes:
1. IoTAnomalyAutoencoder (Reconstruction Error Anomaly Detector)
2. IoTThreatClassifier (Multi-Class Cyber-Threat Signature Classifier)
"""

import os
import json
import csv
import math
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Reproducibility seeds
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

DEVICES = {
    'Smart IP Camera': {'ip': '192.168.1.42', 'proto': 'RTSP / TCP', 'norm_packet': 1240, 'norm_rate': 45, 'icon': '📹', 'role': 'Living Room Cam'},
    'Smart Thermostat': {'ip': '192.168.1.18', 'proto': 'MQTT / TLS', 'norm_packet': 180, 'norm_rate': 2, 'icon': '🌡️', 'role': 'HVAC Control Node'},
    'Smart Lock': {'ip': '192.168.1.105', 'proto': 'Zigbee / BLE Gateway', 'norm_packet': 64, 'norm_rate': 0.5, 'icon': '🔐', 'role': 'Front Entrance Deadbolt'},
    'Smart TV 4K': {'ip': '192.168.1.88', 'proto': 'HTTPS / SSDP', 'norm_packet': 1420, 'norm_rate': 120, 'icon': '📺', 'role': 'Media Room OLED'},
    'Edge Wi-Fi Router': {'ip': '192.168.1.1', 'proto': 'DNS / DHCP / NTP', 'norm_packet': 512, 'norm_rate': 250, 'icon': '📡', 'role': 'Core Gateway'},
    'Smart Voice Assistant': {'ip': '192.168.1.73', 'proto': 'mDNS / WebSockets', 'norm_packet': 320, 'norm_rate': 15, 'icon': '🔊', 'role': 'Kitchen Assistant'}
}

CLASSES = [
    'Normal Baseline Traffic',
    'Mirai Botnet C&C',
    'SYN Flood DDoS',
    'External Port Scan',
    'Covert Data Exfiltration',
    'Brute-Force SSH Auth'
]

CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}
IDX_TO_CLASS = {i: c for i, c in enumerate(CLASSES)}

FEATURE_NAMES = [
    'packet_size_bytes',
    'packet_rate_pps',
    'syn_ratio',
    'payload_entropy',
    'conn_freq_hz',
    'byte_rate_bps',
    'port_diversity',
    'retransmission_rate'
]

def generate_telemetry_vector(device_name, traffic_type):
    dev = DEVICES[device_name]
    base_pkt = dev['norm_packet']
    base_rate = dev['norm_rate']

    if traffic_type == 'Normal Baseline Traffic':
        packet_size = max(40, base_pkt * random.uniform(0.85, 1.15))
        packet_rate = max(0.1, base_rate * random.uniform(0.8, 1.2))
        syn_ratio = random.uniform(0.01, 0.10)
        payload_entropy = random.uniform(3.2, 5.0)
        conn_freq = max(0.1, packet_rate * random.uniform(0.2, 0.5))
        byte_rate = packet_size * packet_rate
        port_diversity = random.uniform(0.01, 0.08)
        retrans_rate = random.uniform(0.001, 0.02)
    elif traffic_type == 'Mirai Botnet C&C':
        packet_size = random.uniform(60, 220)
        packet_rate = base_rate * random.uniform(5.0, 15.0)
        syn_ratio = random.uniform(0.40, 0.75)
        payload_entropy = random.uniform(6.5, 7.8)
        conn_freq = packet_rate * random.uniform(0.8, 1.5)
        byte_rate = packet_size * packet_rate
        port_diversity = random.uniform(0.70, 0.95)
        retrans_rate = random.uniform(0.15, 0.35)
    elif traffic_type == 'SYN Flood DDoS':
        packet_size = random.uniform(40, 90)
        packet_rate = max(500, base_rate * random.uniform(15.0, 40.0))
        syn_ratio = random.uniform(0.88, 0.99)
        payload_entropy = random.uniform(2.0, 3.8)
        conn_freq = packet_rate * random.uniform(0.9, 1.1)
        byte_rate = packet_size * packet_rate
        port_diversity = random.uniform(0.05, 0.25)
        retrans_rate = random.uniform(0.40, 0.75)
    elif traffic_type == 'External Port Scan':
        packet_size = random.uniform(44, 80)
        packet_rate = random.uniform(50, 200)
        syn_ratio = random.uniform(0.75, 0.95)
        payload_entropy = random.uniform(2.5, 4.2)
        conn_freq = random.uniform(80, 250)
        byte_rate = packet_size * packet_rate
        port_diversity = random.uniform(0.85, 1.0)
        retrans_rate = random.uniform(0.05, 0.20)
    elif traffic_type == 'Covert Data Exfiltration':
        packet_size = random.uniform(1200, 1500)
        packet_rate = base_rate * random.uniform(2.0, 6.0)
        syn_ratio = random.uniform(0.05, 0.15)
        payload_entropy = random.uniform(7.4, 7.98) # encrypted ciphertext payload
        conn_freq = random.uniform(2.0, 10.0)
        byte_rate = packet_size * packet_rate
        port_diversity = random.uniform(0.02, 0.10)
        retrans_rate = random.uniform(0.01, 0.05)
    elif traffic_type == 'Brute-Force SSH Auth':
        packet_size = random.uniform(180, 420)
        packet_rate = random.uniform(10, 45)
        syn_ratio = random.uniform(0.30, 0.60)
        payload_entropy = random.uniform(5.5, 6.8)
        conn_freq = random.uniform(5.0, 20.0)
        byte_rate = packet_size * packet_rate
        port_diversity = random.uniform(0.02, 0.08)
        retrans_rate = random.uniform(0.20, 0.50)
    else:
        raise ValueError(f"Unknown traffic type: {traffic_type}")

    return [
        round(packet_size, 2),
        round(packet_rate, 2),
        round(syn_ratio, 4),
        round(payload_entropy, 3),
        round(conn_freq, 2),
        round(byte_rate, 2),
        round(port_diversity, 4),
        round(retrans_rate, 4)
    ]

def build_dataset(total_records=5500):
    dataset = []
    device_names = list(DEVICES.keys())

    # Distribute traffic: 55% normal baseline, 45% evenly across attacks
    num_normal = int(total_records * 0.55)
    num_attacks = total_records - num_normal
    attacks_per_class = num_attacks // 5

    # 1. Normal Records
    for i in range(num_normal):
        dev = random.choice(device_names)
        feats = generate_telemetry_vector(dev, 'Normal Baseline Traffic')
        dataset.append({
            'flow_id': f'FLOW_{i+1:05d}',
            'device_name': dev,
            'traffic_type': 'Normal Baseline Traffic',
            'traffic_idx': 0,
            'is_anomaly': False,
            'features': feats
        })

    # 2. Attack Records
    flow_idx = num_normal + 1
    for att_type in CLASSES[1:]:
        for _ in range(attacks_per_class):
            dev = random.choice(device_names)
            feats = generate_telemetry_vector(dev, att_type)
            dataset.append({
                'flow_id': f'FLOW_{flow_idx:05d}',
                'device_name': dev,
                'traffic_type': att_type,
                'traffic_idx': CLASS_TO_IDX[att_type],
                'is_anomaly': True,
                'features': feats
            })
            flow_idx += 1

    # Fill remainder if any
    while len(dataset) < total_records:
        dev = random.choice(device_names)
        att_type = random.choice(CLASSES[1:])
        feats = generate_telemetry_vector(dev, att_type)
        dataset.append({
            'flow_id': f'FLOW_{flow_idx:05d}',
            'device_name': dev,
            'traffic_type': att_type,
            'traffic_idx': CLASS_TO_IDX[att_type],
            'is_anomaly': True,
            'features': feats
        })
        flow_idx += 1

    random.shuffle(dataset)
    return dataset

# ─── MODEL 1: DEEP IOT ANOMALY AUTOENCODER ─────────────────────────────────────

class IoTAnomalyAutoencoder(nn.Module):
    def __init__(self, in_features=8, latent_dim=4):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(in_features, 16),
            nn.LayerNorm(16),
            nn.LeakyReLU(0.2),
            nn.Linear(16, 8),
            nn.LayerNorm(8),
            nn.LeakyReLU(0.2),
            nn.Linear(8, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 8),
            nn.LayerNorm(8),
            nn.LeakyReLU(0.2),
            nn.Linear(8, 16),
            nn.LayerNorm(16),
            nn.LeakyReLU(0.2),
            nn.Linear(16, in_features)
        )

    def forward(self, x):
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return reconstruction, latent

    def compute_reconstruction_error(self, x):
        rec, _ = self.forward(x)
        # Mean squared error per sample across feature dimension
        err = torch.mean((x - rec) ** 2, dim=-1)
        return err

# ─── MODEL 2: MULTI-CLASS THREAT CLASSIFIER ────────────────────────────────────

class IoTThreatClassifier(nn.Module):
    def __init__(self, in_features=9, num_classes=6):
        super().__init__()
        self.input_layer = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.BatchNorm1d(64),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.15)
        )
        self.hidden = nn.Sequential(
            nn.Linear(64, 64),
            nn.BatchNorm1d(64),
            nn.LeakyReLU(0.2),
            nn.Linear(64, 64)
        )
        self.head = nn.Sequential(
            nn.Linear(64, 32),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.15),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        h = self.input_layer(x)
        h = h + self.hidden(h) # residual connection
        logits = self.head(h)
        return logits

def train_and_evaluate():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_dir = os.path.join(base_dir, "source_code", "data")
    backend_dir = os.path.join(base_dir, "source_code", "backend")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(backend_dir, exist_ok=True)

    print("Generating 5,500 IoT Network Telemetry Dataset...")
    dataset = build_dataset(total_records=5500)
    print(f"Generated {len(dataset)} flow records across 6 IoT devices.")

    # Save to JSON (first 1,000 for inspection)
    json_path = os.path.join(data_dir, "iot_network_telemetry.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset[:1000], f, indent=2)

    # Save to CSV
    csv_path = os.path.join(data_dir, "iot_network_telemetry.csv")
    headers = ['flow_id', 'device_name', 'traffic_type', 'traffic_idx', 'is_anomaly'] + FEATURE_NAMES
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for item in dataset:
            writer.writerow([item['flow_id'], item['device_name'], item['traffic_type'], item['traffic_idx'], int(item['is_anomaly'])] + item['features'])
    print(f"Saved dataset to {csv_path} ({os.path.getsize(csv_path)} bytes)")

    # Prepare features and labels
    X_raw = np.array([item['features'] for item in dataset], dtype=np.float32)
    y_class = np.array([item['traffic_idx'] for item in dataset], dtype=np.int64)
    y_anomaly = np.array([int(item['is_anomaly']) for item in dataset], dtype=np.float32)

    # Compute Feature Scalers (mean and std)
    mean_vec = np.mean(X_raw, axis=0).astype(np.float32).tolist()
    std_vec = (np.std(X_raw, axis=0) + 1e-6).astype(np.float32).tolist()
    scalers = {'mean': mean_vec, 'std': std_vec, 'feature_names': FEATURE_NAMES}
    scalers_path = os.path.join(backend_dir, "iot_scalers.json")
    with open(scalers_path, "w", encoding="utf-8") as f:
        json.dump(scalers, f, indent=2)

    # Normalize X
    X_norm = ((X_raw - np.array(mean_vec, dtype=np.float32)) / np.array(std_vec, dtype=np.float32)).astype(np.float32)

    # Split train/test (80/20)
    n_train = int(len(X_norm) * 0.8)
    X_train, X_test = X_norm[:n_train], X_norm[n_train:]
    y_train, y_test = y_class[:n_train], y_class[n_train:]

    # Normal traffic only for Autoencoder baseline
    normal_mask_train = (y_train == 0)
    X_train_normal = X_train[normal_mask_train]

    # Train Model 1: Autoencoder
    print("\n--- Training Model 1: IoTAnomalyAutoencoder (Reconstruction Loss) ---")
    ae_model = IoTAnomalyAutoencoder(in_features=8, latent_dim=4)
    ae_optimizer = optim.AdamW(ae_model.parameters(), lr=0.005, weight_decay=1e-4)
    ae_criterion = nn.MSELoss()

    ae_train_ds = TensorDataset(torch.from_numpy(X_train_normal), torch.from_numpy(X_train_normal))
    ae_train_loader = DataLoader(ae_train_ds, batch_size=32, shuffle=True)

    ae_model.train()
    for epoch in range(1, 26):
        total_loss = 0.0
        for bx, by in ae_train_loader:
            ae_optimizer.zero_grad()
            rec, _ = ae_model(bx)
            loss = ae_criterion(rec, by)
            loss.backward()
            ae_optimizer.step()
            total_loss += loss.item()

        if epoch % 5 == 0 or epoch == 25:
            print(f"AE Epoch {epoch:02d}/25 - Reconstruction MSE Loss: {total_loss/len(ae_train_loader):.4f}")

    ae_weights_path = os.path.join(backend_dir, "iot_autoencoder_weights.pt")
    torch.save(ae_model.state_dict(), ae_weights_path)
    print(f"Saved Autoencoder weights to {ae_weights_path} ({os.path.getsize(ae_weights_path)} bytes)")

    # Compute reconstruction errors across test set
    ae_model.eval()
    with torch.no_grad():
        test_err = ae_model.compute_reconstruction_error(torch.from_numpy(X_test)).numpy()
        train_err = ae_model.compute_reconstruction_error(torch.from_numpy(X_train)).numpy()

    # Model 2: Threat Classifier (Augments 8 features with Autoencoder reconstruction error -> 9 features)
    print("\n--- Training Model 2: IoTThreatClassifier (Multi-Class Signature Classifier) ---")
    X_train_augmented = np.hstack([X_train, train_err.reshape(-1, 1)]).astype(np.float32)
    X_test_augmented = np.hstack([X_test, test_err.reshape(-1, 1)]).astype(np.float32)

    clf_train_ds = TensorDataset(torch.from_numpy(X_train_augmented), torch.from_numpy(y_train))
    clf_test_ds = TensorDataset(torch.from_numpy(X_test_augmented), torch.from_numpy(y_test))
    clf_train_loader = DataLoader(clf_train_ds, batch_size=64, shuffle=True)
    clf_test_loader = DataLoader(clf_test_ds, batch_size=64, shuffle=False)

    clf_model = IoTThreatClassifier(in_features=9, num_classes=6)
    clf_optimizer = optim.AdamW(clf_model.parameters(), lr=0.004, weight_decay=1e-4)
    clf_criterion = nn.CrossEntropyLoss()

    clf_model.train()
    for epoch in range(1, 26):
        total_loss = 0.0
        for bx, by in clf_train_loader:
            clf_optimizer.zero_grad()
            logits = clf_model(bx)
            loss = clf_criterion(logits, by)
            loss.backward()
            clf_optimizer.step()
            total_loss += loss.item()

        if epoch % 5 == 0 or epoch == 25:
            clf_model.eval()
            correct, total = 0, 0
            with torch.no_grad():
                for bx, by in clf_test_loader:
                    preds = clf_model(bx).argmax(dim=-1)
                    correct += (preds == by).sum().item()
                    total += by.size(0)
            acc = (correct / total) * 100
            print(f"Classifier Epoch {epoch:02d}/25 - Loss: {total_loss/len(clf_train_loader):.4f} - Test Accuracy: {acc:.2f}%")
            clf_model.train()

    clf_weights_path = os.path.join(backend_dir, "iot_classifier_weights.pt")
    torch.save(clf_model.state_dict(), clf_weights_path)
    print(f"Saved Threat Classifier weights to {clf_weights_path} ({os.path.getsize(clf_weights_path)} bytes)")

    # Save detailed metadata
    metadata = {
        'project_id': 'PROJECT-030',
        'domain': 'IoT Telematics & Edge Anomaly Detection',
        'classes': CLASSES,
        'class_count': len(CLASSES),
        'devices': list(DEVICES.keys()),
        'device_count': len(DEVICES),
        'dataset_volume': len(dataset),
        'features': FEATURE_NAMES,
        'feature_count': len(FEATURE_NAMES),
        'models': {
            'IoTAnomalyAutoencoder': {
                'architecture': 'Deep Bottleneck Autoencoder (8 -> 16 -> 8 -> 4 -> 8 -> 16 -> 8)',
                'weights_file': 'iot_autoencoder_weights.pt',
                'file_size_bytes': os.path.getsize(ae_weights_path),
                'anomaly_threshold': 0.35,
                'parameters_count': sum(p.numel() for p in ae_model.parameters())
            },
            'IoTThreatClassifier': {
                'architecture': 'Deep Residual Threat Classifier (9 -> 64 -> 64 -> 32 -> 6)',
                'weights_file': 'iot_classifier_weights.pt',
                'file_size_bytes': os.path.getsize(clf_weights_path),
                'test_accuracy_pct': round(acc, 2),
                'parameters_count': sum(p.numel() for p in clf_model.parameters())
            }
        }
    }

    metadata_path = os.path.join(backend_dir, "model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to {metadata_path}")
    print("\nProject 30 dataset generation and model training completed successfully!")

if __name__ == '__main__':
    train_and_evaluate()
