import os
import json
import csv
import math
import random
from datetime import datetime, timedelta
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

# Fix seeds for exact reproducibility
np.random.seed(42)
torch.manual_seed(42)
random.seed(42)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKEND_DIR, exist_ok=True)

# ─── 1. ATMOSPHERIC STATIONS & POLLUTANT BASELINES ───────────────────────────

STATIONS = [
    {"station_id": "ST-DEL-01", "city": "Delhi", "country": "India", "base_aqi": 235, "temp": 31.5, "humidity": 64.0, "wind": 6.2, "blh": 620},
    {"station_id": "ST-BOM-02", "city": "Mumbai", "country": "India", "base_aqi": 128, "temp": 29.0, "humidity": 78.0, "wind": 14.5, "blh": 850},
    {"station_id": "ST-BLR-03", "city": "Bengaluru", "country": "India", "base_aqi": 68, "temp": 24.2, "humidity": 62.0, "wind": 11.0, "blh": 920},
    {"station_id": "ST-MAA-04", "city": "Chennai", "country": "India", "base_aqi": 82, "temp": 32.0, "humidity": 81.0, "wind": 15.2, "blh": 890},
    {"station_id": "ST-CCU-05", "city": "Kolkata", "country": "India", "base_aqi": 164, "temp": 30.5, "humidity": 75.0, "wind": 8.4, "blh": 710},
    {"station_id": "ST-HYD-06", "city": "Hyderabad", "country": "India", "base_aqi": 105, "temp": 28.0, "humidity": 60.0, "wind": 9.8, "blh": 830},
    {"station_id": "ST-LON-07", "city": "London", "country": "UK", "base_aqi": 42, "temp": 16.0, "humidity": 68.0, "wind": 18.2, "blh": 1100},
    {"station_id": "ST-NYC-08", "city": "New York", "country": "USA", "base_aqi": 48, "temp": 21.0, "humidity": 55.0, "wind": 12.0, "blh": 1050},
    {"station_id": "ST-TYO-09", "city": "Tokyo", "country": "Japan", "base_aqi": 35, "temp": 22.0, "humidity": 58.0, "wind": 10.4, "blh": 1150},
    {"station_id": "ST-PAR-10", "city": "Paris", "country": "France", "base_aqi": 52, "temp": 18.5, "humidity": 64.0, "wind": 13.5, "blh": 1020}
]

AQI_CLASSES = [
    "Good",                      # 0-50
    "Moderate",                  # 51-100
    "Unhealthy for Sensitive",   # 101-150
    "Unhealthy",                 # 151-200
    "Very Unhealthy",            # 201-300
    "Hazardous"                  # 301-500
]

def aqi_to_class(aqi):
    if aqi <= 50: return 0
    elif aqi <= 100: return 1
    elif aqi <= 150: return 2
    elif aqi <= 200: return 3
    elif aqi <= 300: return 4
    else: return 5

# ─── 2. SYNTHESIZE REALISTIC 5,500 HOURLY RECORDS ────────────────────────────

print("Generating 5,500 realistic hourly atmospheric time-series records...")
records = []
start_date = datetime(2026, 1, 1, 0, 0, 0)
num_hours_per_station = 550  # 10 stations x 550 hours = 5,500 records

raw_feature_matrix = []
target_aqi_list = []
target_class_list = []

for station in STATIONS:
    base = station["base_aqi"]
    for h in range(num_hours_per_station):
        cur_time = start_date + timedelta(hours=h)
        hour_of_day = cur_time.hour
        day_of_week = cur_time.weekday()

        # Physical diurnal variations (traffic peaks around 8am & 7pm)
        traffic_factor = 28 * math.sin((hour_of_day - 5) * math.pi / 8) if (6 <= hour_of_day <= 22) else -15
        weekend_dampener = -12 if day_of_week >= 5 else 0

        # Atmospheric inversion factor (nighttime boundary layer collapse)
        inversion = 22 * math.cos(hour_of_day * math.pi / 12)

        # Meteorological fluctuations
        temp_cycle = math.sin((hour_of_day - 9) * math.pi / 12) * 5.0
        temp = round(station["temp"] + temp_cycle + np.random.normal(0, 1.2), 1)
        humidity = round(max(20.0, min(98.0, station["humidity"] - temp_cycle * 2.5 + np.random.normal(0, 2.0))), 1)
        wind = round(max(1.5, station["wind"] + np.random.normal(0, 1.8)), 1)
        wind_dispersion = max(-35, -2.5 * wind)

        # Boundary Layer Height (BLH)
        blh = round(max(250.0, station["blh"] + temp_cycle * 180 + np.random.normal(0, 35)), 0)

        # Seasonal smog episode (e.g. winter inversion / agricultural biomass burning)
        smog_episode = 0
        if station["city"] in ["Delhi", "Kolkata", "Mumbai"]:
            if (100 <= h <= 180) or (340 <= h <= 410):
                smog_episode = 110 + 35 * math.sin((h - 100) * math.pi / 40)

        # Computed composite AQI
        aqi_noise = np.random.normal(0, 8.0)
        aqi = int(max(12, min(495, base + traffic_factor + weekend_dampener + inversion + wind_dispersion + smog_episode + aqi_noise)))

        # Realistic atmospheric pollutant stoichiometries
        pm25 = round(max(3.0, aqi * 0.46 + np.random.normal(0, 3.5)), 1)
        pm10 = round(max(8.0, aqi * 0.76 + np.random.normal(0, 6.0)), 1)
        no2 = round(max(4.0, aqi * 0.22 + traffic_factor * 0.5 + np.random.normal(0, 2.8)), 1)
        so2 = round(max(2.0, 8.0 + aqi * 0.06 + np.random.normal(0, 1.5)), 1)
        co = round(max(0.1, (aqi * 0.009) + (traffic_factor * 0.015) + np.random.normal(0, 0.08)), 2)
        o3 = round(max(5.0, 32.0 + temp_cycle * 6.0 + np.random.normal(0, 4.0)), 1)

        hazard_idx = aqi_to_class(aqi)
        hazard_label = AQI_CLASSES[hazard_idx]

        rec = {
            "record_id": f"REC-{len(records)+1:05d}",
            "station_id": station["station_id"],
            "city": station["city"],
            "country": station["country"],
            "timestamp": cur_time.strftime("%Y-%m-%d %H:00:00"),
            "hour": hour_of_day,
            "day_of_week": day_of_week,
            "pm25": pm25,
            "pm10": pm10,
            "no2": no2,
            "so2": so2,
            "co": co,
            "o3": o3,
            "temperature_c": temp,
            "humidity_pct": humidity,
            "wind_speed_kmh": wind,
            "boundary_layer_height_m": blh,
            "aqi": aqi,
            "hazard_class": hazard_label,
            "hazard_index": hazard_idx
        }
        records.append(rec)

        # Features: [pm25, pm10, no2, so2, co, o3, temp, humidity, wind, blh]
        raw_feature_matrix.append([pm25, pm10, no2, so2, co, o3, temp, humidity, wind, blh])
        target_aqi_list.append(aqi)
        target_class_list.append(hazard_idx)

X_all = np.array(raw_feature_matrix, dtype=np.float32)
y_aqi_all = np.array(target_aqi_list, dtype=np.float32)
y_cls_all = np.array(target_class_list, dtype=np.int64)

print(f"Total synthetic atmospheric records generated: {len(records)} records")

# Save dataset files
csv_path = os.path.join(DATA_DIR, "air_quality_timeseries.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
    writer.writeheader()
    writer.writerows(records)

json_path = os.path.join(DATA_DIR, "air_quality_timeseries.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2)

print(f"Saved: {csv_path} and {json_path}")

# Compute Feature Scaling Parameters (Z-score)
feat_mean = X_all.mean(axis=0).tolist()
feat_std = (X_all.std(axis=0) + 1e-6).tolist()
scaler_params = {
    "feature_names": ["pm25", "pm10", "no2", "so2", "co", "o3", "temperature_c", "humidity_pct", "wind_speed_kmh", "boundary_layer_height_m"],
    "means": feat_mean,
    "stds": feat_std,
    "total_records": len(records),
    "stations_count": len(STATIONS)
}
with open(os.path.join(BACKEND_DIR, "aqi_scalers.json"), "w") as f:
    json.dump(scaler_params, f, indent=2)

# Normalize features
X_norm = (X_all - np.array(feat_mean)) / np.array(feat_std)

# ─── 3. TRAIN DEEP LEARNING MODEL A: BiLSTM TIME-SERIES FORECASTER ───────────
# Takes 24 past hours -> predicts next 24 hours of [PM2.5, PM10, AQI]

print("\n--- Training Deep Model A: BiLSTM Sequence-to-Sequence Forecaster ---")
SEQ_LEN = 24
HORIZON = 24

sequences_X = []
sequences_y = []

# Group by station to prevent sequence discontinuity
for s_idx in range(len(STATIONS)):
    start_pos = s_idx * num_hours_per_station
    end_pos = start_pos + num_hours_per_station
    station_X = X_norm[start_pos:end_pos]
    # target features to forecast: pm25, pm10, aqi
    station_targets = np.column_stack([X_all[start_pos:end_pos, 0], X_all[start_pos:end_pos, 1], y_aqi_all[start_pos:end_pos]])

    for i in range(len(station_X) - SEQ_LEN - HORIZON + 1):
        sequences_X.append(station_X[i:i+SEQ_LEN])
        sequences_y.append(station_targets[i+SEQ_LEN:i+SEQ_LEN+HORIZON])

seq_X_arr = np.array(sequences_X, dtype=np.float32)  # (N, 24, 10)
seq_y_arr = np.array(sequences_y, dtype=np.float32)  # (N, 24, 3)

print(f"Total time-series sequence pairs: {len(seq_X_arr)} windows (24h lookback -> 24h forward)")

class AQITimeSeriesBiLSTM(nn.Module):
    def __init__(self, in_features=10, hidden_dim=64, num_layers=2, out_features=3, horizon=24):
        super().__init__()
        self.horizon = horizon
        self.out_features = out_features
        self.bilstm = nn.LSTM(
            input_size=in_features,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=0.15
        )
        # Bidirectional produces 2 * hidden_dim
        self.fc1 = nn.Linear(hidden_dim * 2, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, horizon * out_features)

    def forward(self, x):
        lstm_out, _ = self.bilstm(x)
        # Pool the temporal representation (use last step or mean)
        last_step = lstm_out[:, -1, :]
        h = self.relu(self.fc1(last_step))
        out = self.fc2(h)
        return out.view(-1, self.horizon, self.out_features)

model_lstm = AQITimeSeriesBiLSTM(in_features=10, hidden_dim=64, num_layers=2, out_features=3, horizon=24)
optimizer_lstm = optim.Adam(model_lstm.parameters(), lr=0.005)
criterion_lstm = nn.HuberLoss(delta=10.0)

# Train for 20 epochs
dataset_t = torch.utils.data.TensorDataset(torch.tensor(seq_X_arr), torch.tensor(seq_y_arr))
loader_t = torch.utils.data.DataLoader(dataset_t, batch_size=64, shuffle=True)

model_lstm.train()
for epoch in range(20):
    total_loss = 0.0
    for bx, by in loader_t:
        optimizer_lstm.zero_grad()
        pred = model_lstm(bx)
        loss = criterion_lstm(pred, by)
        loss.backward()
        optimizer_lstm.step()
        total_loss += loss.item() * len(bx)
    if (epoch + 1) % 5 == 0:
        print(f"BiLSTM Epoch {epoch+1}/20 - Mean Huber Loss: {total_loss / len(seq_X_arr):.4f}")

# Serialize BiLSTM Weights
bilstm_weights_path = os.path.join(BACKEND_DIR, "aqi_bilstm_weights.pt")
torch.save(model_lstm.state_dict(), bilstm_weights_path)
print(f"Saved trained BiLSTM weights to: {bilstm_weights_path}")

# ─── 4. TRAIN DEEP LEARNING MODEL B: HAZARD CLASSIFIER ───────────────────────

print("\n--- Training Deep Model B: Environmental Hazard Classifier ---")

class AQIHazardClassifier(nn.Module):
    def __init__(self, in_features=10, num_classes=6):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.BatchNorm1d(64),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.15),
            nn.Linear(64, 48),
            nn.BatchNorm1d(48),
            nn.LeakyReLU(0.1),
            nn.Dropout(0.1),
            nn.Linear(48, num_classes)
        )

    def forward(self, x):
        return self.net(x)

model_cls = AQIHazardClassifier(in_features=10, num_classes=6)
optimizer_cls = optim.Adam(model_cls.parameters(), lr=0.004)
criterion_cls = nn.CrossEntropyLoss()

# Train/Test Split (80/20)
indices = np.arange(len(X_norm))
np.random.shuffle(indices)
split_idx = int(len(X_norm) * 0.8)
train_idx, test_idx = indices[:split_idx], indices[split_idx:]

X_train_t = torch.tensor(X_norm[train_idx], dtype=torch.float32)
y_train_t = torch.tensor(y_cls_all[train_idx], dtype=torch.long)
X_test_t = torch.tensor(X_norm[test_idx], dtype=torch.float32)
y_test_t = torch.tensor(y_cls_all[test_idx], dtype=torch.long)

train_dataset = torch.utils.data.TensorDataset(X_train_t, y_train_t)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)

model_cls.train()
for epoch in range(25):
    for bx, by in train_loader:
        optimizer_cls.zero_grad()
        out = model_cls(bx)
        loss = criterion_cls(out, by)
        loss.backward()
        optimizer_cls.step()

# Evaluate on test set
model_cls.eval()
with torch.no_grad():
    test_logits = model_cls(X_test_t)
    preds = torch.argmax(test_logits, dim=-1)
    acc = (preds == y_test_t).float().mean().item()
    print(f"Hazard Classifier Test Accuracy: {acc*100:.2f}% across {len(y_test_t)} test vectors")

# Serialize Classifier Weights
cls_weights_path = os.path.join(BACKEND_DIR, "aqi_classifier_weights.pt")
torch.save(model_cls.state_dict(), cls_weights_path)
print(f"Saved trained Classifier weights to: {cls_weights_path}")

# ─── 5. SAVE MODEL METADATA ──────────────────────────────────────────────────

metadata = {
    "project_id": "PROJECT-028",
    "service_name": "AI-Based Air Quality Forecasting and Pollution Level Prediction",
    "assigned_port": 5028,
    "bilstm_architecture": {
        "model_name": "AQITimeSeriesBiLSTM",
        "input_features": 10,
        "hidden_dim": 64,
        "num_layers": 2,
        "bidirectional": True,
        "output_horizon_hours": 24,
        "output_features": ["pm25", "pm10", "predicted_aqi"],
        "loss_function": "HuberLoss (delta=10.0)"
    },
    "classifier_architecture": {
        "model_name": "AQIHazardClassifier",
        "input_features": 10,
        "hidden_layers": [64, 48],
        "output_classes": AQI_CLASSES,
        "test_accuracy": float(round(acc, 4)),
        "loss_function": "CrossEntropyLoss"
    },
    "dataset": {
        "total_records": len(records),
        "monitoring_stations": len(STATIONS),
        "sampling_frequency": "1 hour",
        "start_date": "2026-01-01 00:00:00"
    }
}

with open(os.path.join(BACKEND_DIR, "model_metadata.json"), "w") as f:
    json.dump(metadata, f, indent=2)

print("\n=== Dataset Generation and PyTorch Model Training Completed Successfully ===")
