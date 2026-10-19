import os
import sys
import time
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional

import numpy as np
import torch
import torch.nn as nn
import joblib

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DB_PATH = os.path.join(DATA_DIR, "crime_incident.db")

# 1. PyTorch Model Definition
class CrimeRiskDNN(nn.Module):
    def __init__(self, input_dim=11, num_classes=4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.20),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        return self.net(x)

# 2. Load Model & Artifacts
print("[Backend] Loading PyTorch DNN Risk Forecaster and Random Forest Artifacts...")
device = torch.device("cpu")
model_dnn = CrimeRiskDNN(input_dim=11, num_classes=4)
torch_path = os.path.join(MODELS_DIR, "crime_risk_dnn.pt")
artifacts_path = os.path.join(MODELS_DIR, "crime_pipeline_artifacts.joblib")

if os.path.exists(torch_path):
    model_dnn.load_state_dict(torch.load(torch_path, map_location=device))
    model_dnn.eval()
    print("[Backend] Loaded crime_risk_dnn.pt successfully.")
else:
    print(f"[Backend] WARNING: Model weights not found at {torch_path}")

artifacts = {}
if os.path.exists(artifacts_path):
    artifacts = joblib.load(artifacts_path)
    print("[Backend] Loaded pipeline artifacts successfully.")
else:
    print(f"[Backend] WARNING: Pipeline artifacts not found at {artifacts_path}")

scaler = artifacts.get("scaler")
rf_crime = artifacts.get("rf_crime")
districts_list = artifacts.get("districts", [
    "Central Downtown", "North Waterfront", "South Industrial", 
    "Westside Residential", "East Commercial", "Uptown Arts", 
    "Harbor District", "Tech Corridor"
])
location_types_list = artifacts.get("location_types", [
    "Street / Sidewalk", "Commercial Store / Mall", "Residential Apartment", 
    "Transit Hub / Station", "Parking Garage", "Nightclub / Bar", "Park / Public Space"
])
risk_classes = artifacts.get("risk_classes", ["CRITICAL", "HIGH", "LOW", "MODERATE"])
crime_types = artifacts.get("crime_types", [
    "ASSAULT", "BATTERY", "BURGLARY", "NARCOTICS", 
    "ROBBERY", "THEFT", "VANDALISM", "WEAPONS_VIOLATION"
])
le_dist = artifacts.get("le_dist")
le_loc = artifacts.get("le_loc")
le_risk = artifacts.get("le_risk")
le_crime = artifacts.get("le_crime")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# 3. FastAPI Initialization
app = FastAPI(
    title="Project 13: Empirical Analysis for Crime Prediction and Forecasting",
    description="Enterprise Machine Learning & Deep Learning Crime Forecasting Microservice",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Request / Response Schemas
class RiskPredictionRequest(BaseModel):
    hour: int = Field(default=23, ge=0, le=23)
    day_of_week: int = Field(default=5, ge=0, le=6)
    month: int = Field(default=10, ge=1, le=12)
    is_weekend: int = Field(default=1, ge=0, le=1)
    district: str = Field(default="Central Downtown")
    location_type: str = Field(default="Nightclub / Bar")
    historical_density: float = Field(default=8.5, ge=0.0, le=10.0)
    ambient_light: int = Field(default=2, ge=1, le=5)
    patrol_score: int = Field(default=2, ge=1, le=5)
    latitude: float = Field(default=41.8825)
    longitude: float = Field(default=-87.6285)

class ForecastHourlyRequest(BaseModel):
    district: str = Field(default="Central Downtown")
    day_of_week: int = Field(default=5, ge=0, le=6)
    month: int = Field(default=10, ge=1, le=12)
    location_type: str = Field(default="Street / Sidewalk")

class DispatchRequest(BaseModel):
    unit_callsign: str = Field(default="ALPHA-12")
    assigned_district: str = Field(default="Central Downtown")
    priority_level: str = Field(default="URGENT - CODE 3")
    incident_type: str = Field(default="ROBBERY")
    eta_minutes: int = Field(default=4, ge=1, le=60)

# 5. API Endpoints
@app.get("/")
def read_root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "project_id": "PROJECT-013",
        "title": "EMPIRICAL ANALYSIS FOR CRIME PREDICTION AND FORECASTING USING MACHINE LEARNING AND DEEP LEARNING TECHNIQUES",
        "status": "Operational",
        "port": 5013
    }

@app.get("/health")
def health():
    db_ok = os.path.exists(DB_PATH)
    total_incidents = 0
    if db_ok:
        try:
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM crime_incidents")
                total_incidents = cur.fetchone()[0]
        except Exception:
            pass
    return {
        "status": "healthy",
        "service": "Urban Crime Prediction & Deep Learning Forecasting Subsystem",
        "port": 5013,
        "database": {
            "status": "connected" if db_ok else "missing",
            "file": DB_PATH,
            "total_incidents": total_incidents
        },
        "models": {
            "risk_dnn": "CrimeRiskDNN (PyTorch 11-128-64-32-4)",
            "type_classifier": "RandomForestClassifier (150 trees)",
            "classes": risk_classes
        },
        "timestamp": time.time()
    }

@app.get("/api/districts")
def get_districts():
    district_info = []
    base_coords = {
        "Central Downtown": (41.8825, -87.6285, 0.78),
        "North Waterfront": (41.9100, -87.6320, 0.42),
        "South Industrial": (41.8450, -87.6450, 0.65),
        "Westside Residential": (41.8750, -87.6950, 0.35),
        "East Commercial": (41.8900, -87.6180, 0.58),
        "Uptown Arts": (41.9680, -87.6550, 0.48),
        "Harbor District": (41.8550, -87.6150, 0.70),
        "Tech Corridor": (41.9250, -87.6820, 0.30)
    }
    for d in districts_list:
        lat, lon, baseline = base_coords.get(d, (41.88, -87.63, 0.50))
        district_info.append({
            "name": d,
            "latitude": lat,
            "longitude": lon,
            "baseline_risk": baseline,
            "risk_tier": "CRITICAL" if baseline >= 0.70 else ("HIGH" if baseline >= 0.55 else "MODERATE")
        })
    return {"districts": district_info, "location_types": location_types_list}

@app.get("/api/metrics")
def get_metrics():
    metrics_path = os.path.join(MODELS_DIR, "model_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            return json.load(f)
    return {
        "project_id": "PROJECT-013",
        "dnn_risk_model": {"accuracy": 0.683, "f1_score": 0.667},
        "crime_type_ensemble": {"accuracy": 0.415, "f1_score": 0.290}
    }

@app.get("/api/stats")
def get_stats():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM crime_incidents")
        total = cur.fetchone()[0]

        cur.execute("SELECT risk_category, COUNT(*) FROM crime_incidents GROUP BY risk_category")
        risk_dist = {row[0]: row[1] for row in cur.fetchall()}

        cur.execute("SELECT primary_type, COUNT(*) FROM crime_incidents GROUP BY primary_type ORDER BY COUNT(*) DESC LIMIT 5")
        top_crimes = [{"crime": row[0], "count": row[1]} for row in cur.fetchall()]

        cur.execute("SELECT AVG(risk_score) FROM crime_incidents")
        avg_risk = round(cur.fetchone()[0] or 0.0, 3)

        cur.execute("SELECT COUNT(*) FROM patrol_dispatches")
        total_dispatches = cur.fetchone()[0]

        return {
            "total_incidents": total,
            "risk_distribution": risk_dist,
            "top_crimes": top_crimes,
            "avg_risk_score": avg_risk,
            "total_dispatches": total_dispatches
        }

@app.get("/api/history")
def get_history(limit: int = 25):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, incident_id, timestamp, district, location_type, latitude, longitude,
                   historical_density, risk_score, risk_category, primary_type, arrest_made, patrol_dispatched
            FROM crime_incidents
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        return {"records": rows, "count": len(rows)}

@app.get("/api/dispatches")
def get_dispatches(limit: int = 20):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, dispatch_id, timestamp, unit_callsign, assigned_district, priority_level, incident_type, eta_minutes, status
            FROM patrol_dispatches
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        return {"dispatches": rows, "count": len(rows)}

@app.post("/api/predict_risk")
def predict_risk(req: RiskPredictionRequest):
    t0 = time.time()
    
    # Feature vector mapping
    try:
        dist_code = le_dist.transform([req.district])[0] if le_dist else 0
    except Exception:
        dist_code = 0

    try:
        loc_code = le_loc.transform([req.location_type])[0] if le_loc else 0
    except Exception:
        loc_code = 0

    raw_feat = np.array([[
        req.hour,
        req.day_of_week,
        req.month,
        req.is_weekend,
        dist_code,
        loc_code,
        req.historical_density,
        req.ambient_light,
        req.patrol_score,
        req.latitude,
        req.longitude
    ]])

    if scaler:
        scaled_feat = scaler.transform(raw_feat)
    else:
        scaled_feat = raw_feat

    # 1. Deep Learning Crime Risk Level
    with torch.no_grad():
        x_tensor = torch.tensor(scaled_feat, dtype=torch.float32)
        logits = model_dnn(x_tensor)
        probs = torch.softmax(logits, dim=1).numpy()[0]
        pred_idx = int(np.argmax(probs))
        predicted_risk = le_risk.inverse_transform([pred_idx])[0] if le_risk else risk_classes[pred_idx]
        confidence = float(probs[pred_idx])

    # 2. Random Forest Crime Type Prediction
    predicted_type = "THEFT"
    type_conf = 0.50
    if rf_crime:
        type_probs = rf_crime.predict_proba(scaled_feat)[0]
        type_idx = int(np.argmax(type_probs))
        predicted_type = le_crime.inverse_transform([type_idx])[0] if le_crime else crime_types[type_idx]
        type_conf = float(type_probs[type_idx])

    # Recommended patrol action
    prio_map = {
        "CRITICAL": "URGENT - CODE 3: Dispatch Immediate High-Visibility Tactical Patrol Unit",
        "HIGH": "HIGH - CODE 2: Route Nearest Sector Cruiser & Activate Perimeter Surveillance",
        "MODERATE": "MEDIUM - CODE 1: Increase Regular Patrol Frequency & Verify Street Lighting",
        "LOW": "ROUTINE: Standard Periodic Monitoring, No Immediate Dispatch Required"
    }
    recommendation = prio_map.get(predicted_risk, "Standard Surveillance")

    latency = round((time.time() - t0) * 1000, 2)

    # Log to SQLite
    incident_id = f"CR-LIVE-{int(time.time()*1000)%1000000:06d}"
    t_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    auto_disp = 1 if predicted_risk in ["CRITICAL", "HIGH"] else 0

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO crime_incidents (
                incident_id, timestamp, district, location_type, latitude, longitude,
                historical_density, risk_score, risk_category, primary_type, arrest_made, patrol_dispatched
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident_id, t_str, req.district, req.location_type, req.latitude, req.longitude,
            req.historical_density, round(confidence, 4), predicted_risk, predicted_type, 0, auto_disp
        ))
        conn.commit()

    return {
        "success": True,
        "incident_id": incident_id,
        "timestamp": t_str,
        "district": req.district,
        "location_type": req.location_type,
        "predicted_risk": predicted_risk,
        "risk_confidence": round(confidence * 100, 1),
        "predicted_crime_type": predicted_type,
        "type_confidence": round(type_conf * 100, 1),
        "risk_probabilities": {
            cls_name: round(float(probs[i]) * 100, 1) for i, cls_name in enumerate(le_risk.classes_)
        } if le_risk else {},
        "recommendation": recommendation,
        "patrol_dispatched": bool(auto_disp),
        "inference_latency_ms": latency
    }

@app.post("/api/forecast_hourly")
def forecast_hourly(req: ForecastHourlyRequest):
    t0 = time.time()
    try:
        dist_code = le_dist.transform([req.district])[0] if le_dist else 0
    except Exception:
        dist_code = 0
    try:
        loc_code = le_loc.transform([req.location_type])[0] if le_loc else 0
    except Exception:
        loc_code = 0

    hourly_results = []
    base_lat = 41.88
    base_lon = -87.63

    for h in range(24):
        is_wk = 1 if req.day_of_week in [4, 5, 6] else 0
        raw_feat = np.array([[
            h, req.day_of_week, req.month, is_wk, dist_code, loc_code,
            6.5, 2 if (h >= 20 or h <= 5) else 4, 3, base_lat, base_lon
        ]])
        scaled_feat = scaler.transform(raw_feat) if scaler else raw_feat
        with torch.no_grad():
            logits = model_dnn(torch.tensor(scaled_feat, dtype=torch.float32))
            probs = torch.softmax(logits, dim=1).numpy()[0]
            pred_idx = int(np.argmax(probs))
            risk_cat = le_risk.inverse_transform([pred_idx])[0] if le_risk else risk_classes[pred_idx]
            # Critical / High composite score
            crit_prob = float(probs[le_risk.transform(["CRITICAL"])[0]]) if le_risk and "CRITICAL" in le_risk.classes_ else float(probs[0])
            high_prob = float(probs[le_risk.transform(["HIGH"])[0]]) if le_risk and "HIGH" in le_risk.classes_ else float(probs[1])
            composite = round((crit_prob * 1.0 + high_prob * 0.6) * 100, 1)

        hourly_results.append({
            "hour": h,
            "hour_label": f"{h:02d}:00",
            "risk_category": risk_cat,
            "spike_probability": composite,
            "is_night": bool(h >= 21 or h <= 4)
        })

    return {
        "success": True,
        "district": req.district,
        "day_of_week": req.day_of_week,
        "hourly_forecast": hourly_results,
        "peak_hour": max(hourly_results, key=lambda x: x["spike_probability"])["hour_label"],
        "computation_time_ms": round((time.time() - t0) * 1000, 2)
    }

@app.post("/api/dispatch_unit")
def dispatch_unit(req: DispatchRequest):
    disp_id = f"DISP-UNIT-{int(time.time()*1000)%1000000:06d}"
    t_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO patrol_dispatches (
                dispatch_id, timestamp, unit_callsign, assigned_district, priority_level, incident_type, eta_minutes, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            disp_id, t_str, req.unit_callsign, req.assigned_district, req.priority_level, req.incident_type, req.eta_minutes, "EN_ROUTE"
        ))
        conn.commit()

    return {
        "success": True,
        "dispatch_id": disp_id,
        "timestamp": t_str,
        "status": "DISPATCHED",
        "message": f"Unit {req.unit_callsign} dispatched to {req.assigned_district} (ETA: {req.eta_minutes} min)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5013)
