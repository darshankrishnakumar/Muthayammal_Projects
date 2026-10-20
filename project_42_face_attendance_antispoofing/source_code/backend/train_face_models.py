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

from backend.app.ml.antispoof_arcface_model import DeepAntiSpoofFaceNet
from backend.app.ml.biometric_liveness_model import BiometricLivenessQualityRegressorNet

def run_training():
    print("=" * 70)
    print("  PROJECT-042: TRAINING FACE ATTENDANCE & ANTI-SPOOFING MODELS (6,000 ROWS)")
    print("=" * 70)

    device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
    print(f"Using compute acceleration device: {device}")

    # Set seeds
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "data")
    exp_dir = os.path.join(base_dir, "experiments")
    models_dir = os.path.join(base_dir, "backend", "models")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(exp_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "face_attendance_telemetry_6000.csv")

    students = [
        ("STU-101", "Alex Chen", "Computer Science", 4),
        ("STU-102", "Priya Sharma", "Artificial Intelligence", 3),
        ("STU-103", "David Miller", "Robotics Engineering", 4),
        ("STU-104", "Sophia Rossi", "Data Science", 3),
        ("STU-105", "Marcus Johnson", "Cybersecurity", 4)
    ]
    attack_types = ["REAL_LIVE_FACE", "PRINT_ATTACK_2D", "SCREEN_REPLAY_ATTACK", "SILICONE_3D_MASK"]
    courses = ["CS-401", "AI-502", "ROB-405", "DS-303", "CYB-408"]

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Generate 6,000-Record Telemetry Dataset
    # ─────────────────────────────────────────────────────────────────────────
    print(f"Generating 6,000 synthetic physical biometric records at {csv_path}...")
    fieldnames = [
        "record_id", "student_id", "full_name", "department", "course_code",
        "presentation_type", "is_spoof", "liveness_status", "status",
        "pupil_interocular_dist_px", "face_pitch_deg", "face_yaw_deg",
        "specular_reflection_ratio", "fft_high_freq_energy", "micro_tremor_score",
        "ambient_lux", "color_gamut_std", "face_match_confidence",
        "spoof_risk_pct", "liveness_optical_flow", "illumination_entropy", "attendance_score"
    ]

    total_records = 6000
    rows = []
    regressor_features = []
    regressor_targets = []
    images = np.zeros((total_records, 3, 64, 64), dtype=np.float32)
    spoof_labels = []

    for i in range(total_records):
        rec_id = f"ATT-2026-{10000 + i}"
        s_idx = i % len(students)
        stu_id, stu_name, stu_dept, stu_year = students[s_idx]
        course = courses[i % len(courses)]

        # 50% Real Live Face, 50% Spoof Attacks (Print, Screen, Mask)
        att_idx = i % 4
        pres_type = attack_types[att_idx]
        is_spoof = 0 if pres_type == "REAL_LIVE_FACE" else 1

        if is_spoof == 0:
            liveness_status = "REAL"
            status = "PRESENT" if (i % 10 != 0) else "LATE"
            specular = random.uniform(0.05, 0.18)
            fft_energy = random.uniform(0.65, 0.95)
            micro_tremor = random.uniform(0.68, 0.96)
            gamut_std = random.uniform(0.20, 0.38)
            face_conf = random.uniform(0.92, 0.995)
            spoof_risk = random.uniform(0.5, 4.5)
            liveness_flow = random.uniform(0.70, 0.98)
            entropy = random.uniform(6.5, 9.2)
            att_score = random.uniform(92.0, 99.8)
        else:
            liveness_status = "SPOOF_DETECTED"
            status = "REJECTED_SPOOF"
            if pres_type == "PRINT_ATTACK_2D":
                specular = random.uniform(0.01, 0.05) # Flat diffuse paper
                fft_energy = random.uniform(0.10, 0.35) # Loss of high freq skin pores
                micro_tremor = random.uniform(0.01, 0.12) # Static photo
                gamut_std = random.uniform(0.05, 0.15)
                face_conf = random.uniform(0.80, 0.92)
                spoof_risk = random.uniform(88.0, 99.5)
                liveness_flow = random.uniform(0.01, 0.15)
                entropy = random.uniform(2.0, 4.5)
                att_score = random.uniform(5.0, 25.0)
            elif pres_type == "SCREEN_REPLAY_ATTACK":
                specular = random.uniform(0.25, 0.55) # Glass screen reflection
                fft_energy = random.uniform(0.75, 0.98) # High freq moire lattice
                micro_tremor = random.uniform(0.05, 0.22) # Display jitter
                gamut_std = random.uniform(0.08, 0.18)
                face_conf = random.uniform(0.82, 0.94)
                spoof_risk = random.uniform(92.0, 99.8)
                liveness_flow = random.uniform(0.08, 0.25)
                entropy = random.uniform(3.0, 5.0)
                att_score = random.uniform(8.0, 28.0)
            else: # SILICONE_3D_MASK
                specular = random.uniform(0.35, 0.65) # Latex / silicone sheen
                fft_energy = random.uniform(0.25, 0.45)
                micro_tremor = random.uniform(0.15, 0.35)
                gamut_std = random.uniform(0.12, 0.22)
                face_conf = random.uniform(0.75, 0.88)
                spoof_risk = random.uniform(85.0, 98.0)
                liveness_flow = random.uniform(0.12, 0.32)
                entropy = random.uniform(3.5, 5.5)
                att_score = random.uniform(10.0, 32.0)

        iod_px = random.uniform(55.0, 72.0)
        pitch = random.uniform(-12.0, 12.0)
        yaw = random.uniform(-15.0, 15.0)
        ambient_lux = random.uniform(280.0, 650.0)

        row = {
            "record_id": rec_id,
            "student_id": stu_id,
            "full_name": stu_name,
            "department": stu_dept,
            "course_code": course,
            "presentation_type": pres_type,
            "is_spoof": is_spoof,
            "liveness_status": liveness_status,
            "status": status,
            "pupil_interocular_dist_px": round(iod_px, 1),
            "face_pitch_deg": round(pitch, 1),
            "face_yaw_deg": round(yaw, 1),
            "specular_reflection_ratio": round(specular, 3),
            "fft_high_freq_energy": round(fft_energy, 3),
            "micro_tremor_score": round(micro_tremor, 3),
            "ambient_lux": round(ambient_lux, 1),
            "color_gamut_std": round(gamut_std, 3),
            "face_match_confidence": round(face_conf, 3),
            "spoof_risk_pct": round(spoof_risk, 1),
            "liveness_optical_flow": round(liveness_flow, 3),
            "illumination_entropy": round(entropy, 2),
            "attendance_score": round(att_score, 1)
        }
        rows.append(row)

        # Regressor vector
        x_reg = [
            iod_px, pitch, yaw, specular, fft_energy, micro_tremor,
            ambient_lux, gamut_std, face_conf, float(is_spoof)
        ]
        y_reg = [spoof_risk, micro_tremor, entropy, att_score]
        regressor_features.append(x_reg)
        regressor_targets.append(y_reg)

        # Synthetic multi-channel face image
        img = np.ones((3, 64, 64), dtype=np.float32) * 0.65
        # Add facial oval feature
        img[0, 15:50, 18:46] = 0.82
        img[1, 15:50, 18:46] = 0.68
        img[2, 15:50, 18:46] = 0.58

        if is_spoof == 1:
            if pres_type == "SCREEN_REPLAY_ATTACK": # Moiré pattern
                img[:, ::4, ::4] = 0.95
            elif pres_type == "PRINT_ATTACK_2D": # Desaturated low gamut
                img[1:] = img[0]
            else: # Specular glare
                img[:, 25:35, 25:35] = 1.0

        images[i] = np.clip(img, 0.0, 1.0)
        spoof_labels.append(1 if is_spoof == 0 else 0) # 1: Real Live Face, 0: Spoof

    # Write CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV generated successfully: {len(rows)} records written.")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Train DeepAntiSpoofFaceNet
    # ─────────────────────────────────────────────────────────────────────────
    print("\nTraining DeepAntiSpoofFaceNet (ArcFace Embedding + Anti-Spoofing Head)...")
    x_img_t = torch.tensor(images, dtype=torch.float32)
    y_spoof_t = torch.tensor(spoof_labels, dtype=torch.long)

    dataset_cnn = TensorDataset(x_img_t, y_spoof_t)
    train_size = int(0.8 * total_records)
    val_size = total_records - train_size
    train_ds, val_ds = torch.utils.data.random_split(dataset_cnn, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False)

    model_face = DeepAntiSpoofFaceNet(embedding_dim=512).to(device)
    optimizer_face = torch.optim.AdamW(model_face.parameters(), lr=1e-3, weight_decay=1e-4)
    criterion_ce = nn.CrossEntropyLoss()

    for epoch in range(15):
        model_face.train()
        for bx, by in train_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer_face.zero_grad()
            emb, spoof_logits = model_face(bx)
            loss = criterion_ce(spoof_logits, by)
            loss.backward()
            optimizer_face.step()

    model_face.eval()
    correct = 0
    total_val = 0
    with torch.no_grad():
        for bx, by in val_loader:
            bx, by = bx.to(device), by.to(device)
            emb, spoof_logits = model_face(bx)
            pred = spoof_logits.argmax(dim=-1)
            correct += (pred == by).sum().item()
            total_val += bx.size(0)

    val_acc = correct / total_val
    print(f"DeepAntiSpoofFaceNet Anti-Spoofing Validation Accuracy: {val_acc*100:.2f}%")

    phase2_weights = os.path.join(exp_dir, "phase2_model.pt")
    baseline_weights = os.path.join(exp_dir, "baseline_model.pt")
    torch.save(model_face.state_dict(), phase2_weights)
    torch.save(model_face.state_dict(), baseline_weights)
    print(f"Saved DeepAntiSpoofFaceNet weights to {phase2_weights} ({os.path.getsize(phase2_weights)} bytes)")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Train BiometricLivenessQualityRegressorNet
    # ─────────────────────────────────────────────────────────────────────────
    print("\nTraining BiometricLivenessQualityRegressorNet...")
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

    regressor = BiometricLivenessQualityRegressorNet(in_features=10).to(device)
    optimizer_reg = torch.optim.AdamW(regressor.parameters(), lr=2e-3, weight_decay=1e-4)
    criterion_l1 = nn.SmoothL1Loss()

    for epoch in range(20):
        regressor.train()
        for bx, by in train_r_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer_reg.zero_grad()
            p_risk, p_tremor, p_ent, p_match = regressor(bx)
            p_out = torch.cat([p_risk, p_tremor, p_ent, p_match], dim=-1)
            loss = criterion_l1(p_out, by)
            loss.backward()
            optimizer_reg.step()

    regressor.eval()
    errors = []
    with torch.no_grad():
        for bx, by in val_r_loader:
            bx, by = bx.to(device), by.to(device)
            p_risk, p_tremor, p_ent, p_match = regressor(bx)
            p_out = torch.cat([p_risk, p_tremor, p_ent, p_match], dim=-1)
            err = torch.abs(p_out - by).cpu().numpy()
            errors.append(err)

    all_err = np.concatenate(errors, axis=0)
    mae = np.mean(all_err, axis=0)
    print(f"Regressor Validation MAEs:")
    print(f"  • Spoof Risk: {mae[0]:.2f}%")
    print(f"  • Micro-Tremor: {mae[1]:.3f}")
    print(f"  • Illumination Entropy: {mae[2]:.2f}")
    print(f"  • Attendance Score: {mae[3]:.2f} pts")

    reg_weights_path = os.path.join(models_dir, "biometric_liveness_regressor_weights.pt")
    torch.save(regressor.state_dict(), reg_weights_path)
    print(f"Saved regressor weights to {reg_weights_path} ({os.path.getsize(reg_weights_path)} bytes)")

    # 4. Save Scalers
    scalers_path = os.path.join(models_dir, "face_scalers.json")
    scalers_data = {
        "features": fieldnames[9:19],
        "mean": mean_x,
        "std": std_x,
        "targets": ["spoof_risk_pct", "micro_tremor_score", "illumination_entropy", "attendance_score"]
    }
    with open(scalers_path, "w") as f:
        json.dump(scalers_data, f, indent=2)

    # 5. Save Metadata
    meta_path = os.path.join(models_dir, "model_metadata.json")
    meta_data = {
        "model_name": "DeepAntiSpoofFaceNet + BiometricLivenessQualityRegressorNet",
        "arcface_antispoof": {
            "parameters": sum(p.numel() for p in model_face.parameters()),
            "embedding_dim": 512,
            "validation_accuracy": round(val_acc, 4),
            "status": "TRAINED_SERIALIZED"
        },
        "liveness_regressor": {
            "parameters": sum(p.numel() for p in regressor.parameters()),
            "spoof_risk_mae": round(float(mae[0]), 2),
            "micro_tremor_mae": round(float(mae[1]), 3),
            "entropy_mae": round(float(mae[2]), 2),
            "attendance_score_mae": round(float(mae[3]), 2),
            "status": "TRAINED_SERIALIZED"
        },
        "dataset_records": 6000,
        "status": "TRAINED_SERIALIZED"
    }
    with open(meta_path, "w") as f:
        json.dump(meta_data, f, indent=2)

    print("Project 42 Model Training and Serialization Complete!")

if __name__ == "__main__":
    run_training()
