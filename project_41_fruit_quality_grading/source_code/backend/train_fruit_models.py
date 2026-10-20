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

from backend.app.ml.multitask_fruit_model import MultiTaskFruitNet
from backend.app.ml.fruit_freshness_model import FruitFreshnessShelfLifeRegressorNet

def run_training():
    print("=" * 70)
    print("  PROJECT-041: TRAINING FRUIT QUALITY & FRESHNESS MODELS (6,000 ROWS)")
    print("=" * 70)

    device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
    print(f"Using compute acceleration device: {device}")

    # Set seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)

    # Output paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "data")
    exp_dir = os.path.join(base_dir, "experiments")
    models_dir = os.path.join(base_dir, "backend", "models")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(exp_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "fruit_quality_telemetry_6000.csv")

    varieties = ["APPLE", "ORANGE", "BANANA", "MANGO"]
    grades = ["GRADE_A_PREMIUM", "GRADE_B_STANDARD", "GRADE_C_REJECT"]
    defects = ["NONE", "BRUISE", "SKIN_ROT", "FUNGAL_SPOT", "SCAB"]
    sorting_chutes = {
        "GRADE_A_PREMIUM": "BIN_1_EXPORT",
        "GRADE_B_STANDARD": "BIN_2_DOMESTIC",
        "GRADE_C_REJECT": "BIN_3_DISCARD"
    }

    # ─────────────────────────────────────────────────────────────────────────
    # 1. Generate 6,000-Record Telemetry Dataset
    # ─────────────────────────────────────────────────────────────────────────
    print(f"Generating 6,000 synthetic physical telemetry records at {csv_path}...")
    fieldnames = [
        "record_id", "batch_lot", "conveyor_lane", "fruit_variety", "variety_id",
        "quality_grade", "grade_id", "defect_type", "defect_id", "sorting_chute",
        "weight_grams", "diameter_mm", "mean_chroma_r", "mean_chroma_g", "mean_chroma_b",
        "surface_defect_ratio", "skin_reflectance_index", "harvest_days_elapsed",
        "cold_storage_temp_c", "storage_humidity_pct", "firmness_n", "sugar_brix",
        "shelf_life_days", "batch_economic_index"
    ]

    total_records = 6000
    rows = []
    regressor_features = []
    regressor_targets = []
    images = np.zeros((total_records, 3, 64, 64), dtype=np.float32)
    var_labels = []
    grade_labels = []
    defect_labels = []

    for i in range(total_records):
        rec_id = f"FRUIT-2026-{10000 + i}"
        batch_lot = f"LOT-{2026}-B{(i // 500) + 1:02d}"
        conveyor_lane = (i % 4) + 1

        v_idx = i % 4
        variety = varieties[v_idx]

        g_idx = i % 3
        grade = grades[g_idx]

        d_idx = i % 5
        defect = defects[d_idx]
        chute = sorting_chutes[grade]

        # Fruit-specific physical parameters
        if variety == "APPLE":
            weight = random.uniform(160.0, 240.0)
            diameter = random.uniform(70.0, 85.0)
            r = random.uniform(0.75, 0.95)
            g = random.uniform(0.20, 0.40)
            b = random.uniform(0.10, 0.20)
        elif variety == "ORANGE":
            weight = random.uniform(180.0, 260.0)
            diameter = random.uniform(72.0, 88.0)
            r = random.uniform(0.85, 0.98)
            g = random.uniform(0.50, 0.70)
            b = random.uniform(0.05, 0.15)
        elif variety == "BANANA":
            weight = random.uniform(120.0, 170.0)
            diameter = random.uniform(55.0, 65.0)
            r = random.uniform(0.70, 0.90)
            g = random.uniform(0.70, 0.90)
            b = random.uniform(0.10, 0.20)
        else: # MANGO
            weight = random.uniform(220.0, 350.0)
            diameter = random.uniform(80.0, 105.0)
            r = random.uniform(0.80, 0.95)
            g = random.uniform(0.55, 0.75)
            b = random.uniform(0.10, 0.25)

        # Grade-driven defect area & physical state
        if grade == "GRADE_A_PREMIUM":
            defect_ratio = random.uniform(0.00, 0.015)
            defect = "NONE"
            d_idx = 0
            harvest_days = random.randint(1, 6)
            reflectance = random.uniform(0.70, 0.90)
            firmness = random.uniform(65.0, 92.0)
            brix = random.uniform(14.0, 20.0)
            shelf_life = random.uniform(15.0, 28.0)
            economic_idx = random.uniform(88.0, 99.5)
        elif grade == "GRADE_B_STANDARD":
            defect_ratio = random.uniform(0.015, 0.060)
            if d_idx == 0:
                d_idx = random.choice([1, 4]) # BRUISE or SCAB
                defect = defects[d_idx]
            harvest_days = random.randint(7, 14)
            reflectance = random.uniform(0.50, 0.72)
            firmness = random.uniform(42.0, 64.0)
            brix = random.uniform(11.0, 15.5)
            shelf_life = random.uniform(7.0, 14.5)
            economic_idx = random.uniform(60.0, 85.0)
        else: # GRADE_C_REJECT
            defect_ratio = random.uniform(0.060, 0.280)
            if d_idx == 0:
                d_idx = random.choice([2, 3]) # SKIN_ROT or FUNGAL_SPOT
                defect = defects[d_idx]
            harvest_days = random.randint(15, 28)
            reflectance = random.uniform(0.15, 0.48)
            firmness = random.uniform(12.0, 38.0)
            brix = random.uniform(7.5, 12.0)
            shelf_life = random.uniform(0.5, 5.0)
            economic_idx = random.uniform(10.0, 48.0)

        storage_temp = random.uniform(2.0, 8.5)
        storage_hum = random.uniform(75.0, 95.0)

        row = {
            "record_id": rec_id,
            "batch_lot": batch_lot,
            "conveyor_lane": conveyor_lane,
            "fruit_variety": variety,
            "variety_id": v_idx,
            "quality_grade": grade,
            "grade_id": g_idx,
            "defect_type": defect,
            "defect_id": d_idx,
            "sorting_chute": chute,
            "weight_grams": round(weight, 1),
            "diameter_mm": round(diameter, 1),
            "mean_chroma_r": round(r, 3),
            "mean_chroma_g": round(g, 3),
            "mean_chroma_b": round(b, 3),
            "surface_defect_ratio": round(defect_ratio, 3),
            "skin_reflectance_index": round(reflectance, 3),
            "harvest_days_elapsed": harvest_days,
            "cold_storage_temp_c": round(storage_temp, 1),
            "storage_humidity_pct": round(storage_hum, 1),
            "firmness_n": round(firmness, 1),
            "sugar_brix": round(brix, 1),
            "shelf_life_days": round(shelf_life, 1),
            "batch_economic_index": round(economic_idx, 1)
        }
        rows.append(row)

        # Regressor vectors
        x_reg = [
            weight, diameter, r, g, b, defect_ratio,
            reflectance, float(harvest_days), storage_temp, storage_hum
        ]
        y_reg = [firmness, brix, shelf_life, economic_idx]
        regressor_features.append(x_reg)
        regressor_targets.append(y_reg)

        # Synthetic multi-channel optical image
        img = np.ones((3, 64, 64), dtype=np.float32)
        img[0] = r + np.random.uniform(-0.04, 0.04, (64, 64))
        img[1] = g + np.random.uniform(-0.04, 0.04, (64, 64))
        img[2] = b + np.random.uniform(-0.04, 0.04, (64, 64))

        # Inject defect artifact if present
        if g_idx == 2: # Reject
            img[:, 20:44, 20:44] = 0.08
        elif g_idx == 1: # Standard defect
            img[:, 25:35, 25:35] = 0.35

        images[i] = np.clip(img, 0.0, 1.0)
        var_labels.append(v_idx)
        grade_labels.append(g_idx)
        defect_labels.append(d_idx)

    # Write CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"CSV generated successfully: {len(rows)} records written.")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. Train MultiTaskFruitNet (Multi-Task ConvNet)
    # ─────────────────────────────────────────────────────────────────────────
    print("\nTraining MultiTaskFruitNet (Variety, Grade, Defect Classification)...")
    x_img_t = torch.tensor(images, dtype=torch.float32)
    y_var_t = torch.tensor(var_labels, dtype=torch.long)
    y_grade_t = torch.tensor(grade_labels, dtype=torch.long)
    y_defect_t = torch.tensor(defect_labels, dtype=torch.long)

    dataset_cnn = TensorDataset(x_img_t, y_var_t, y_grade_t, y_defect_t)
    train_size = int(0.8 * total_records)
    val_size = total_records - train_size
    train_ds, val_ds = torch.utils.data.random_split(dataset_cnn, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=64, shuffle=False)

    model_cnn = MultiTaskFruitNet(num_varieties=4, num_grades=3, num_defects=5).to(device)
    optimizer_cnn = torch.optim.AdamW(model_cnn.parameters(), lr=1e-3, weight_decay=1e-4)
    criterion_ce = nn.CrossEntropyLoss()

    for epoch in range(15):
        model_cnn.train()
        total_loss = 0.0
        for bx, b_var, b_grade, b_def in train_loader:
            bx, b_var, b_grade, b_def = bx.to(device), b_var.to(device), b_grade.to(device), b_def.to(device)
            optimizer_cnn.zero_grad()
            out_v, out_g, out_d = model_cnn(bx)
            loss_v = criterion_ce(out_v, b_var)
            loss_g = criterion_ce(out_g, b_grade)
            loss_d = criterion_ce(out_d, b_def)
            loss = loss_v + loss_g + loss_d
            loss.backward()
            optimizer_cnn.step()
            total_loss += loss.item()

    model_cnn.eval()
    correct_v = 0
    correct_g = 0
    correct_d = 0
    total_val = 0
    with torch.no_grad():
        for bx, b_var, b_grade, b_def in val_loader:
            bx, b_var, b_grade, b_def = bx.to(device), b_var.to(device), b_grade.to(device), b_def.to(device)
            out_v, out_g, out_d = model_cnn(bx)
            correct_v += (out_v.argmax(dim=-1) == b_var).sum().item()
            correct_g += (out_g.argmax(dim=-1) == b_grade).sum().item()
            correct_d += (out_d.argmax(dim=-1) == b_def).sum().item()
            total_val += bx.size(0)

    acc_v = correct_v / total_val
    acc_g = correct_g / total_val
    acc_d = correct_d / total_val
    print(f"Validation Accuracies -> Variety: {acc_v*100:.2f}%, Grade: {acc_g*100:.2f}%, Defect: {acc_d*100:.2f}%")

    phase2_weights = os.path.join(exp_dir, "phase2_model.pt")
    baseline_weights = os.path.join(exp_dir, "baseline_model.pt")
    torch.save(model_cnn.state_dict(), phase2_weights)
    torch.save(model_cnn.state_dict(), baseline_weights)
    print(f"Saved MultiTaskFruitNet weights to {phase2_weights} ({os.path.getsize(phase2_weights)} bytes)")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. Train FruitFreshnessShelfLifeRegressorNet
    # ─────────────────────────────────────────────────────────────────────────
    print("\nTraining FruitFreshnessShelfLifeRegressorNet (Firmness, Brix, Shelf Life, Economic Index)...")
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

    regressor = FruitFreshnessShelfLifeRegressorNet(in_features=10).to(device)
    optimizer_reg = torch.optim.AdamW(regressor.parameters(), lr=2e-3, weight_decay=1e-4)
    criterion_l1 = nn.SmoothL1Loss()

    for epoch in range(20):
        regressor.train()
        for bx, by in train_r_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer_reg.zero_grad()
            p_firm, p_brix, p_shelf, p_econ = regressor(bx)
            p_out = torch.cat([p_firm, p_brix, p_shelf, p_econ], dim=-1)
            loss = criterion_l1(p_out, by)
            loss.backward()
            optimizer_reg.step()

    regressor.eval()
    errors = []
    with torch.no_grad():
        for bx, by in val_r_loader:
            bx, by = bx.to(device), by.to(device)
            p_firm, p_brix, p_shelf, p_econ = regressor(bx)
            p_out = torch.cat([p_firm, p_brix, p_shelf, p_econ], dim=-1)
            err = torch.abs(p_out - by).cpu().numpy()
            errors.append(err)

    all_err = np.concatenate(errors, axis=0)
    mae = np.mean(all_err, axis=0)
    print(f"Regressor Validation MAEs:")
    print(f"  • Firmness: {mae[0]:.2f} N")
    print(f"  • Sugar (Brix): {mae[1]:.2f} Brix %")
    print(f"  • Shelf Life: {mae[2]:.2f} Days")
    print(f"  • Batch Economic Quality: {mae[3]:.2f} Points")

    reg_weights_path = os.path.join(models_dir, "fruit_freshness_regressor_weights.pt")
    torch.save(regressor.state_dict(), reg_weights_path)
    print(f"Saved regressor weights to {reg_weights_path} ({os.path.getsize(reg_weights_path)} bytes)")

    # 4. Save Scalers
    scalers_path = os.path.join(models_dir, "fruit_scalers.json")
    scalers_data = {
        "features": fieldnames[10:20],
        "mean": mean_x,
        "std": std_x,
        "targets": ["firmness_n", "sugar_brix", "shelf_life_days", "batch_economic_index"]
    }
    with open(scalers_path, "w") as f:
        json.dump(scalers_data, f, indent=2)

    # 5. Save Metadata
    meta_path = os.path.join(models_dir, "model_metadata.json")
    meta_data = {
        "model_name": "MultiTaskFruitNet + FruitFreshnessShelfLifeRegressorNet",
        "multitask_cnn": {
            "parameters": sum(p.numel() for p in model_cnn.parameters()),
            "variety_acc": round(acc_v, 4),
            "grade_acc": round(acc_g, 4),
            "defect_acc": round(acc_d, 4),
            "status": "TRAINED_SERIALIZED"
        },
        "freshness_regressor": {
            "parameters": sum(p.numel() for p in regressor.parameters()),
            "firmness_mae": round(float(mae[0]), 2),
            "sugar_brix_mae": round(float(mae[1]), 2),
            "shelf_life_mae": round(float(mae[2]), 2),
            "economic_index_mae": round(float(mae[3]), 2),
            "status": "TRAINED_SERIALIZED"
        },
        "dataset_records": 6000,
        "status": "TRAINED_SERIALIZED"
    }
    with open(meta_path, "w") as f:
        json.dump(meta_data, f, indent=2)

    print("Project 41 Model Training and Serialization Complete!")

if __name__ == "__main__":
    run_training()
