"""
Phase 1 Baseline Spatio-Temporal Model for Accident Detection.
Uses a 2D CNN spatial encoder paired with a Gated Recurrent Unit (GRU)
to model temporal dynamics across consecutive video frames.
"""

import time
import json
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, Any, Tuple
from backend.app.ml.dataset import create_train_val_test_splits


class SpatialCNNEncoder(nn.Module):
    """
    Lightweight, fast ConvNet extracting spatial visual features from individual frames.
    Input: (B*T, 3, 224, 224) -> Output: (B*T, 128)
    """
    def __init__(self, feature_dim: int = 128):
        super().__init__()
        self.conv_net = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1),  # 112x112
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 56x56

            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),  # 28x28
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 14x14

            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),  # 7x7
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten()
        )
        self.fc = nn.Linear(128, feature_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.conv_net(x)
        return self.fc(features)


class BaselineTemporalCNNGRU(nn.Module):
    """
    Phase 1 Baseline Spatio-Temporal Model.
    Processes a sliding sequence of T frames through the spatial CNN encoder,
    followed by a temporal GRU layer and a sigmoid classification head.
    """
    def __init__(self, feature_dim: int = 128, hidden_dim: int = 64, num_layers: int = 1):
        super().__init__()
        self.feature_dim = feature_dim
        self.hidden_dim = hidden_dim
        self.encoder = SpatialCNNEncoder(feature_dim=feature_dim)
        self.gru = nn.GRU(
            input_size=feature_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=False
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, frames: torch.Tensor) -> torch.Tensor:
        """
        Args:
            frames: Tensor of shape (Batch, Time, Channels, Height, Width)
        Returns:
            prob: Tensor of shape (Batch, 1) representing accident probability
        """
        b, t, c, h, w = frames.shape
        # Reshape batch and time for CNN spatial feature extraction
        flat_frames = frames.contiguous().view(b * t, c, h, w)
        spatial_feats = self.encoder(flat_frames)  # (b*t, feature_dim)
        seq_feats = spatial_feats.contiguous().view(b, t, self.feature_dim)  # (b, t, feature_dim)

        gru_out, _ = self.gru(seq_feats)  # (b, t, hidden_dim)
        last_step = gru_out[:, -1, :]      # (b, hidden_dim)
        prob = self.classifier(last_step)  # (b, 1)
        return prob


def train_baseline(
    manifest_path: str = "data/sample_videos/dataset_manifest.json",
    output_model_path: str = "experiments/baseline_model.pt",
    output_log_path: str = "experiments/baseline_experiment.json",
    epochs: int = 5,
    lr: float = 1e-3,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Trains the Phase 1 Baseline model with full experiment logging.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)

    device = torch.device("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    print(f"Training Baseline model on device: {device}")

    train_loader, val_loader, test_loader = create_train_val_test_splits(manifest_path)
    model = BaselineTemporalCNNGRU().to(device)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)

    start_time = time.time()
    epoch_logs = []

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for batch in train_loader:
            frames = batch["frames"].to(device)
            labels = batch["label"].to(device)

            optimizer.zero_grad()
            preds = model(frames)
            loss = criterion(preds, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(labels)

        train_loss /= max(1, len(train_loader.dataset))

        # Evaluate on validation set
        model.eval()
        val_preds, val_targets = [], []
        with torch.no_grad():
            for batch in val_loader:
                frames = batch["frames"].to(device)
                labels = batch["label"].to(device)
                preds = model(frames)
                val_preds.extend(preds.cpu().numpy().flatten())
                val_targets.extend(labels.cpu().numpy().flatten())

        val_preds_arr = np.array(val_preds)
        val_targets_arr = np.array(val_targets)
        val_bin = (val_preds_arr >= 0.5).astype(int)
        accuracy = float(np.mean(val_bin == val_targets_arr)) if len(val_targets_arr) > 0 else 0.0

        epoch_logs.append({
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "val_accuracy": round(accuracy, 4)
        })
        print(f"Epoch {epoch}/{epochs} | Train Loss: {train_loss:.4f} | Val Accuracy: {accuracy:.4f}")

    total_duration = time.time() - start_time

    # Final evaluation on unseen test set
    model.eval()
    test_preds, test_targets = [], []
    with torch.no_grad():
        for batch in test_loader:
            frames = batch["frames"].to(device)
            labels = batch["label"].to(device)
            preds = model(frames)
            test_preds.extend(preds.cpu().numpy().flatten())
            test_targets.extend(labels.cpu().numpy().flatten())

    test_preds_arr = np.array(test_preds)
    test_targets_arr = np.array(test_targets)
    test_bin = (test_preds_arr >= 0.5).astype(int)

    tp = int(np.sum((test_bin == 1) & (test_targets_arr == 1)))
    fp = int(np.sum((test_bin == 1) & (test_targets_arr == 0)))
    tn = int(np.sum((test_bin == 0) & (test_targets_arr == 0)))
    fn = int(np.sum((test_bin == 0) & (test_targets_arr == 1)))

    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    accuracy = float((tp + tn) / len(test_targets_arr)) if len(test_targets_arr) > 0 else 0.0

    experiment_log = {
        "model_name": "BaselineTemporalCNNGRU",
        "phase": "Phase 1 Baseline",
        "device": str(device),
        "random_seed": seed,
        "input_resolution": "224x224",
        "window_size": 16,
        "training_epochs": epochs,
        "learning_rate": lr,
        "training_duration_seconds": round(total_duration, 2),
        "training_history": epoch_logs,
        "test_metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn}
        }
    }

    torch.save(model.state_dict(), output_model_path)
    with open(output_log_path, "w") as f:
        json.dump(experiment_log, f, indent=2)

    print(f"Baseline model saved to {output_model_path}")
    print(f"Experiment log saved to {output_log_path}")
    return experiment_log

if __name__ == "__main__":
    train_baseline()
