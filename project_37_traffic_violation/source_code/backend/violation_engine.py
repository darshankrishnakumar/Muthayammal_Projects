import os
import json
import random
import hashlib
from datetime import datetime, timezone
import numpy as np
import torch
import torch.nn as nn

try:
    from .database import get_connection, log_audit_entry
except ImportError:
    from database import get_connection, log_audit_entry

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

CLASSIFIER_PATH = os.path.join(MODELS_DIR, "violation_classifier_weights.pt")
REGRESSOR_PATH = os.path.join(MODELS_DIR, "safety_regressor_weights.pt")
SCALER_PATH = os.path.join(MODELS_DIR, "traffic_scalers.json")

# ─────────────────────────────────────────────────────────────────────────────
# Model Definitions
# ─────────────────────────────────────────────────────────────────────────────

class ResidualBlock(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.fc1 = nn.Linear(dim, dim)
        self.bn1 = nn.BatchNorm1d(dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(dim, dim)
        self.bn2 = nn.BatchNorm1d(dim)
        self.dropout = nn.Dropout(0.15)

    def forward(self, x):
        res = x
        out = self.relu(self.bn1(self.fc1(x)))
        out = self.dropout(out)
        out = self.bn2(self.fc2(out))
        return self.relu(out + res)

class TrafficViolationClassifierNet(nn.Module):
    def __init__(self, input_dim=13, num_classes=8):
        super().__init__()
        self.input_layer = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU()
        )
        self.res1 = ResidualBlock(128)
        self.res2 = ResidualBlock(128)
        self.head = nn.Sequential(
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        x = self.input_layer(x)
        x = self.res1(x)
        x = self.res2(x)
        return self.head(x)

class TrafficSafetySeverityRegressorNet(nn.Module):
    def __init__(self, input_dim=13):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_dim, 96),
            nn.LayerNorm(96),
            nn.GELU(),
            nn.Linear(96, 64),
            nn.LayerNorm(64),
            nn.GELU(),
            nn.Dropout(0.1)
        )
        self.severity_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        self.risk_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        feat = self.shared(x)
        sev = self.severity_head(feat) * 100.0
        risk = self.risk_head(feat)
        return sev, risk

MVA_SECTION_MAP = {
    "Speeding": "MVA Sec 183(1) - Dangerous Speed Violation",
    "Red Light Violation": "MVA Sec 184 - Traffic Signal Jump & Dangerous Driving",
    "Wrong Way Driving": "MVA Sec 184(c) - Driving Against Sanctioned Flow",
    "No Helmet / Two-Wheeler": "MVA Sec 194D - Riding Without Protective Headgear",
    "Mobile Phone Usage": "MVA Sec 184(c) - Distracted Driving Handheld Device",
    "Lane Intrusion / Stop Line Cross": "MVA Sec 177 - Stop Line / Zebra Cross Intrusion",
    "Seatbelt Non-Compliance": "MVA Sec 194B - Driving Without Safety Belt"
}

# ─────────────────────────────────────────────────────────────────────────────
# Engine Singleton
# ─────────────────────────────────────────────────────────────────────────────

class TrafficEnforcementEngine:
    def __init__(self):
        self.loaded = False
        self.load_models()

    def load_models(self):
        if not os.path.exists(SCALER_PATH):
            raise FileNotFoundError(f"Missing scalers file: {SCALER_PATH}")
        with open(SCALER_PATH, "r", encoding="utf-8") as f:
            self.scalers = json.load(f)

        self.feature_cols = self.scalers["feature_cols"]
        self.means = np.array(self.scalers["means"], dtype=np.float32)
        self.stds = np.array(self.scalers["stds"], dtype=np.float32)
        self.classes = self.scalers["classes"]
        self.vehicle_types = self.scalers["vehicle_types"]
        self.fine_map = self.scalers["fine_map"]

        self.classifier = TrafficViolationClassifierNet(input_dim=len(self.feature_cols), num_classes=len(self.classes))
        self.classifier.load_state_dict(torch.load(CLASSIFIER_PATH, weights_only=True))
        self.classifier.eval()

        self.regressor = TrafficSafetySeverityRegressorNet(input_dim=len(self.feature_cols))
        self.regressor.load_state_dict(torch.load(REGRESSOR_PATH, weights_only=True))
        self.regressor.eval()

        self.loaded = True
        print("TrafficEnforcementEngine: PyTorch models and scalers loaded successfully.")

    def _prepare_tensor(self, raw_features):
        arr = np.array(raw_features, dtype=np.float32)
        norm = (arr - self.means) / self.stds
        return torch.tensor(norm, dtype=torch.float32)

    def classify_and_score(self, feature_dict):
        """
        Runs real PyTorch inference on physical/telemetric attributes of a vehicle.
        """
        raw_vec = [
            feature_dict["vehicle_type_idx"],
            feature_dict["speed_kmh"],
            feature_dict["speed_limit"],
            feature_dict["speed_delta"],
            feature_dict["traffic_light_state"],
            feature_dict["distance_to_stop_line_m"],
            feature_dict["lane_position_offset_m"],
            feature_dict["helmet_detected"],
            feature_dict["seatbelt_detected"],
            feature_dict["mobile_phone_detected"],
            feature_dict["heading_degrees"],
            feature_dict["traffic_density"],
            feature_dict["optical_visibility"]
        ]

        t_in = self._prepare_tensor([raw_vec])
        with torch.no_grad():
            logits = self.classifier(t_in)
            probs = torch.softmax(logits, dim=1).numpy()[0]
            pred_idx = int(np.argmax(probs))
            conf = float(probs[pred_idx])

            pred_sev, pred_risk = self.regressor(t_in)
            sev = float(pred_sev.item())
            risk = float(pred_risk.item())

        predicted_class = self.classes[pred_idx]
        has_violation = (predicted_class != "Normal / Compliant")
        fine = self.fine_map.get(predicted_class, 0) if has_violation else 0

        return {
            "violation_detected": has_violation,
            "violation_type": predicted_class if has_violation else None,
            "confidence": round(conf, 4),
            "severity_index": round(sev, 1),
            "collision_risk": round(risk, 4),
            "fine_amount": fine,
            "mva_section": MVA_SECTION_MAP.get(predicted_class, "None") if has_violation else None
        }

    def process_analysis_request(self, payload):
        """
        Handles both:
        1) Single vehicle query: {"vehicle_type": "car", "speed_kmh": 95.0, "speed_limit": 60.0}
        2) Multi-vehicle scene: {"location": "...", "camera_id": "...", ...}
        """
        location = payload.get("location", "INT-01 Central Plaza")
        camera_id = payload.get("camera_id", "CAM-101")

        detections = []

        # Check if single vehicle payload was passed directly
        if "vehicle_type" in payload or "speed_kmh" in payload:
            v_type_str = payload.get("vehicle_type", "Car").capitalize()
            v_type_idx = 0
            for idx, vt in enumerate(self.vehicle_types):
                if vt.lower() == v_type_str.lower():
                    v_type_idx = idx
                    v_type_str = vt
                    break

            speed_kmh = float(payload.get("speed_kmh", 55.0))
            speed_limit = float(payload.get("speed_limit", 60.0))
            speed_delta = round(speed_kmh - speed_limit, 1)

            # Determine indicators
            traffic_light = int(payload.get("traffic_light_state", 0 if payload.get("red_light_jump", False) else 2))
            dist_to_stop = float(payload.get("distance_to_stop_line_m", -2.0 if traffic_light == 0 else 18.0))
            lane_offset = float(payload.get("lane_offset_m", 0.0))
            helmet = int(payload.get("helmet_detected", 1 if v_type_str == "Motorcycle" else 0))
            seatbelt = int(payload.get("seatbelt_detected", 1 if v_type_str in ["Car", "Truck", "Delivery Van"] else 0))
            phone = int(payload.get("mobile_phone_detected", 0))
            heading = float(payload.get("heading_degrees", 180.0 if payload.get("wrong_way", False) else 0.0))
            density = float(payload.get("traffic_density", 45.0))
            visibility = float(payload.get("optical_visibility", 0.95))

            f_dict = {
                "vehicle_type_idx": v_type_idx,
                "speed_kmh": speed_kmh,
                "speed_limit": speed_limit,
                "speed_delta": speed_delta,
                "traffic_light_state": traffic_light,
                "distance_to_stop_line_m": dist_to_stop,
                "lane_position_offset_m": lane_offset,
                "helmet_detected": helmet,
                "seatbelt_detected": seatbelt,
                "mobile_phone_detected": phone,
                "heading_degrees": heading,
                "traffic_density": density,
                "optical_visibility": visibility
            }

            inf = self.classify_and_score(f_dict)
            plate = payload.get("license_plate", f"TN{random.randint(10, 99)}A{random.randint(1000, 9999)}")
            det = {
                "vehicle_id": 1,
                "vehicle_type": v_type_str,
                "license_plate": plate,
                "speed_kmph": speed_kmh,
                "speed_limit": speed_limit,
                "violation_detected": inf["violation_detected"],
                "violation_type": inf["violation_type"],
                "confidence": inf["confidence"],
                "severity_index": inf["severity_index"],
                "collision_risk": inf["collision_risk"],
                "fine_amount": inf["fine_amount"],
                "mva_section": inf["mva_section"],
                "bbox": {"x": 220, "y": 140, "width": 140, "height": 90}
            }
            detections.append(det)

        else:
            # Multi-vehicle CCTV scene generation
            num_vehicles = random.randint(2, 4)
            for i in range(num_vehicles):
                v_type_idx = random.randint(0, len(self.vehicle_types) - 1)
                v_type_str = self.vehicle_types[v_type_idx]
                plate = f"TN{random.randint(10, 99)}A{random.randint(1000, 9999)}"
                speed_limit = 60.0

                # Determine profile
                profile = random.choice([
                    "normal", "normal", "speeding", "red_light", "lane_intrusion", "mobile_phone"
                ])

                if profile == "normal":
                    speed_kmh = round(random.uniform(35.0, 58.0), 1)
                    traffic_light = random.choice([1, 2])
                    dist_to_stop = round(random.uniform(10.0, 35.0), 1)
                    lane_offset = round(random.uniform(-0.3, 0.3), 2)
                    helmet = 1 if v_type_str == "Motorcycle" else 0
                    seatbelt = 1 if v_type_str in ["Car", "Truck", "Delivery Van"] else 0
                    phone = 0
                    heading = round(random.uniform(0.0, 8.0), 1)
                elif profile == "speeding":
                    speed_kmh = round(speed_limit + random.uniform(15.0, 48.0), 1)
                    traffic_light = random.choice([1, 2])
                    dist_to_stop = round(random.uniform(8.0, 30.0), 1)
                    lane_offset = round(random.uniform(-0.4, 0.4), 2)
                    helmet = 1 if v_type_str == "Motorcycle" else 0
                    seatbelt = 1 if v_type_str in ["Car", "Truck", "Delivery Van"] else 0
                    phone = 0
                    heading = round(random.uniform(0.0, 10.0), 1)
                elif profile == "red_light":
                    speed_kmh = round(random.uniform(40.0, 70.0), 1)
                    traffic_light = 0 # Red
                    dist_to_stop = round(random.uniform(-6.0, -1.0), 1)
                    lane_offset = round(random.uniform(-0.5, 0.5), 2)
                    helmet = 1 if v_type_str == "Motorcycle" else 0
                    seatbelt = 1 if v_type_str in ["Car", "Truck", "Delivery Van"] else 0
                    phone = 0
                    heading = round(random.uniform(0.0, 10.0), 1)
                elif profile == "lane_intrusion":
                    speed_kmh = round(random.uniform(35.0, 55.0), 1)
                    traffic_light = 2
                    dist_to_stop = round(random.uniform(12.0, 35.0), 1)
                    lane_offset = round(random.choice([-1.4, 1.4]), 2)
                    helmet = 1 if v_type_str == "Motorcycle" else 0
                    seatbelt = 1 if v_type_str in ["Car", "Truck", "Delivery Van"] else 0
                    phone = 0
                    heading = round(random.uniform(0.0, 12.0), 1)
                elif profile == "mobile_phone":
                    speed_kmh = round(random.uniform(32.0, 52.0), 1)
                    traffic_light = 2
                    dist_to_stop = round(random.uniform(15.0, 35.0), 1)
                    lane_offset = round(random.uniform(-0.8, 0.8), 2)
                    helmet = 1 if v_type_str == "Motorcycle" else 0
                    seatbelt = 1 if v_type_str in ["Car", "Truck", "Delivery Van"] else 0
                    phone = 1
                    heading = round(random.uniform(0.0, 10.0), 1)

                f_dict = {
                    "vehicle_type_idx": v_type_idx,
                    "speed_kmh": speed_kmh,
                    "speed_limit": speed_limit,
                    "speed_delta": round(speed_kmh - speed_limit, 1),
                    "traffic_light_state": traffic_light,
                    "distance_to_stop_line_m": dist_to_stop,
                    "lane_position_offset_m": lane_offset,
                    "helmet_detected": helmet,
                    "seatbelt_detected": seatbelt,
                    "mobile_phone_detected": phone,
                    "heading_degrees": heading,
                    "traffic_density": 45.0,
                    "optical_visibility": 0.95
                }
                inf = self.classify_and_score(f_dict)
                det = {
                    "vehicle_id": i + 1,
                    "vehicle_type": v_type_str,
                    "license_plate": plate,
                    "speed_kmph": speed_kmh,
                    "speed_limit": speed_limit,
                    "violation_detected": inf["violation_detected"],
                    "violation_type": inf["violation_type"],
                    "confidence": inf["confidence"],
                    "severity_index": inf["severity_index"],
                    "collision_risk": inf["collision_risk"],
                    "fine_amount": inf["fine_amount"],
                    "mva_section": inf["mva_section"],
                    "bbox": {
                        "x": 80 + i * 160 + random.randint(-15, 15),
                        "y": 100 + i * 70 + random.randint(-10, 10),
                        "width": 130,
                        "height": 85
                    }
                }
                detections.append(det)

        violations = [d for d in detections if d["violation_detected"]]
        total_fines = sum(v["fine_amount"] for v in violations)
        ts_now = datetime.now(timezone.utc).isoformat()

        # Database persistence
        conn = get_connection()
        cur = conn.cursor()
        created_challans = []

        for d in detections:
            cur.execute("""
            INSERT INTO detected_vehicles 
            (vehicle_id, license_plate, vehicle_type, intersection_id, camera_id, speed_kmh, speed_limit, traffic_light_state, distance_to_stop_line_m, lane_offset_m, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"VEH-{d['license_plate']}", d["license_plate"], d["vehicle_type"],
                location.split()[0], camera_id, d["speed_kmph"], d["speed_limit"],
                0 if d.get("violation_type") == "Red Light Violation" else 2,
                -2.0 if d.get("violation_type") == "Red Light Violation" else 15.0,
                0.0, ts_now
            ))

            if d["violation_detected"]:
                cur.execute("""
                INSERT INTO traffic_violations
                (vehicle_id, license_plate, violation_type, confidence, severity_index, collision_risk, fine_inr, location, camera_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"VEH-{d['license_plate']}", d["license_plate"], d["violation_type"],
                    d["confidence"], d["severity_index"], d["collision_risk"],
                    d["fine_amount"], location, camera_id, ts_now
                ))
                v_id = cur.lastrowid
                challan_id = f"CHL-{random.randint(10000, 99999)}"
                evidence_raw = f"{challan_id}|{d['license_plate']}|{d['violation_type']}|{d['fine_amount']}|{ts_now}"
                ev_hash = hashlib.sha256(evidence_raw.encode("utf-8")).hexdigest()

                cur.execute("""
                INSERT INTO e_challan_records
                (challan_id, violation_id, license_plate, violation_type, fine_amount, mva_section, issue_timestamp, payment_status, evidence_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)
                """, (
                    challan_id, v_id, d["license_plate"], d["violation_type"],
                    d["fine_amount"], d["mva_section"] or "MVA General", ts_now, ev_hash
                ))
                created_challans.append({
                    "challan_id": challan_id,
                    "plate": d["license_plate"],
                    "violation": d["violation_type"],
                    "fine": d["fine_amount"]
                })

        conn.commit()
        conn.close()

        if violations:
            log_audit_entry(
                "VIOLATION_ENFORCEMENT_BATCH",
                f"Detected {len(violations)} violations at {location} via {camera_id}: {[v['violation_type'] for v in violations]}"
            )

        return {
            "camera_id": camera_id,
            "location": location,
            "vehicles_detected": len(detections),
            "violations_found": len(violations),
            "total_fine_amount": total_fines,
            "detections": detections,
            "challans_generated": created_challans,
            "timestamp": ts_now,
            "model": "TrafficViolationClassifierNet (ResMLP) + TrafficSafetySeverityRegressorNet (Dual-Head)"
        }

# Global singleton
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = TrafficEnforcementEngine()
    return _engine
