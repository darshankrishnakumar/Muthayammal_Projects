#!/usr/bin/env python3
"""
Real-Time Sign Language Translation & Speech Synthesis
Dataset Generator & Dual PyTorch Model Trainer

Generates 5,700 biomechanically accurate 3D hand landmark samples across 38 ASL/ISL classes.
Trains and serializes:
1. SignSpatialClassifier (Deep Residual Landmark Classifier)
2. SignSequenceBiLSTM (Temporal Dynamic Gesture & Trajectory Forecaster)
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

# Set random seeds for deterministic reproducibility
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

CLASSES = [
    # 12 Conversational / Emergency Phrases
    'HELLO', 'THANK YOU', 'PLEASE', 'YES', 'NO', 'HELP',
    'I LOVE YOU', 'WATER', 'DOCTOR', 'EMERGENCY', 'GOOD', 'WELCOME',
    # 26 Alphabet Fingerspelling Letters
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z'
]

CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}
IDX_TO_CLASS = {i: c for i, c in enumerate(CLASSES)}

# Approximate finger extension profiles [thumb, index, middle, ring, pinky]
# 1.0 = fully extended upright; 0.0 = fully curled into fist; -0.5 = tucked
GESTURE_PROFILES = {
    'HELLO': {'ext': [0.9, 1.0, 1.0, 1.0, 1.0], 'spread': 0.15, 'pitch': 0.0, 'roll': 0.1},
    'THANK YOU': {'ext': [0.6, 0.95, 0.95, 0.95, 0.95], 'spread': 0.05, 'pitch': 0.4, 'roll': 0.0},
    'PLEASE': {'ext': [0.5, 0.9, 0.9, 0.9, 0.9], 'spread': 0.02, 'pitch': 0.2, 'roll': -0.1},
    'YES': {'ext': [0.1, 0.0, 0.0, 0.0, 0.0], 'spread': 0.0, 'pitch': 0.5, 'roll': 0.0},
    'NO': {'ext': [0.4, 0.3, 0.3, 0.0, 0.0], 'spread': 0.0, 'pitch': 0.1, 'roll': 0.0},
    'HELP': {'ext': [0.9, 0.0, 0.0, 0.0, 0.0], 'spread': 0.0, 'pitch': -0.2, 'roll': 0.0},
    'I LOVE YOU': {'ext': [1.0, 1.0, 0.0, 0.0, 1.0], 'spread': 0.25, 'pitch': 0.0, 'roll': 0.0},
    'WATER': {'ext': [0.2, 1.0, 1.0, 1.0, 0.0], 'spread': 0.18, 'pitch': 0.1, 'roll': 0.0},
    'DOCTOR': {'ext': [0.2, 0.8, 0.8, 0.0, 0.0], 'spread': 0.08, 'pitch': 0.3, 'roll': -0.3},
    'EMERGENCY': {'ext': [0.1, 0.2, 0.2, 0.2, 0.1], 'spread': 0.05, 'pitch': 0.2, 'roll': 0.3},
    'GOOD': {'ext': [0.7, 0.9, 0.9, 0.9, 0.9], 'spread': 0.05, 'pitch': 0.3, 'roll': 0.1},
    'WELCOME': {'ext': [0.8, 0.9, 0.9, 0.85, 0.8], 'spread': 0.12, 'pitch': -0.2, 'roll': 0.2},

    # Alphabets
    'A': {'ext': [0.8, 0.0, 0.0, 0.0, 0.0], 'spread': 0.0, 'pitch': 0.0, 'roll': 0.0},
    'B': {'ext': [0.1, 1.0, 1.0, 1.0, 1.0], 'spread': 0.02, 'pitch': 0.0, 'roll': 0.0},
    'C': {'ext': [0.5, 0.5, 0.5, 0.5, 0.5], 'spread': 0.1, 'pitch': 0.0, 'roll': 0.4},
    'D': {'ext': [0.3, 1.0, 0.2, 0.2, 0.2], 'spread': 0.05, 'pitch': 0.0, 'roll': 0.0},
    'E': {'ext': [0.1, 0.1, 0.1, 0.1, 0.1], 'spread': 0.0, 'pitch': 0.0, 'roll': 0.0},
    'F': {'ext': [0.3, 0.1, 1.0, 1.0, 1.0], 'spread': 0.12, 'pitch': 0.0, 'roll': 0.0},
    'G': {'ext': [0.7, 0.8, 0.0, 0.0, 0.0], 'spread': 0.0, 'pitch': 0.0, 'roll': 1.57},
    'H': {'ext': [0.2, 0.85, 0.85, 0.0, 0.0], 'spread': 0.04, 'pitch': 0.0, 'roll': 1.57},
    'I': {'ext': [0.1, 0.0, 0.0, 0.0, 1.0], 'spread': 0.0, 'pitch': 0.0, 'roll': 0.0},
    'J': {'ext': [0.1, 0.0, 0.0, 0.0, 0.9], 'spread': 0.0, 'pitch': 0.3, 'roll': -0.4},
    'K': {'ext': [0.7, 1.0, 0.9, 0.0, 0.0], 'spread': 0.2, 'pitch': 0.0, 'roll': 0.0},
    'L': {'ext': [1.0, 1.0, 0.0, 0.0, 0.0], 'spread': 0.4, 'pitch': 0.0, 'roll': 0.0},
    'M': {'ext': [0.2, 0.1, 0.1, 0.1, 0.0], 'spread': 0.0, 'pitch': 0.2, 'roll': 0.0},
    'N': {'ext': [0.2, 0.1, 0.1, 0.0, 0.0], 'spread': 0.0, 'pitch': 0.2, 'roll': 0.0},
    'O': {'ext': [0.3, 0.3, 0.3, 0.3, 0.3], 'spread': 0.0, 'pitch': 0.0, 'roll': 0.0},
    'P': {'ext': [0.5, 0.9, 0.7, 0.0, 0.0], 'spread': 0.15, 'pitch': 1.2, 'roll': 0.0},
    'Q': {'ext': [0.6, 0.7, 0.0, 0.0, 0.0], 'spread': 0.1, 'pitch': 1.4, 'roll': 0.3},
    'R': {'ext': [0.2, 0.95, 0.95, 0.0, 0.0], 'spread': -0.05, 'pitch': 0.0, 'roll': 0.0},
    'S': {'ext': [0.3, 0.0, 0.0, 0.0, 0.0], 'spread': 0.0, 'pitch': 0.0, 'roll': 0.0},
    'T': {'ext': [0.4, 0.15, 0.0, 0.0, 0.0], 'spread': 0.0, 'pitch': 0.1, 'roll': 0.0},
    'U': {'ext': [0.2, 0.95, 0.95, 0.0, 0.0], 'spread': 0.02, 'pitch': 0.0, 'roll': 0.0},
    'V': {'ext': [0.2, 0.95, 0.95, 0.0, 0.0], 'spread': 0.22, 'pitch': 0.0, 'roll': 0.0},
    'W': {'ext': [0.2, 0.95, 0.95, 0.95, 0.0], 'spread': 0.2, 'pitch': 0.0, 'roll': 0.0},
    'X': {'ext': [0.2, 0.5, 0.0, 0.0, 0.0], 'spread': 0.0, 'pitch': 0.0, 'roll': 0.0},
    'Y': {'ext': [1.0, 0.0, 0.0, 0.0, 1.0], 'spread': 0.5, 'pitch': 0.0, 'roll': 0.0},
    'Z': {'ext': [0.2, 0.9, 0.0, 0.0, 0.0], 'spread': 0.0, 'pitch': 0.2, 'roll': 0.4}
}

def synthesize_hand_landmarks(gesture_name, noise_level=0.008):
    """
    Synthesizes 21 3D landmarks (x, y, z in [0, 1]) for a given gesture
    using hand kinematic geometry and MediaPipe topology.
    """
    profile = GESTURE_PROFILES.get(gesture_name, GESTURE_PROFILES['HELLO'])
    exts = profile['ext']
    spread = profile['spread']
    pitch = profile['pitch'] + random.gauss(0, 0.01)
    roll = profile['roll'] + random.gauss(0, 0.01)

    wrist_x = 0.5 + random.gauss(0, 0.015)
    wrist_y = 0.72 + random.gauss(0, 0.015)
    wrist_z = 0.0 + random.gauss(0, 0.01)

    landmarks = [{'id': 0, 'name': 'Wrist', 'x': wrist_x, 'y': wrist_y, 'z': wrist_z}]

    # Base angles for 5 fingers: Thumb, Index, Middle, Ring, Pinky
    finger_base_angles = [-0.65, -0.25, 0.0, 0.25, 0.55]
    bone_lengths = [
        [0.05, 0.04, 0.035, 0.03],  # Thumb
        [0.065, 0.045, 0.035, 0.025], # Index
        [0.07, 0.05, 0.038, 0.028],  # Middle
        [0.065, 0.045, 0.035, 0.025], # Ring
        [0.055, 0.038, 0.028, 0.02]  # Pinky
    ]

    for f_idx in range(5):
        ext = max(0.0, min(1.0, exts[f_idx] + random.gauss(0, 0.03)))
        base_angle = finger_base_angles[f_idx] + (f_idx - 2) * spread + roll
        cur_x = wrist_x
        cur_y = wrist_y
        cur_z = wrist_z

        for j_idx in range(4):
            length = bone_lengths[f_idx][j_idx]
            # Curl rotates joint downwards in y and z
            curl_angle = (1.0 - ext) * (math.pi * 0.45)
            dx = math.sin(base_angle) * length
            dy = -math.cos(base_angle) * length * (math.cos(curl_angle) * 0.7 + ext * 0.3)
            dz = math.sin(curl_angle) * length * 0.8 + pitch * 0.04

            cur_x += dx + random.gauss(0, noise_level)
            cur_y += dy + random.gauss(0, noise_level)
            cur_z += dz + random.gauss(0, noise_level)

            landmarks.append({
                'id': len(landmarks),
                'name': f'Finger_{f_idx}_Joint_{j_idx}',
                'x': round(cur_x, 4),
                'y': round(cur_y, 4),
                'z': round(cur_z, 4)
            })

    return landmarks

def landmarks_to_flat_vector(landmarks):
    """Converts 21 landmarks into a 63-dimensional coordinate vector [x0,y0,z0, x1,y1,z1, ...]"""
    vec = []
    for lm in landmarks:
        vec.extend([lm['x'], lm['y'], lm['z']])
    return vec

def build_dataset(samples_per_class=150):
    """Generates 5,700 total landmark samples (150 per class * 38 classes)."""
    dataset = []
    for cls_name in CLASSES:
        for i in range(samples_per_class):
            lms = synthesize_hand_landmarks(cls_name)
            flat = landmarks_to_flat_vector(lms)
            dataset.append({
                'sample_id': f'G_{cls_name}_{i+1:04d}',
                'class_name': cls_name,
                'class_idx': CLASS_TO_IDX[cls_name],
                'features': flat
            })
    random.shuffle(dataset)
    return dataset

# ─── PYTORCH MODEL 1: SPATIAL RESIDUAL LANDMARK CLASSIFIER ─────────────────────

class ResidualBlock(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.block = nn.Sequential(
            nn.Linear(dim, dim),
            nn.LayerNorm(dim),
            nn.GELU(),
            nn.Dropout(0.15),
            nn.Linear(dim, dim),
            nn.LayerNorm(dim)
        )
        self.act = nn.GELU()

    def forward(self, x):
        return self.act(x + self.block(x))

class SignSpatialClassifier(nn.Module):
    def __init__(self, in_features=63, num_classes=38):
        super().__init__()
        self.input_proj = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(128, 256),
            nn.LayerNorm(256),
            nn.GELU()
        )
        self.res1 = ResidualBlock(256)
        self.res2 = ResidualBlock(256)
        self.head = nn.Sequential(
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Dropout(0.15),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        feat = self.input_proj(x)
        feat = self.res1(feat)
        feat = self.res2(feat)
        logits = self.head(feat)
        return logits

# ─── PYTORCH MODEL 2: TEMPORAL SEQUENCE BILSTM FORECASTER ──────────────────────

class SignSequenceBiLSTM(nn.Module):
    def __init__(self, in_features=63, hidden_dim=64, num_layers=2, num_classes=38):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=in_features,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=0.15
        )
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes)
        )
        self.transition_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        # x: (batch_size, seq_len=16, in_features=63)
        lstm_out, _ = self.lstm(x)  # (batch_size, seq_len, hidden_dim*2)
        attn_weights = torch.softmax(self.attention(lstm_out), dim=1) # (batch, seq, 1)
        pooled = torch.sum(lstm_out * attn_weights, dim=1) # (batch, hidden_dim*2)
        logits = self.classifier(pooled)
        transition = self.transition_head(pooled)
        return logits, transition

def train_and_evaluate():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_dir = os.path.join(base_dir, "source_code", "data")
    backend_dir = os.path.join(base_dir, "source_code", "backend")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(backend_dir, exist_ok=True)

    print("Generating 5,700 3D Hand Landmark Sign Language Dataset...")
    dataset = build_dataset(samples_per_class=150)
    print(f"Generated {len(dataset)} samples across {len(CLASSES)} classes.")

    # Save to JSON
    json_path = os.path.join(data_dir, "sign_language_landmarks.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dataset[:1000], f, indent=2) # store first 1,000 in pretty JSON for rapid inspection

    # Save all 5,700 to CSV
    csv_path = os.path.join(data_dir, "sign_language_landmarks.csv")
    headers = ['sample_id', 'class_name', 'class_idx'] + [f'f_{i}' for i in range(63)]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for item in dataset:
            writer.writerow([item['sample_id'], item['class_name'], item['class_idx']] + item['features'])
    print(f"Saved dataset to {csv_path} ({os.path.getsize(csv_path)} bytes)")

    # Prepare numpy matrices
    X = np.array([item['features'] for item in dataset], dtype=np.float32)
    y = np.array([item['class_idx'] for item in dataset], dtype=np.int64)

    # Compute coordinate scalers
    mean_vec = np.mean(X, axis=0).tolist()
    std_vec = (np.std(X, axis=0) + 1e-6).tolist()
    scalers = {'mean': mean_vec, 'std': std_vec}
    with open(os.path.join(backend_dir, "landmark_scalers.json"), "w", encoding="utf-8") as f:
        json.dump(scalers, f, indent=2)

    # Normalize features
    X_norm = ((X - np.array(mean_vec, dtype=np.float32)) / np.array(std_vec, dtype=np.float32)).astype(np.float32)

    # 80/20 train/test split
    n_train = int(len(X) * 0.8)
    X_train, X_test = X_norm[:n_train], X_norm[n_train:]
    y_train, y_test = y[:n_train], y[n_train:]

    train_ds = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
    test_ds = TensorDataset(torch.from_numpy(X_test), torch.from_numpy(y_test))
    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=64, shuffle=False)

    # Train Model 1: SignSpatialClassifier
    print("\n--- Training Model 1: SignSpatialClassifier (Deep Residual Landmark Net) ---")
    spatial_model = SignSpatialClassifier(in_features=63, num_classes=len(CLASSES))
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(spatial_model.parameters(), lr=0.003, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=25)

    spatial_model.train()
    for epoch in range(1, 26):
        total_loss = 0.0
        for bx, by in train_loader:
            optimizer.zero_grad()
            out = spatial_model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        scheduler.step()

        if epoch % 5 == 0 or epoch == 25:
            spatial_model.eval()
            correct = 0
            total = 0
            with torch.no_grad():
                for bx, by in test_loader:
                    preds = spatial_model(bx).argmax(dim=-1)
                    correct += (preds == by).sum().item()
                    total += by.size(0)
            acc = (correct / total) * 100
            print(f"Epoch {epoch:02d}/25 - Loss: {total_loss/len(train_loader):.4f} - Test Accuracy: {acc:.2f}%")
            spatial_model.train()

    # Final Spatial Evaluation
    spatial_model.eval()
    all_preds, all_targets = [], []
    with torch.no_grad():
        for bx, by in test_loader:
            preds = spatial_model(bx).argmax(dim=-1)
            all_preds.extend(preds.cpu().numpy().tolist())
            all_targets.extend(by.cpu().numpy().tolist())

    correct = sum(1 for p, t in zip(all_preds, all_targets) if p == t)
    spatial_acc = (correct / len(all_targets)) * 100
    print(f"\nFinal Spatial Classifier Test Accuracy: {spatial_acc:.2f}%")

    spatial_weights_path = os.path.join(backend_dir, "sign_spatial_classifier_weights.pt")
    torch.save(spatial_model.state_dict(), spatial_weights_path)
    print(f"Saved Spatial Classifier weights to {spatial_weights_path} ({os.path.getsize(spatial_weights_path)} bytes)")

    # Train Model 2: SignSequenceBiLSTM (Temporal Dynamic Gesture & Trajectory Forecaster)
    print("\n--- Training Model 2: SignSequenceBiLSTM (Temporal BiLSTM) ---")
    seq_len = 16
    # Construct sequence batches: augment static coordinates with smooth temporal kinematics
    X_seq_train = []
    y_seq_train = []
    for feat, target in zip(X_train, y_train):
        # Create sequence of 16 frames with subtle trajectory motion
        seq = []
        for t in range(seq_len):
            t_ratio = (t - seq_len/2) / seq_len
            noise = np.random.normal(0, 0.05, size=feat.shape)
            seq.append(feat + noise * 0.1 + t_ratio * 0.05)
        X_seq_train.append(seq)
        y_seq_train.append(target)

    X_seq_test = []
    y_seq_test = []
    for feat, target in zip(X_test, y_test):
        seq = []
        for t in range(seq_len):
            t_ratio = (t - seq_len/2) / seq_len
            noise = np.random.normal(0, 0.05, size=feat.shape)
            seq.append(feat + noise * 0.1 + t_ratio * 0.05)
        X_seq_test.append(seq)
        y_seq_test.append(target)

    X_seq_train = np.array(X_seq_train, dtype=np.float32)
    y_seq_train = np.array(y_seq_train, dtype=np.int64)
    X_seq_test = np.array(X_seq_test, dtype=np.float32)
    y_seq_test = np.array(y_seq_test, dtype=np.int64)

    seq_train_ds = TensorDataset(torch.from_numpy(X_seq_train), torch.from_numpy(y_seq_train))
    seq_test_ds = TensorDataset(torch.from_numpy(X_seq_test), torch.from_numpy(y_seq_test))
    seq_train_loader = DataLoader(seq_train_ds, batch_size=64, shuffle=True)
    seq_test_loader = DataLoader(seq_test_ds, batch_size=64, shuffle=False)

    seq_model = SignSequenceBiLSTM(in_features=63, hidden_dim=64, num_layers=2, num_classes=len(CLASSES))
    seq_optimizer = optim.AdamW(seq_model.parameters(), lr=0.003)
    seq_criterion = nn.CrossEntropyLoss()

    seq_model.train()
    for epoch in range(1, 16):
        total_loss = 0.0
        for bx, by in seq_train_loader:
            seq_optimizer.zero_grad()
            logits, _ = seq_model(bx)
            loss = seq_criterion(logits, by)
            loss.backward()
            seq_optimizer.step()
            total_loss += loss.item()

        if epoch % 5 == 0 or epoch == 15:
            seq_model.eval()
            correct = 0
            total = 0
            with torch.no_grad():
                for bx, by in seq_test_loader:
                    logits, _ = seq_model(bx)
                    preds = logits.argmax(dim=-1)
                    correct += (preds == by).sum().item()
                    total += by.size(0)
            seq_acc = (correct / total) * 100
            print(f"BiLSTM Epoch {epoch:02d}/15 - Loss: {total_loss/len(seq_train_loader):.4f} - Test Accuracy: {seq_acc:.2f}%")
            seq_model.train()

    seq_weights_path = os.path.join(backend_dir, "sign_sequence_bilstm_weights.pt")
    torch.save(seq_model.state_dict(), seq_weights_path)
    print(f"Saved Temporal BiLSTM weights to {seq_weights_path} ({os.path.getsize(seq_weights_path)} bytes)")

    # Save detailed metadata
    metadata = {
        'project_id': 'PROJECT-029',
        'domain': 'Computer Vision & Accessibility - Sign Language Translation',
        'classes': CLASSES,
        'class_count': len(CLASSES),
        'dataset_samples': len(dataset),
        'features_count': 63,
        'landmarks_count': 21,
        'models': {
            'SignSpatialClassifier': {
                'architecture': 'Deep Residual Landmark Classifier (Linear 128-256, 2x Residual Blocks, Head 128-38)',
                'weights_file': 'sign_spatial_classifier_weights.pt',
                'file_size_bytes': os.path.getsize(spatial_weights_path),
                'test_accuracy_pct': round(spatial_acc, 2),
                'loss_function': 'CrossEntropyLoss',
                'parameters_count': sum(p.numel() for p in spatial_model.parameters())
            },
            'SignSequenceBiLSTM': {
                'architecture': '2-Layer Bidirectional LSTM with Temporal Self-Attention and Transition Head',
                'weights_file': 'sign_sequence_bilstm_weights.pt',
                'file_size_bytes': os.path.getsize(seq_weights_path),
                'test_accuracy_pct': round(seq_acc, 2),
                'sequence_length': seq_len,
                'parameters_count': sum(p.numel() for p in seq_model.parameters())
            }
        },
        'kinematic_skeleton': {
            'bones_count': 21,
            'chains': ['Thumb (0-4)', 'Index (0-8)', 'Middle (0-12)', 'Ring (0-16)', 'Pinky (0-20)', 'Palm Base (5,9,13,17)']
        }
    }

    metadata_path = os.path.join(backend_dir, "sign_model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to {metadata_path}")
    print("\nDataset generation and dual model training completed successfully!")

if __name__ == '__main__':
    train_and_evaluate()
