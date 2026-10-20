import os
import json
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from backend.app.ml.dual_stream_fire_model import DualStreamFireSmokeNet
from backend.app.ml.thermal_risk_model import FirePropagationThermalRiskRegressorNet

np.random.seed(42)
torch.manual_seed(42)
random.seed(42)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_DIR = os.path.join(BASE_DIR, "source_code", "data")
MODELS_DIR = os.path.join(BASE_DIR, "source_code", "backend", "models")
EXP_DIR = os.path.join(BASE_DIR, "source_code", "experiments")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(EXP_DIR, exist_ok=True)

HAZARD_CLASSES = ["NORMAL", "SMOKE_DETECTED", "FLAME_DETECTED", "DUAL_FIRE_SMOKE_HAZARD"]

HAZARD_PROFILES = {
    "NORMAL": {
        "temp_mean": 24.0, "temp_std": 4.0,
        "rad_mean": 0.4, "rad_std": 0.2,
        "obs_mean": 1.2, "obs_std": 0.8,
        "flicker_mean": 0.0, "flicker_std": 0.5,
        "flame_area_mean": 0.0, "flame_area_std": 0.01,
        "plume_mean": 0.3, "plume_std": 0.1,
        "co_mean": 8.0, "co_std": 3.0,
        "urgency_mean": 5.0, "urgency_std": 3.0
    },
    "SMOKE_DETECTED": {
        "temp_mean": 38.0, "temp_std": 8.0,
        "rad_mean": 1.8, "rad_std": 0.6,
        "obs_mean": 45.0, "obs_std": 12.0,
        "flicker_mean": 3.5, "flicker_std": 1.5,
        "flame_area_mean": 0.02, "flame_area_std": 0.02,
        "plume_mean": 2.4, "plume_std": 0.8,
        "co_mean": 120.0, "co_std": 35.0,
        "urgency_mean": 48.0, "urgency_std": 10.0
    },
    "FLAME_DETECTED": {
        "temp_mean": 420.0, "temp_std": 85.0,
        "rad_mean": 18.5, "rad_std": 5.5,
        "obs_mean": 15.0, "obs_std": 6.0,
        "flicker_mean": 12.5, "flicker_std": 2.2,
        "flame_area_mean": 0.35, "flame_area_std": 0.10,
        "plume_mean": 1.8, "plume_std": 0.5,
        "co_mean": 180.0, "co_std": 50.0,
        "urgency_mean": 75.0, "urgency_std": 12.0
    },
    "DUAL_FIRE_SMOKE_HAZARD": {
        "temp_mean": 720.0, "temp_std": 110.0,
        "rad_mean": 36.0, "rad_std": 7.0,
        "obs_mean": 78.0, "obs_std": 14.0,
        "flicker_mean": 15.8, "flicker_std": 2.5,
        "flame_area_mean": 0.55, "flame_area_std": 0.12,
        "plume_mean": 5.4, "plume_std": 1.2,
        "co_mean": 550.0, "co_std": 120.0,
        "urgency_mean": 95.0, "urgency_std": 4.0
    }
}

def generate_telemetry_dataset():
    csv_path = os.path.join(DATA_DIR, "fire_smoke_telemetry_6000.csv")
    print(f"Generating 6,000-record dataset at {csv_path}...")

    zones = [
        "Industrial Plant Boiler Room",
        "Warehouse Sector B Chemical Storage",
        "Commercial Mall Kitchen",
        "Underground Parking Bay 4",
        "Data Center Server Hall 3"
    ]

    records = []
    record_id = 1

    # 1,500 records per class across 4 classes = 6,000 records
    for class_idx, hazard in enumerate(HAZARD_CLASSES):
        prof = HAZARD_PROFILES[hazard]
        for _ in range(1500):
            zone = random.choice(zones)
            camera_id = f"CCTV-{zone[:3].upper()}-0{random.randint(1, 4)}"

            ambient_temp = float(np.clip(np.random.normal(prof["temp_mean"], prof["temp_std"]), 15.0, 950.0))
            rad = float(np.clip(np.random.normal(prof["rad_mean"], prof["rad_std"]), 0.1, 45.0))
            obs = float(np.clip(np.random.normal(prof["obs_mean"], prof["obs_std"]), 0.0, 98.0))
            flicker = float(np.clip(np.random.normal(prof["flicker_mean"], prof["flicker_std"]), 0.0, 24.0))
            flame_area = float(np.clip(np.random.normal(prof["flame_area_mean"], prof["flame_area_std"]), 0.0, 0.85))
            plume = float(np.clip(np.random.normal(prof["plume_mean"], prof["plume_std"]), 0.1, 8.5))
            co = float(np.clip(np.random.normal(prof["co_mean"], prof["co_std"]), 5.0, 800.0))
            airflow = float(np.clip(np.random.normal(1.8, 0.8), 0.1, 6.5))
            occupancy = int(np.clip(np.random.normal(12, 6), 0, 50))
            thermal_strain = float(np.clip(ambient_temp / 950.0 * 0.8 + rad / 45.0 * 0.2, 0.0, 1.0))

            urgency = float(np.clip(prof["urgency_mean"] + np.random.normal(0, prof["urgency_std"]), 0.0, 100.0))

            records.append({
                "record_id": f"HAZ-{record_id:05d}",
                "zone_name": zone,
                "camera_id": camera_id,
                "hazard_type": hazard,
                "class_id": class_idx,
                "ambient_temp_c": round(ambient_temp, 2),
                "ir_thermal_radiation_kw_m2": round(rad, 2),
                "smoke_obscuration_pct_m": round(obs, 2),
                "flicker_frequency_hz": round(flicker, 2),
                "flame_pixel_area_ratio": round(flame_area, 4),
                "plume_expansion_m_s": round(plume, 3),
                "co_concentration_ppm": round(co, 1),
                "airflow_velocity_m_s": round(airflow, 2),
                "zone_occupancy_persons": occupancy,
                "structural_thermal_strain": round(thermal_strain, 4),
                "evacuation_urgency_index": round(urgency, 2)
            })
            record_id += 1

    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False)
    print(f"Generated {len(df)} records across {len(HAZARD_CLASSES)} hazard classes in {csv_path}")
    return df

def train_dual_stream_convnet():
    print("Training DualStreamFireSmokeNet on 6,000 spatial-temporal multi-modal pairs...")
    device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))

    num_samples = 6000
    images = np.random.uniform(0.1, 0.35, (num_samples, 3, 64, 64)).astype(np.float32)
    flicker = np.random.uniform(0.0, 0.15, (num_samples, 8)).astype(np.float32)
    labels = np.repeat(np.arange(4), 1500)

    for i in range(num_samples):
        cls = labels[i]
        if cls == 1:  # SMOKE
            images[i, :, 20:45, 20:45] = np.random.uniform(0.55, 0.75)
            flicker[i, 1] = np.random.uniform(0.35, 0.55)
        elif cls == 2:  # FLAME
            images[i, 0, 25:40, 25:40] = np.random.uniform(0.85, 1.0)
            images[i, 1, 25:40, 25:40] = np.random.uniform(0.40, 0.65)
            flicker[i, 3] = np.random.uniform(0.80, 1.0)
            flicker[i, 4] = np.random.uniform(0.60, 0.85)
        elif cls == 3:  # DUAL HAZARD
            images[i, 0, 20:45, 20:45] = np.random.uniform(0.85, 1.0)
            images[i, 1, 20:45, 20:45] = np.random.uniform(0.40, 0.70)
            images[i, 2, 10:55, 10:55] = np.random.uniform(0.45, 0.70)
            flicker[i, 3] = np.random.uniform(0.85, 1.0)
            flicker[i, 4] = np.random.uniform(0.70, 0.95)
            flicker[i, 1] = np.random.uniform(0.40, 0.65)

    indices = np.random.permutation(num_samples)
    images, flicker, labels = images[indices], flicker[indices], labels[indices]

    train_n = int(0.85 * num_samples)
    img_train, f_train, y_train = torch.tensor(images[:train_n]), torch.tensor(flicker[:train_n]), torch.tensor(labels[:train_n])
    img_val, f_val, y_val = torch.tensor(images[train_n:]), torch.tensor(flicker[train_n:]), torch.tensor(labels[train_n:])

    train_ds = torch.utils.data.TensorDataset(img_train, f_train, y_train)
    loader = DataLoader(train_ds, batch_size=64, shuffle=True)

    model = DualStreamFireSmokeNet(num_classes=4).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.002, weight_decay=1e-4)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(10):
        model.train()
        for b_img, b_f, b_y in loader:
            b_img, b_f, b_y = b_img.to(device), b_f.to(device), b_y.to(device)
            optimizer.zero_grad()
            logits = model(b_img, b_f)
            loss = loss_fn(logits, b_y)
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        val_logits = model(img_val.to(device), f_val.to(device))
        preds = torch.argmax(val_logits, dim=-1).cpu().numpy()
        acc = float(np.mean(preds == labels[train_n:]))
    print(f"DualStreamFireSmokeNet Validation Accuracy: {acc*100:.2f}%")

    phase2_path = os.path.join(EXP_DIR, "phase2_model.pt")
    base_path = os.path.join(EXP_DIR, "baseline_model.pt")
    torch.save(model.state_dict(), phase2_path)
    torch.save(model.state_dict(), base_path)
    print(f"Saved DualStream weights to {phase2_path} ({os.path.getsize(phase2_path)} bytes)")
    return acc

def train_thermal_risk_regressor(df: pd.DataFrame):
    feature_cols = [
        "ambient_temp_c", "ir_thermal_radiation_kw_m2", "smoke_obscuration_pct_m",
        "flicker_frequency_hz", "flame_pixel_area_ratio", "plume_expansion_m_s",
        "co_concentration_ppm", "airflow_velocity_m_s", "zone_occupancy_persons",
        "structural_thermal_strain"
    ]

    target_cols = ["ambient_temp_c", "plume_expansion_m_s", "evacuation_urgency_index", "co_concentration_ppm"]

    X = df[feature_cols].values.astype(np.float32)
    Y = df[target_cols].values.astype(np.float32)

    mean_X = np.mean(X, axis=0)
    std_X = np.std(X, axis=0) + 1e-6
    X_norm = (X - mean_X) / std_X

    scalers = {
        "features": feature_cols,
        "mean": mean_X.tolist(),
        "std": std_X.tolist(),
        "targets": target_cols
    }
    scalers_path = os.path.join(MODELS_DIR, "fire_scalers.json")
    with open(scalers_path, "w") as f:
        json.dump(scalers, f, indent=2)

    n = len(X_norm)
    indices = np.random.permutation(n)
    train_idx, test_idx = indices[:int(0.8*n)], indices[int(0.8*n):]

    X_train, Y_train = torch.tensor(X_norm[train_idx]), torch.tensor(Y[train_idx])
    X_test, Y_test = torch.tensor(X_norm[test_idx]), torch.tensor(Y[test_idx])

    train_ds = torch.utils.data.TensorDataset(X_train, Y_train)
    loader = DataLoader(train_ds, batch_size=64, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
    model = FirePropagationThermalRiskRegressorNet(in_features=len(feature_cols)).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.002, weight_decay=1e-4)
    loss_fn = nn.MSELoss()

    print(f"Training FirePropagationThermalRiskRegressorNet on {device}...")
    for epoch in range(25):
        model.train()
        for bx, by in loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            p_temp, p_plume, p_urg, p_co = model(bx)
            l1 = loss_fn(p_temp.squeeze(), by[:, 0]) * 0.001
            l2 = loss_fn(p_plume.squeeze(), by[:, 1]) * 1.0
            l3 = loss_fn(p_urg.squeeze(), by[:, 2]) * 0.01
            l4 = loss_fn(p_co.squeeze(), by[:, 3]) * 0.001
            loss = l1 + l2 + l3 + l4
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        tx = X_test.to(device)
        ty = Y_test.to(device)
        p_temp, p_plume, p_urg, p_co = model(tx)
        mae_temp = float(torch.mean(torch.abs(p_temp.squeeze() - ty[:, 0])))
        mae_plume = float(torch.mean(torch.abs(p_plume.squeeze() - ty[:, 1])))
        mae_urg = float(torch.mean(torch.abs(p_urg.squeeze() - ty[:, 2])))
        mae_co = float(torch.mean(torch.abs(p_co.squeeze() - ty[:, 3])))

    print(f"Evaluation Results:")
    print(f"  Flame Temp MAE: {mae_temp:.2f} deg C")
    print(f"  Plume Expansion MAE: {mae_plume:.3f} m/s")
    print(f"  Evacuation Urgency MAE: {mae_urg:.2f} points")
    print(f"  CO Toxicity MAE: {mae_co:.1f} ppm")

    weights_path = os.path.join(MODELS_DIR, "thermal_risk_regressor_weights.pt")
    torch.save(model.state_dict(), weights_path)
    print(f"Saved regressor weights to {weights_path} ({os.path.getsize(weights_path)} bytes)")

    meta = {
        "model_name": "DualStreamFireSmokeNet + FirePropagationThermalRiskRegressorNet",
        "parameters": sum(p.numel() for p in model.parameters()),
        "test_mae": {
            "flame_temp_c": round(mae_temp, 2),
            "plume_expansion_m_s": round(mae_plume, 3),
            "evacuation_urgency_index": round(mae_urg, 2),
            "co_concentration_ppm": round(mae_co, 1)
        },
        "target_hazard_classes": len(HAZARD_CLASSES),
        "dataset_records": len(df),
        "status": "TRAINED_SERIALIZED"
    }
    meta_path = os.path.join(MODELS_DIR, "model_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

if __name__ == "__main__":
    df = generate_telemetry_dataset()
    train_dual_stream_convnet()
    train_thermal_risk_regressor(df)
