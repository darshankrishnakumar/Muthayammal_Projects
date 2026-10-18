"""
Apple Health Intelligence AI - Reproducible Training Engine
============================================================
Supports reproducible training and fine-tuning for:
1. Model A: Apple Fruit Condition Classifier (Fresh vs Rotten)
2. Model B: Apple Leaf Disease Classifier (Healthy, Apple_Scab, Black_Rot, Cedar_Apple_Rust)
3. Model C: Apple Input Validator (apple_fruit, apple_leaf, unsupported)

Key Features:
- Two-stage training: Head warm-up -> selective backbone fine-tuning
- Balanced CrossEntropyLoss with automated inverse-frequency class weights
- AdamW optimizer with weight decay
- Learning rate scheduler (CosineAnnealingLR)
- Early stopping based on validation loss/F1
- Saves best checkpoint and complete configuration JSON
"""

import os
import sys
import json
import time
import copy
import random
import argparse
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
from torchvision.datasets import ImageFolder
from PIL import Image

try:
    from sklearn.metrics import classification_report, f1_score, accuracy_score
except ImportError:
    classification_report = None
    f1_score = None
    accuracy_score = None


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class TaskClassifier(nn.Module):
    """MobileNetV2 backbone with modular classification head and Grad-CAM hook."""
    def __init__(self, num_classes: int, dropout: float = 0.3):
        super().__init__()
        base = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
        self.features = base.features
        in_features = base.last_channel  # 1280
        
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(256, num_classes)
        )
        self.gradients = None
        self.activations = None

    def activations_hook(self, grad):
        self.gradients = grad

    def forward(self, x, retain_grad: bool = False):
        feat = self.features(x)
        if retain_grad:
            self.activations = feat
            feat.register_hook(self.activations_hook)
        pooled = F.adaptive_avg_pool2d(feat, (1, 1)).reshape(feat.shape[0], -1)
        out = self.classifier(pooled)
        return out


def get_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomResizedCrop(224, scale=(0.85, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.10, hue=0.02),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    return train_transform, eval_transform


def compute_class_weights(dataset: ImageFolder, device: torch.device) -> torch.Tensor:
    """Calculate inverse class frequency weights to mitigate imbalanced datasets."""
    targets = [s[1] for s in dataset.samples]
    class_counts = np.bincount(targets, minlength=len(dataset.classes))
    total_samples = len(targets)
    num_classes = len(dataset.classes)
    
    weights = []
    for count in class_counts:
        if count > 0:
            w = total_samples / (num_classes * count)
        else:
            w = 1.0
        weights.append(w)
    
    weight_tensor = torch.tensor(weights, dtype=torch.float32).to(device)
    print(f"Class counts: {dict(zip(dataset.classes, class_counts))}")
    print(f"Computed loss weights: {weight_tensor.cpu().numpy().round(3)}")
    return weight_tensor


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, targets in loader:
        images = images.to(device)
        targets = targets.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)
        correct += (preds == targets).sum().item()
        total += targets.size(0)

    epoch_loss = running_loss / max(1, total)
    epoch_acc = (correct / max(1, total)) * 100.0
    return epoch_loss, epoch_acc


def evaluate_epoch(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for images, targets in loader:
            images = images.to(device)
            targets = targets.to(device)

            outputs = model(images)
            loss = criterion(outputs, targets)

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())

    total = len(all_targets)
    epoch_loss = running_loss / max(1, total)
    epoch_acc = (np.array(all_preds) == np.array(all_targets)).mean() * 100.0 if total > 0 else 0.0
    
    macro_f1 = 0.0
    if f1_score and total > 0:
        macro_f1 = f1_score(all_targets, all_preds, average='macro', zero_division=0) * 100.0

    return epoch_loss, epoch_acc, macro_f1, all_preds, all_targets


def run_pipeline(
    task_name: str,
    data_dir: str,
    output_dir: str = "models",
    epochs_head: int = 5,
    epochs_fine: int = 8,
    lr_head: float = 1e-3,
    lr_fine: float = 1e-4,
    batch_size: int = 16,
    patience: int = 4,
    seed: int = 42
):
    set_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n==================================================")
    print(f" STARTING TRAINING: Task = {task_name}")
    print(f" Device = {device} | Seed = {seed}")
    print(f"==================================================")

    train_tf, eval_tf = get_transforms()
    train_dir = Path(data_dir) / "train"
    val_dir = Path(data_dir) / "val"
    test_dir = Path(data_dir) / "test"

    if not train_dir.exists() or not any(train_dir.iterdir()):
        raise RuntimeError(f"Training directory {train_dir} does not exist or is empty. Run prepare_datasets.py first.")

    train_ds = ImageFolder(str(train_dir), transform=train_tf)
    classes = train_ds.classes
    num_classes = len(classes)
    print(f"Target classes ({num_classes}): {classes}")
    print(f"Training samples: {len(train_ds)}")

    def safe_load_image_folder(folder_path, tf):
        if not folder_path.exists():
            return None
        # Check if at least one image file exists in any subfolder
        has_images = any(folder_path.glob("*/*.*"))
        if not has_images:
            return None
        try:
            ds = ImageFolder(str(folder_path), transform=tf)
            return ds if len(ds) > 0 else None
        except Exception:
            return None

    val_ds = safe_load_image_folder(val_dir, eval_tf)
    test_ds = safe_load_image_folder(test_dir, eval_tf)

    # Loaders (use num_workers=0 on Windows to avoid multiprocessing issues)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0) if val_ds else None
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0) if test_ds else None

    # Loss with class weighting
    class_weights = compute_class_weights(train_ds, device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # Initialize model
    model = TaskClassifier(num_classes=num_classes).to(device)

    # Stage 1: Freeze features, train classifier head
    print("\n--- STAGE 1: Training Classification Head (Backbone Frozen) ---")
    for param in model.features.parameters():
        param.requires_grad = False
    optimizer = torch.optim.AdamW(model.classifier.parameters(), lr=lr_head, weight_decay=1e-4)

    best_val_loss = float('inf')
    best_weights = copy.deepcopy(model.state_dict())
    epochs_no_improve = 0

    history_rows = []
    global_epoch = 0

    for epoch in range(1, epochs_head + 1):
        global_epoch += 1
        t0 = time.time()
        t_loss, t_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        v_loss, v_acc, v_f1 = None, None, None

        if val_loader:
            v_loss, v_acc, v_f1, _, _ = evaluate_epoch(model, val_loader, criterion, device)
            print(f"Epoch {epoch:02d}/{epochs_head:02d} [{time.time()-t0:.1f}s] - Train Loss: {t_loss:.4f}, Acc: {t_acc:.1f}% | Val Loss: {v_loss:.4f}, Acc: {v_acc:.1f}%, F1: {v_f1:.1f}%")
            if v_loss < best_val_loss:
                best_val_loss = v_loss
                best_weights = copy.deepcopy(model.state_dict())
        else:
            print(f"Epoch {epoch:02d}/{epochs_head:02d} [{time.time()-t0:.1f}s] - Train Loss: {t_loss:.4f}, Acc: {t_acc:.1f}%")
            best_weights = copy.deepcopy(model.state_dict())

        history_rows.append({
            "epoch": global_epoch,
            "stage": "head_warmup",
            "train_loss": round(t_loss, 4),
            "train_acc": round(t_acc, 2),
            "val_loss": round(v_loss, 4) if v_loss is not None else "",
            "val_acc": round(v_acc, 2) if v_acc is not None else "",
            "val_f1": round(v_f1, 2) if v_f1 is not None else "",
            "lr": lr_head
        })

    # Stage 2: Unfreeze top layers of backbone
    if epochs_fine > 0:
        print("\n--- STAGE 2: Selective Backbone Fine-Tuning ---")
        model.load_state_dict(best_weights)
        # Unfreeze later inverted residual blocks (layers 14 through 18)
        for i, block in enumerate(model.features):
            if i >= 14:
                for param in block.parameters():
                    param.requires_grad = True
            else:
                for param in block.parameters():
                    param.requires_grad = False

        fine_params = [
            {'params': [p for i, blk in enumerate(model.features) if i >= 14 for p in blk.parameters()], 'lr': lr_fine * 0.1},
            {'params': model.classifier.parameters(), 'lr': lr_fine}
        ]
        opt_fine = torch.optim.AdamW(fine_params, weight_decay=1e-4)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt_fine, T_max=epochs_fine, eta_min=1e-6)

        for epoch in range(1, epochs_fine + 1):
            global_epoch += 1
            t0 = time.time()
            t_loss, t_acc = train_one_epoch(model, train_loader, opt_fine, criterion, device)
            curr_lr = opt_fine.param_groups[-1]['lr']
            scheduler.step()

            v_loss, v_acc, v_f1 = None, None, None
            if val_loader:
                v_loss, v_acc, v_f1, _, _ = evaluate_epoch(model, val_loader, criterion, device)
                print(f"Fine Epoch {epoch:02d}/{epochs_fine:02d} [{time.time()-t0:.1f}s] - Train Loss: {t_loss:.4f}, Acc: {t_acc:.1f}% | Val Loss: {v_loss:.4f}, Acc: {v_acc:.1f}%, F1: {v_f1:.1f}%")
                if v_loss < best_val_loss:
                    best_val_loss = v_loss
                    best_weights = copy.deepcopy(model.state_dict())
                    epochs_no_improve = 0
                else:
                    epochs_no_improve += 1
                    if epochs_no_improve >= patience:
                        print(f"Early stopping triggered at epoch {epoch}")
                        history_rows.append({
                            "epoch": global_epoch,
                            "stage": "fine_tuning",
                            "train_loss": round(t_loss, 4),
                            "train_acc": round(t_acc, 2),
                            "val_loss": round(v_loss, 4) if v_loss is not None else "",
                            "val_acc": round(v_acc, 2) if v_acc is not None else "",
                            "val_f1": round(v_f1, 2) if v_f1 is not None else "",
                            "lr": curr_lr
                        })
                        break
            else:
                print(f"Fine Epoch {epoch:02d}/{epochs_fine:02d} [{time.time()-t0:.1f}s] - Train Loss: {t_loss:.4f}, Acc: {t_acc:.1f}%")
                best_weights = copy.deepcopy(model.state_dict())

            history_rows.append({
                "epoch": global_epoch,
                "stage": "fine_tuning",
                "train_loss": round(t_loss, 4),
                "train_acc": round(t_acc, 2),
                "val_loss": round(v_loss, 4) if v_loss is not None else "",
                "val_acc": round(v_acc, 2) if v_acc is not None else "",
                "val_f1": round(v_f1, 2) if v_f1 is not None else "",
                "lr": curr_lr
            })

    # Export training history to results/
    import csv
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    history_csv = results_dir / f"{task_name}_training_history.csv"
    with open(history_csv, "w", newline="") as hf:
        writer = csv.DictWriter(hf, fieldnames=["epoch", "stage", "train_loss", "train_acc", "val_loss", "val_acc", "val_f1", "lr"])
        writer.writeheader()
        writer.writerows(history_rows)
    with open(results_dir / "training_history.csv", "w", newline="") as hf:
        writer = csv.DictWriter(hf, fieldnames=["epoch", "stage", "train_loss", "train_acc", "val_loss", "val_acc", "val_f1", "lr"])
        writer.writeheader()
        writer.writerows(history_rows)
    print(f"[OK] Training history saved to: {history_csv} and {results_dir / 'training_history.csv'}")

    # Load best weights
    model.load_state_dict(best_weights)
    model.eval()

    # Evaluate on held-out test set
    test_metrics = {}
    if test_loader:
        t_loss, t_acc, t_f1, preds, targets = evaluate_epoch(model, test_loader, criterion, device)
        test_metrics = {
            "test_loss": round(t_loss, 4),
            "test_accuracy": round(t_acc, 2),
            "test_macro_f1": round(t_f1, 2)
        }
        print(f"\n[Test Set Results] Loss: {t_loss:.4f} | Accuracy: {t_acc:.2f}% | Macro F1: {t_f1:.2f}%")

    # Save checkpoint and config metadata
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    ckpt_file = out_path / f"apple_{task_name}_v1.pth"
    config_file = out_path / f"apple_{task_name}_v1_config.json"

    torch.save({
        "model_state_dict": model.state_dict(),
        "classes": classes,
        "num_classes": num_classes,
        "architecture": "MobileNetV2_Transfer",
        "task_name": task_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }, str(ckpt_file))

    config_data = {
        "version": "1.0.0",
        "task_name": task_name,
        "model_architecture": "MobileNetV2",
        "pretrained_weights": "MobileNet_V2_Weights.DEFAULT (ImageNet-1K)",
        "classes": classes,
        "class_to_idx": {c: i for i, c in enumerate(classes)},
        "input_dimensions": [3, 224, 224],
        "normalization": {
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225]
        },
        "training_metadata": {
            "seed": seed,
            "device": str(device),
            "epochs_head": epochs_head,
            "epochs_fine": epochs_fine,
            "batch_size": batch_size,
            "best_val_loss": round(best_val_loss, 4) if best_val_loss != float('inf') else None,
            "test_metrics": test_metrics
        }
    }

    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)

    print(f"\n[OK] Model saved to: {ckpt_file}")
    print(f"[OK] Configuration saved to: {config_file}")
    return ckpt_file, config_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Apple Intelligence CNN models")
    parser.add_argument("--task", required=True, choices=["fruit_condition", "leaf_disease", "input_validator"], help="Target task")
    parser.add_argument("--data_dir", required=True, help="Path to processed task directory")
    parser.add_argument("--output_dir", default="models", help="Directory to save checkpoint")
    parser.add_argument("--epochs_head", type=int, default=5, help="Epochs for classification head")
    parser.add_argument("--epochs_fine", type=int, default=6, help="Epochs for backbone fine-tuning")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    run_pipeline(
        task_name=args.task,
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        epochs_head=args.epochs_head,
        epochs_fine=args.epochs_fine,
        batch_size=args.batch_size,
        seed=args.seed
    )
