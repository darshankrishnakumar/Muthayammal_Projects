import os
import json
import math
import random
import csv
from datetime import datetime, timezone
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# Reproducibility seeds
np.random.seed(42)
random.seed(42)
torch.manual_seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(DATA_DIR, "..", "backend"))
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKEND_DIR, exist_ok=True)

EMOTIONS = ['happy', 'sad', 'angry', 'fear', 'neutral', 'surprise', 'disgust']
EMOTION_TO_IDX = {e: i for i, e in enumerate(EMOTIONS)}

EMOTION_PRIORS = {
    'happy': {'valence': 0.78, 'arousal': 0.62, 'pitch_f0': 240.0, 'pitch_std': 32.0, 'energy': 0.68, 'centroid': 2400.0, 'zcr': 0.14, 'rolloff': 4800.0, 'jitter': 0.8, 'shimmer': 2.4},
    'sad': {'valence': -0.72, 'arousal': -0.55, 'pitch_f0': 140.0, 'pitch_std': 18.0, 'energy': 0.28, 'centroid': 1500.0, 'zcr': 0.07, 'rolloff': 3200.0, 'jitter': 1.6, 'shimmer': 4.2},
    'angry': {'valence': -0.81, 'arousal': 0.88, 'pitch_f0': 260.0, 'pitch_std': 45.0, 'energy': 0.85, 'centroid': 2800.0, 'zcr': 0.18, 'rolloff': 5600.0, 'jitter': 1.2, 'shimmer': 3.6},
    'fear': {'valence': -0.65, 'arousal': 0.74, 'pitch_f0': 285.0, 'pitch_std': 48.0, 'energy': 0.72, 'centroid': 3100.0, 'zcr': 0.20, 'rolloff': 6200.0, 'jitter': 1.8, 'shimmer': 4.8},
    'neutral': {'valence': 0.05, 'arousal': 0.02, 'pitch_f0': 175.0, 'pitch_std': 15.0, 'energy': 0.45, 'centroid': 1750.0, 'zcr': 0.09, 'rolloff': 3800.0, 'jitter': 0.5, 'shimmer': 1.9},
    'surprise': {'valence': 0.45, 'arousal': 0.79, 'pitch_f0': 270.0, 'pitch_std': 40.0, 'energy': 0.75, 'centroid': 2600.0, 'zcr': 0.16, 'rolloff': 5200.0, 'jitter': 1.0, 'shimmer': 2.9},
    'disgust': {'valence': -0.76, 'arousal': 0.42, 'pitch_f0': 190.0, 'pitch_std': 24.0, 'energy': 0.55, 'centroid': 1900.0, 'zcr': 0.11, 'rolloff': 4100.0, 'jitter': 1.4, 'shimmer': 3.8}
}

LANGUAGES = ['English', 'Hindi', 'Tamil', 'Spanish', 'French', 'German', 'Mandarin', 'Japanese']

def generate_ser_dataset(n_samples=5000):
    print(f"Generating {n_samples} multilingual speech emotion samples across 8 languages...")
    data_rows = []
    X = np.zeros((n_samples, 40), dtype=np.float32)
    y_class = np.zeros(n_samples, dtype=np.int64)
    y_va = np.zeros((n_samples, 2), dtype=np.float32)

    for i in range(n_samples):
        emotion = random.choice(EMOTIONS)
        lang = random.choice(LANGUAGES)
        prior = EMOTION_PRIORS[emotion]

        # Generate realistic MFCC coefficients (13 means + 13 stds)
        mfcc_means = [0.0] * 13
        mfcc_means[0] = round(float(np.random.normal(-240.0 + (prior['energy'] * 80.0), 30.0)), 2)
        for m in range(1, 13):
            shift = (prior['valence'] * 5.0) if m % 2 == 1 else (prior['arousal'] * 6.0)
            mfcc_means[m] = round(float(np.random.normal(shift + (12 - m) * 1.5, 8.0)), 2)

        mfcc_stds = [round(float(abs(np.random.normal(6.0 + (prior['arousal'] * 3.0), 1.5))), 2) for _ in range(13)]

        # Prosodic & Spectral Features
        pitch_f0 = round(float(np.random.normal(prior['pitch_f0'], prior['pitch_std'] * 0.5)), 1)
        pitch_std = round(float(abs(np.random.normal(prior['pitch_std'], 5.0))), 1)
        energy_db = round(float(np.clip(np.random.normal(prior['energy'], 0.05), 0.1, 1.0)), 3)
        centroid = round(float(np.random.normal(prior['centroid'], 150.0)), 1)
        rolloff = round(float(np.random.normal(prior['rolloff'], 250.0)), 1)
        zcr = round(float(np.clip(np.random.normal(prior['zcr'], 0.02), 0.02, 0.40)), 3)
        jitter = round(float(np.clip(np.random.normal(prior['jitter'], 0.2), 0.2, 3.5)), 2)
        shimmer = round(float(np.clip(np.random.normal(prior['shimmer'], 0.4), 0.8, 8.0)), 2)

        # Chroma energy across 4 sub-bands
        chroma = [
            round(float(np.clip(np.random.normal(0.4 + prior['valence']*0.2, 0.08), 0.05, 0.95)), 3),
            round(float(np.clip(np.random.normal(0.5 + prior['arousal']*0.2, 0.08), 0.05, 0.95)), 3),
            round(float(np.clip(np.random.normal(0.35 + prior['energy']*0.25, 0.08), 0.05, 0.95)), 3),
            round(float(np.clip(np.random.normal(0.45 - prior['valence']*0.15, 0.08), 0.05, 0.95)), 3)
        ]

        # Spectral contrast (2 bands)
        contrast = [
            round(float(np.random.normal(18.0 + prior['arousal'] * 5.0, 3.0)), 2),
            round(float(np.random.normal(14.0 + prior['energy'] * 4.0, 2.5)), 2)
        ]

        # Russell Circumplex Valence & Arousal with slight individual variance
        valence = round(float(np.clip(np.random.normal(prior['valence'], 0.06), -1.0, 1.0)), 2)
        arousal = round(float(np.clip(np.random.normal(prior['arousal'], 0.06), -1.0, 1.0)), 2)
        duration = round(float(np.random.uniform(2.2, 6.8)), 1)

        # Build 40-dim feature vector
        feat_vector = mfcc_means + mfcc_stds + [
            pitch_f0, pitch_std, energy_db, centroid, rolloff, zcr, jitter, shimmer
        ] + chroma + contrast

        X[i] = np.array(feat_vector, dtype=np.float32)
        y_class[i] = EMOTION_TO_IDX[emotion]
        y_va[i] = np.array([valence, arousal], dtype=np.float32)

        row = {
            'sample_id': f"SER-{i+1:05d}",
            'language': lang,
            'duration_seconds': duration,
            'emotion': emotion,
            'valence': valence,
            'arousal': arousal,
            'pitch_f0_hz': pitch_f0,
            'pitch_std_hz': pitch_std,
            'rms_energy_db': energy_db,
            'spectral_centroid_hz': centroid,
            'spectral_rolloff_hz': rolloff,
            'zero_crossing_rate': zcr,
            'jitter_local_pct': jitter,
            'shimmer_local_pct': shimmer,
            'mfcc_means_json': json.dumps(mfcc_means),
            'mfcc_stds_json': json.dumps(mfcc_stds)
        }
        data_rows.append(row)

    # Save to CSV
    csv_path = os.path.join(DATA_DIR, "speech_emotions_dataset.csv")
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = list(data_rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_rows)
    print(f"Saved {n_samples} audio samples to {csv_path}")

    return X, y_class, y_va

# ─── NEURAL NETWORK ARCHITECTURE: 1D-CNN + BI-LSTM WITH ATTENTION ───

class SelfAttentionPooling(nn.Module):
    def __init__(self, hidden_dim):
        super(SelfAttentionPooling, self).__init__()
        self.attn = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        # x: (batch_size, seq_len, hidden_dim)
        scores = self.attn(x) # (batch_size, seq_len, 1)
        weights = torch.softmax(scores, dim=1) # (batch_size, seq_len, 1)
        context = torch.sum(x * weights, dim=1) # (batch_size, hidden_dim)
        return context, weights

class MultilingualSERNet(nn.Module):
    def __init__(self, in_features=40, num_classes=7):
        super(MultilingualSERNet, self).__init__()
        # 1D-CNN Feature Refinement
        self.conv1 = nn.Conv1d(1, 64, kernel_size=5, padding=2)
        self.bn1 = nn.BatchNorm1d(64)
        self.relu = nn.ReLU()
        self.pool1 = nn.MaxPool1d(2) # 40 -> 20
        self.drop1 = nn.Dropout(0.2)

        self.conv2 = nn.Conv1d(64, 128, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(128)
        self.pool2 = nn.MaxPool1d(2) # 20 -> 10
        self.drop2 = nn.Dropout(0.2)

        # Bidirectional LSTM over temporal audio feature map (seq_len=10, in_features=128)
        self.bilstm = nn.LSTM(input_size=128, hidden_size=64, num_layers=2, batch_first=True, bidirectional=True)
        self.attention = SelfAttentionPooling(hidden_dim=128)

        # Shared Latent Representation
        self.fc_shared = nn.Linear(128, 64)
        self.drop_shared = nn.Dropout(0.25)

        # Multi-Task Classification & Regression Heads
        self.classifier = nn.Linear(64, num_classes)
        self.va_regressor = nn.Linear(64, 2)
        self.tanh = nn.Tanh()

    def forward(self, x):
        # x shape: (B, 40) -> reshape to (B, 1, 40)
        x = x.unsqueeze(1)
        h = self.drop1(self.pool1(self.relu(self.bn1(self.conv1(x)))))
        h = self.drop2(self.pool2(self.relu(self.bn2(self.conv2(h)))))

        # Permute for LSTM: (B, Channels, SeqLen) -> (B, SeqLen, Channels)
        h = h.permute(0, 2, 1) # (B, 10, 128)
        lstm_out, _ = self.bilstm(h) # (B, 10, 128)
        context, _ = self.attention(lstm_out) # (B, 128)

        feat = self.drop_shared(self.relu(self.fc_shared(context))) # (B, 64)
        logits = self.classifier(feat) # (B, 7)
        va = self.tanh(self.va_regressor(feat)) # (B, 2) in [-1, 1]
        return logits, va, feat

# ─── TRAINING PIPELINE ───

def train_and_evaluate():
    X, y_class, y_va = generate_ser_dataset(n_samples=5000)

    # Feature Standardization
    feat_mean = np.mean(X, axis=0)
    feat_std = np.std(X, axis=0) + 1e-6
    X_norm = (X - feat_mean) / feat_std

    # Train / Val / Test split (70% / 15% / 15%)
    N = len(X)
    indices = np.arange(N)
    np.random.shuffle(indices)

    train_idx = indices[: int(0.70 * N)]
    val_idx = indices[int(0.70 * N): int(0.85 * N)]
    test_idx = indices[int(0.85 * N):]

    x_train = torch.FloatTensor(X_norm[train_idx])
    y_class_train = torch.LongTensor(y_class[train_idx])
    y_va_train = torch.FloatTensor(y_va[train_idx])

    x_val = torch.FloatTensor(X_norm[val_idx])
    y_class_val = torch.LongTensor(y_class[val_idx])
    y_va_val = torch.FloatTensor(y_va[val_idx])

    x_test = torch.FloatTensor(X_norm[test_idx])
    y_class_test = torch.LongTensor(y_class[test_idx])
    y_va_test = torch.FloatTensor(y_va[test_idx])

    model = MultilingualSERNet(in_features=40, num_classes=7)
    criterion_cls = nn.CrossEntropyLoss()
    criterion_reg = nn.MSELoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.003, weight_decay=1e-4)

    batch_size = 128
    num_epochs = 35
    num_batches = len(train_idx) // batch_size

    print(f"Training Deep Multilingual SERNet (1D-CNN + BiLSTM + Attention) for {num_epochs} epochs...")
    model.train()
    for epoch in range(1, num_epochs + 1):
        perm = torch.randperm(len(train_idx))
        epoch_loss = 0.0
        for b in range(num_batches):
            b_idx = perm[b * batch_size : (b + 1) * batch_size]
            bx = x_train[b_idx]
            by_cls = y_class_train[b_idx]
            by_va = y_va_train[b_idx]

            optimizer.zero_grad()
            logits, va_pred, _ = model(bx)
            loss_cls = criterion_cls(logits, by_cls)
            loss_reg = criterion_reg(va_pred, by_va)
            total_loss = loss_cls + 0.5 * loss_reg
            total_loss.backward()
            optimizer.step()
            epoch_loss += total_loss.item()

        if epoch % 10 == 0 or epoch == num_epochs:
            model.eval()
            with torch.no_grad():
                val_logits, val_va, _ = model(x_val)
                val_preds = torch.argmax(val_logits, dim=1)
                val_acc = (val_preds == y_class_val).float().mean().item()
                val_mse = criterion_reg(val_va, y_va_val).item()
                print(f"Epoch {epoch:02d} | Train Loss: {epoch_loss/num_batches:.4f} | Val Accuracy: {val_acc*100:.2f}% | Val VA MSE: {val_mse:.4f}")
            model.train()

    # Final Evaluation on Test Set
    model.eval()
    with torch.no_grad():
        test_logits, test_va, test_feats = model(x_test)
        test_preds = torch.argmax(test_logits, dim=1).numpy()
        true_labels = y_class[test_idx]
        test_acc = float(np.mean(test_preds == true_labels))

        # Precision, Recall, F1 across 7 emotion classes
        precision_list, recall_list, f1_list = [], [], []
        for c in range(7):
            tp = np.sum((test_preds == c) & (true_labels == c))
            fp = np.sum((test_preds == c) & (true_labels != c))
            fn = np.sum((test_preds != c) & (true_labels == c))
            p = tp / max(1, tp + fp)
            r = tp / max(1, tp + fn)
            f1 = 2 * p * r / max(1e-6, p + r)
            precision_list.append(p)
            recall_list.append(r)
            f1_list.append(f1)

        macro_prec = float(np.mean(precision_list))
        macro_rec = float(np.mean(recall_list))
        macro_f1 = float(np.mean(f1_list))
        test_mse = float(criterion_reg(test_va, y_va_test).item())

        print("\n--- INDEPENDENT TEST SET EVALUATION ---")
        print(f"Classification Accuracy: {test_acc*100:.2f}%")
        print(f"Macro Precision:         {macro_prec*100:.2f}%")
        print(f"Macro Recall:            {macro_rec*100:.2f}%")
        print(f"Macro F1-Score:          {macro_f1:.4f}")
        print(f"Valence-Arousal MSE:     {test_mse:.4f}")

    # Save weights
    weights_path = os.path.join(BACKEND_DIR, "ser_model_weights.pt")
    torch.save(model.state_dict(), weights_path)
    print(f"Saved PyTorch weights to {weights_path}")

    # Save metadata & feature scalers
    metadata = {
        "model_architecture": "1D-CNN + Bi-LSTM with Self-Attention Pooling (DeepSERNet)",
        "input_features": 40,
        "hidden_dim": 64,
        "classes": EMOTIONS,
        "num_classes": len(EMOTIONS),
        "supported_languages": LANGUAGES,
        "feature_mean": [float(m) for m in feat_mean],
        "feature_std": [float(s) for s in feat_std],
        "metrics": {
            "test_accuracy": round(test_acc, 4),
            "macro_precision": round(macro_prec, 4),
            "macro_recall": round(macro_rec, 4),
            "macro_f1": round(macro_f1, 4),
            "valence_arousal_mse": round(test_mse, 4),
            "training_samples": len(train_idx),
            "validation_samples": len(val_idx),
            "test_samples": len(test_idx),
            "total_samples": N
        },
        "trained_timestamp": datetime.now(timezone.utc).isoformat()
    }
    meta_path = os.path.join(BACKEND_DIR, "ser_model_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved model metadata to {meta_path}")

if __name__ == "__main__":
    train_and_evaluate()
