import os
import sys
import json
import csv
import random
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.ml.dual_domain_forgery_model import DualDomainForgeryNet
from backend.app.ml.document_forensic_model import DocumentForensicRiskRegressorNet

def run_training():
    print("=" * 70)
    print("  PROJECT-043: TRAINING DOCUMENT FORGERY & FORENSIC MODELS (6,000 ROWS)")
    print("=" * 70)

    device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
    print(f"Using compute acceleration device: {device}")

    # Set seeds
    torch.manual_seed(43)
    np.random.seed(43)
    random.seed(43)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "data")
    exp_dir = os.path.join(base_dir, "experiments")
    models_dir = os.path.join(base_dir, "backend", "models")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(exp_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "document_forgery_telemetry_6000.csv")

    doc_types = ["INVOICE", "IDENTITY_CARD", "ACADEMIC_CERTIFICATE", "CONTRACT"]
    forgery_types = ["NONE", "COPY_MOVE", "SPLICING", "TEXT_ERASURE"]
    doc_titles = [
        "Commercial Tax Invoice #9841",
        "Driver License National ID #A772",
        "Degree Certificate Stanford #2024",
        "Real Estate Agreement Clause 4",
        "Medical Reimbursement Claim #510",
        "Employment Contract NDA Schedule",
        "Export Customs Declaration Form",
        "Academic Transcript Honors Board"
    ]

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Generate 6,000-Record Telemetry Dataset
    # ─────────────────────────────────────────────────────────────────────────
    print(f"Generating 6,000 synthetic forensic telemetry records at {csv_path}...")
    fieldnames = [
        "audit_id", "document_title", "document_type", "forgery_verdict", "forgery_type",
        "is_forged", "ela_residual_mean", "ela_variance", "dct_high_pass_energy",
        "quantization_error", "noise_variance", "laplacian_edge_sharpness",
        "color_histogram_divergence", "text_alignment_delta", "copy_move_keypoints",
        "forgery_risk_pct", "tampered_area_pct", "ela_discrepancy_score", "spectral_dct_noise"
    ]

    total_records = 6000
    rows = []
    regressor_features = []
    regressor_targets = []
    spatial_imgs = np.zeros((total_records, 3, 64, 64), dtype=np.float32)
    freq_imgs = np.zeros((total_records, 3, 64, 64), dtype=np.float32)
    class_labels = []

    for i in range(total_records):
        aud_id = f"AUD-2026-{10000 + i}"
        d_type = doc_types[i % len(doc_types)]
        d_title = f"{doc_titles[i % len(doc_titles)]} (Batch-{100 + (i % 20)})"

        # 50% Authentic (Class 0: NONE), 50% Forged (Class 1: COPY_MOVE, Class 2: SPLICING, Class 3: TEXT_ERASURE)
        c_idx = i % 4 # 0: Authentic, 1: Copy-Move, 2: Splicing, 3: Text Erasure
        f_type = forgery_types[c_idx]
        is_forged = 0 if c_idx == 0 else 1

        if is_forged == 0:
            verdict = "AUTHENTIC"
            ela_mean = random.uniform(0.01, 0.08)
            ela_var = random.uniform(0.005, 0.03)
            dct_energy = random.uniform(0.05, 0.20)
            quant_err = random.uniform(0.02, 0.12)
            noise_var = random.uniform(0.01, 0.05)
            edge_sharp = random.uniform(0.70, 0.95)
            color_div = random.uniform(0.01, 0.08)
            align_delta = random.uniform(0.0, 0.5)
            cm_keypoints = 0
            forgery_risk = random.uniform(1.0, 8.0)
            tampered_area = 0.0
            ela_score = random.uniform(0.1, 0.8)
            spec_dct = random.uniform(0.04, 0.18)
        else:
            verdict = "FORGED"
            if f_type == "COPY_MOVE":
                ela_mean = random.uniform(0.12, 0.35)
                ela_var = random.uniform(0.08, 0.25)
                dct_energy = random.uniform(0.40, 0.75)
                quant_err = random.uniform(0.25, 0.55)
                noise_var = random.uniform(0.10, 0.30)
                edge_sharp = random.uniform(0.45, 0.80)
                color_div = random.uniform(0.15, 0.40)
                align_delta = random.uniform(0.4, 2.5)
                cm_keypoints = random.randint(18, 95)
                forgery_risk = random.uniform(85.0, 99.5)
                tampered_area = random.uniform(4.0, 22.0)
                ela_score = random.uniform(6.5, 9.8)
                spec_dct = random.uniform(0.65, 0.94)
            elif f_type == "SPLICING":
                ela_mean = random.uniform(0.30, 0.65) # Severe compression mismatch
                ela_var = random.uniform(0.20, 0.48)
                dct_energy = random.uniform(0.55, 0.88)
                quant_err = random.uniform(0.45, 0.85)
                noise_var = random.uniform(0.25, 0.60)
                edge_sharp = random.uniform(0.30, 0.65)
                color_div = random.uniform(0.35, 0.75)
                align_delta = random.uniform(1.2, 5.0)
                cm_keypoints = random.randint(2, 15)
                forgery_risk = random.uniform(90.0, 99.9)
                tampered_area = random.uniform(8.0, 38.0)
                ela_score = random.uniform(7.8, 9.9)
                spec_dct = random.uniform(0.75, 0.98)
            else: # TEXT_ERASURE
                ela_mean = random.uniform(0.20, 0.45)
                ela_var = random.uniform(0.15, 0.35)
                dct_energy = random.uniform(0.35, 0.65)
                quant_err = random.uniform(0.30, 0.60)
                noise_var = random.uniform(0.15, 0.40)
                edge_sharp = random.uniform(0.20, 0.50) # Blurred inpainting
                color_div = random.uniform(0.10, 0.30)
                align_delta = random.uniform(2.0, 6.5)
                cm_keypoints = 0
                forgery_risk = random.uniform(82.0, 97.5)
                tampered_area = random.uniform(2.0, 15.0)
                ela_score = random.uniform(5.5, 8.8)
                spec_dct = random.uniform(0.55, 0.88)

        row = {
            "audit_id": aud_id,
            "document_title": d_title,
            "document_type": d_type,
            "forgery_verdict": verdict,
            "forgery_type": f_type,
            "is_forged": is_forged,
            "ela_residual_mean": round(ela_mean, 3),
            "ela_variance": round(ela_var, 3),
            "dct_high_pass_energy": round(dct_energy, 3),
            "quantization_error": round(quant_err, 3),
            "noise_variance": round(noise_var, 3),
            "laplacian_edge_sharpness": round(edge_sharp, 3),
            "color_histogram_divergence": round(color_div, 3),
            "text_alignment_delta": round(align_delta, 2),
            "copy_move_keypoints": cm_keypoints,
            "forgery_risk_pct": round(forgery_risk, 1),
            "tampered_area_pct": round(tampered_area, 1),
            "ela_discrepancy_score": round(ela_score, 2),
            "spectral_dct_noise": round(spec_dct, 3)
        }
        rows.append(row)

        # Regressor vector: 10 forensic parameters
        x_reg = [
            ela_mean, ela_var, dct_energy, quant_err, noise_var,
            edge_sharp, color_div, align_delta, float(cm_keypoints), float(is_forged)
        ]
        y_reg = [forgery_risk, tampered_area, ela_score, spec_dct]
        regressor_features.append(x_reg)
        regressor_targets.append(y_reg)

        # Spatial ELA Stream Synthetic Tensor (3, 64, 64)
        s_img = np.ones((3, 64, 64), dtype=np.float32) * 0.15 # Low background residual
        # Frequency DCT Stream Synthetic Tensor (3, 64, 64)
        f_img = np.ones((3, 64, 64), dtype=np.float32) * 0.20

        if is_forged == 1:
            # Tampering anomaly patch in spatial ELA and frequency DCT
            if f_type == "COPY_MOVE":
                s_img[:, 15:35, 15:35] = 0.85
                f_img[:, 15:35, 15:35] = 0.78
            elif f_type == "SPLICING":
                s_img[:, 25:50, 20:45] = 0.95
                f_img[:, 25:50, 20:45] = 0.92
            else: # TEXT_ERASURE
                s_img[:, 10:25, 30:55] = 0.75
                f_img[:, 10:25, 30:55] = 0.70

        spatial_imgs[i] = np.clip(s_img, 0.0, 1.0)
        freq_imgs[i] = np.clip(f_img, 0.0, 1.0)
        class_labels.append(c_idx)

    # Write CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} records in {csv_path} ({os.path.getsize(csv_path)} bytes).")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Train DualDomainForgeryNet
    # ─────────────────────────────────────────────────────────────────────────
    print("\nTraining DualDomainForgeryNet on Spatial ELA & Frequency DCT Streams...")
    train_size = 4800
    val_size = 1200

    s_tensor = torch.tensor(spatial_imgs, dtype=torch.float32)
    f_tensor = torch.tensor(freq_imgs, dtype=torch.float32)
    labels_tensor = torch.tensor(class_labels, dtype=torch.long)

    dataset_cnn = TensorDataset(s_tensor, f_tensor, labels_tensor)
    train_cnn_ds, val_cnn_ds = torch.utils.data.random_split(dataset_cnn, [train_size, val_size])

    train_cnn_loader = DataLoader(train_cnn_ds, batch_size=64, shuffle=True)
    val_cnn_loader = DataLoader(val_cnn_ds, batch_size=64, shuffle=False)

    model_cnn = DualDomainForgeryNet().to(device)
    optimizer_cnn = torch.optim.AdamW(model_cnn.parameters(), lr=1e-3, weight_decay=1e-4)
    criterion_cnn = nn.CrossEntropyLoss()

    for epoch in range(15):
        model_cnn.train()
        total_loss = 0.0
        for bs, bf, bl in train_cnn_loader:
            bs, bf, bl = bs.to(device), bf.to(device), bl.to(device)
            optimizer_cnn.zero_grad()
            logits = model_cnn(bs, bf)
            loss = criterion_cnn(logits, bl)
            loss.backward()
            optimizer_cnn.step()
            total_loss += loss.item()

    model_cnn.eval()
    correct = 0
    total_val = 0
    with torch.no_grad():
        for bs, bf, bl in val_cnn_loader:
            bs, bf, bl = bs.to(device), bf.to(device), bl.to(device)
            logits = model_cnn(bs, bf)
            preds = torch.argmax(logits, dim=-1)
            correct += (preds == bl).sum().item()
            total_val += bl.size(0)

    val_acc = correct / total_val
    print(f"DualDomainForgeryNet Validation Accuracy: {val_acc*100:.2f}%")

    phase2_weights = os.path.join(exp_dir, "phase2_model.pt")
    baseline_weights = os.path.join(exp_dir, "baseline_model.pt")
    torch.save(model_cnn.state_dict(), phase2_weights)
    torch.save(model_cnn.state_dict(), baseline_weights)
    print(f"Saved DualDomainForgeryNet weights to {phase2_weights} ({os.path.getsize(phase2_weights)} bytes)")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Train DocumentForensicRiskRegressorNet
    # ─────────────────────────────────────────────────────────────────────────
    print("\nTraining DocumentForensicRiskRegressorNet...")
    X_reg_arr = np.array(regressor_features, dtype=np.float32)
    Y_reg_arr = np.array(regressor_targets, dtype=np.float32)

    mean_x = np.mean(X_reg_arr, axis=0).tolist()
    std_x = (np.std(X_reg_arr, axis=0) + 1e-6).tolist()

    X_norm = (X_reg_arr - np.array(mean_x, dtype=np.float32)) / np.array(std_x, dtype=np.float32)

    x_reg_t = torch.tensor(X_norm, dtype=torch.float32)
    y_reg_t = torch.tensor(Y_reg_arr, dtype=torch.float32)

    ds_reg = TensorDataset(x_reg_t, y_reg_t)
    train_r_ds, val_r_ds = torch.utils.data.random_split(ds_reg, [train_size, val_size])

    train_r_loader = DataLoader(train_r_ds, batch_size=64, shuffle=True)
    val_r_loader = DataLoader(val_r_ds, batch_size=64, shuffle=False)

    regressor = DocumentForensicRiskRegressorNet(in_features=10).to(device)
    optimizer_reg = torch.optim.AdamW(regressor.parameters(), lr=2e-3, weight_decay=1e-4)
    criterion_l1 = nn.SmoothL1Loss()

    for epoch in range(20):
        regressor.train()
        for bx, by in train_r_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer_reg.zero_grad()
            p_risk, p_area, p_ela, p_dct = regressor(bx)
            p_out = torch.cat([p_risk, p_area, p_ela, p_dct], dim=-1)
            loss = criterion_l1(p_out, by)
            loss.backward()
            optimizer_reg.step()

    regressor.eval()
    errors = []
    with torch.no_grad():
        for bx, by in val_r_loader:
            bx, by = bx.to(device), by.to(device)
            p_risk, p_area, p_ela, p_dct = regressor(bx)
            p_out = torch.cat([p_risk, p_area, p_ela, p_dct], dim=-1)
            err = torch.abs(p_out - by).cpu().numpy()
            errors.append(err)

    all_err = np.concatenate(errors, axis=0)
    mae = np.mean(all_err, axis=0)
    print(f"Regressor Validation MAEs:")
    print(f"  • Forgery Risk: {mae[0]:.2f}%")
    print(f"  • Tampered Area: {mae[1]:.2f}%")
    print(f"  • ELA Discrepancy: {mae[2]:.2f} pts")
    print(f"  • Spectral DCT Noise: {mae[3]:.3f}")

    reg_weights_path = os.path.join(models_dir, "document_forensic_regressor_weights.pt")
    torch.save(regressor.state_dict(), reg_weights_path)
    print(f"Saved regressor weights to {reg_weights_path} ({os.path.getsize(reg_weights_path)} bytes)")

    # 4. Save Scalers
    scalers_path = os.path.join(models_dir, "forgery_scalers.json")
    scalers_data = {
        "features": fieldnames[6:16],
        "mean": mean_x,
        "std": std_x,
        "targets": ["forgery_risk_pct", "tampered_area_pct", "ela_discrepancy_score", "spectral_dct_noise"]
    }
    with open(scalers_path, "w") as f:
        json.dump(scalers_data, f, indent=2)

    # 5. Save Metadata
    meta_path = os.path.join(models_dir, "model_metadata.json")
    meta_data = {
        "model_name": "DualDomainForgeryNet + DocumentForensicRiskRegressorNet",
        "dual_domain_cnn": {
            "parameters": sum(p.numel() for p in model_cnn.parameters()),
            "classes": 4,
            "validation_accuracy": round(val_acc, 4),
            "status": "TRAINED_SERIALIZED"
        },
        "forensic_regressor": {
            "parameters": sum(p.numel() for p in regressor.parameters()),
            "forgery_risk_mae": round(float(mae[0]), 2),
            "tampered_area_mae": round(float(mae[1]), 2),
            "ela_discrepancy_mae": round(float(mae[2]), 2),
            "spectral_dct_mae": round(float(mae[3]), 3),
            "status": "TRAINED_SERIALIZED"
        },
        "dataset_records": 6000,
        "status": "TRAINED_SERIALIZED"
    }
    with open(meta_path, "w") as f:
        json.dump(meta_data, f, indent=2)

    print("Project 43 Model Training and Serialization Complete!")

if __name__ == "__main__":
    run_training()
