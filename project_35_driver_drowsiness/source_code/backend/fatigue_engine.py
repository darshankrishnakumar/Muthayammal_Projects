import os
import json
import uuid
from datetime import datetime, timezone
import numpy as np
import torch
import torch.nn as nn
try:
    from .database import get_connection, record_audit_log
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from database import get_connection, record_audit_log

# ─────────────────────────────────────────────────────────────────────────────
# 1. Neural Architectures matching trained weights
# ─────────────────────────────────────────────────────────────────────────────
class DriverFatigueClassifierNet(nn.Module):
    def __init__(self, in_features=8, num_classes=4):
        super(DriverFatigueClassifierNet, self).__init__()
        self.fc1 = nn.Linear(in_features, 64)
        self.ln1 = nn.LayerNorm(64)
        self.relu = nn.ReLU()
        self.drop = nn.Dropout(0.15)

        self.res_fc1 = nn.Linear(64, 64)
        self.res_ln1 = nn.LayerNorm(64)
        self.res_fc2 = nn.Linear(64, 64)
        self.res_ln2 = nn.LayerNorm(64)

        self.fc2 = nn.Linear(64, 32)
        self.ln2 = nn.LayerNorm(32)
        self.out = nn.Linear(32, num_classes)

    def forward(self, x):
        x = self.drop(self.relu(self.ln1(self.fc1(x))))
        residual = x
        res = self.relu(self.res_ln1(self.res_fc1(x)))
        res = self.res_ln2(self.res_fc2(res))
        x = self.relu(residual + res)
        x = self.drop(self.relu(self.ln2(self.fc2(x))))
        return self.out(x)

class AttentionScoreRegressorNet(nn.Module):
    def __init__(self, in_features=8):
        super(AttentionScoreRegressorNet, self).__init__()
        self.shared = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(64, 48),
            nn.LayerNorm(48),
            nn.ReLU()
        )
        self.head_vigilance = nn.Sequential(
            nn.Linear(48, 24),
            nn.ReLU(),
            nn.Linear(24, 1)
        )
        self.head_microsleep = nn.Sequential(
            nn.Linear(48, 24),
            nn.ReLU(),
            nn.Linear(24, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        feat = self.shared(x)
        vigilance = self.head_vigilance(feat)
        microsleep = self.head_microsleep(feat)
        return vigilance, microsleep

# ─────────────────────────────────────────────────────────────────────────────
# 2. Engine Singleton & Model Weights Loader
# ─────────────────────────────────────────────────────────────────────────────
class DriverFatigueEngine:
    _instance = None

    def __init__(self):
        models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "models"))
        scalers_path = os.path.join(models_dir, "fatigue_scalers.json")
        clf_weights = os.path.join(models_dir, "fatigue_classifier_weights.pt")
        reg_weights = os.path.join(models_dir, "vigilance_regressor_weights.pt")

        with open(scalers_path, "r") as f:
            self.scalers = json.load(f)

        self.feature_cols = self.scalers["feature_cols"]
        self.means = self.scalers["means"]
        self.stds = self.scalers["stds"]
        self.classes = self.scalers["classes"]

        self.clf = DriverFatigueClassifierNet(in_features=8, num_classes=4)
        self.clf.load_state_dict(torch.load(clf_weights, map_location=torch.device("cpu")))
        self.clf.eval()

        self.reg = AttentionScoreRegressorNet(in_features=8)
        self.reg.load_state_dict(torch.load(reg_weights, map_location=torch.device("cpu")))
        self.reg.eval()
        print("DriverFatigueEngine initialized successfully with PyTorch models.")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DriverFatigueEngine()
        return cls._instance

    def predict(self, raw_features: dict, driver_id: str = "DRV-801"):
        # Resolve feature values with physical fallbacks
        ear = float(raw_features.get("ear", 0.34))
        mar = float(raw_features.get("mar", 0.16))

        # Default physics heuristics when missing in single-frame requests
        if "blink_duration_ms" in raw_features:
            blink_dur = float(raw_features["blink_duration_ms"])
        else:
            # Low EAR correlates with prolonged eyelid closures
            blink_dur = float(np.clip(160.0 + max(0.0, 0.32 - ear) * 2800.0, 120.0, 900.0))

        if "blink_frequency_cpm" in raw_features:
            blink_freq = float(raw_features["blink_frequency_cpm"])
        else:
            blink_freq = float(np.clip(16.0 + max(0.0, 0.30 - ear) * 80.0, 8.0, 45.0))

        head_pitch = float(raw_features.get("head_pitch_deg", 0.0))
        head_yaw = float(raw_features.get("head_yaw_deg", 0.0))
        head_roll = float(raw_features.get("head_roll_deg", 0.0))

        if "perclos_pct" in raw_features:
            perclos = float(raw_features["perclos_pct"])
        else:
            # Low EAR triggers higher PERCLOS
            perclos = float(np.clip(max(0.0, 0.34 - ear) * 220.0 + (mar > 0.45) * 12.0, 2.0, 65.0))

        vec = [
            ear, mar, blink_dur, blink_freq,
            head_pitch, head_yaw, head_roll, perclos
        ]

        # Normalize features
        norm_vec = []
        for val, col in zip(vec, self.feature_cols):
            m = self.means[col]
            s = self.stds[col]
            norm_vec.append((val - m) / s)

        t_in = torch.tensor([norm_vec], dtype=torch.float32)

        with torch.no_grad():
            clf_logits = self.clf(t_in)
            probs = torch.softmax(clf_logits, dim=1).numpy()[0]
            pred_class_idx = int(np.argmax(probs))
            drowsiness_state = self.classes[pred_class_idx]

            pred_vig, pred_micro = self.reg(t_in)
            vigilance_score = float(np.clip(pred_vig.numpy()[0][0], 0.0, 100.0))
            microsleep_risk = float(np.clip(pred_micro.numpy()[0][0], 0.0, 1.0))

        # Regulatory & Safety Classification (FMCSA / NHTSA guidelines)
        alert_required = drowsiness_state in ["Moderately Drowsy", "Severely Drowsy"] or vigilance_score < 70.0 or microsleep_risk > 0.45

        if drowsiness_state == "Severely Drowsy" or microsleep_risk > 0.70:
            severity = "CRITICAL"
            alert_type = "HAPTIC_AUDITORY_PULLOVER"
            recommended_action = "IMMEDIATE EMERGENCY STOP: Audible warning siren and haptic seat vibration triggered. Safely exit traffic corridor."
        elif drowsiness_state == "Moderately Drowsy" or microsleep_risk > 0.40:
            severity = "HIGH"
            alert_type = "AUDITORY_WARNING"
            recommended_action = "FATIGUE WARNING: Audible chime activated. Plan rest stop within 15 minutes."
        elif drowsiness_state == "Slightly Drowsy" or vigilance_score < 80.0:
            severity = "MODERATE"
            alert_type = "VISUAL_ALERT"
            recommended_action = "VIGILANCE ADVISORY: Visual dashboard notice. Take a break soon."
        else:
            severity = "NOMINAL"
            alert_type = "NONE"
            recommended_action = "Driver alert and focused. Nominal operating condition."

        # Database persistence
        conn = get_connection()
        cursor = conn.cursor()

        now_str = datetime.now(timezone.utc).isoformat()
        telemetry_id = f"TEL-{uuid.uuid4().hex[:8].upper()}"

        cursor.execute("""
            INSERT INTO fatigue_telemetry (
                telemetry_id, driver_id, timestamp, ear, mar,
                blink_duration_ms, blink_frequency_cpm, head_pitch_deg,
                head_yaw_deg, head_roll_deg, perclos_pct,
                drowsiness_state, vigilance_score, microsleep_risk
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            telemetry_id, driver_id, now_str, ear, mar,
            round(blink_dur, 1), round(blink_freq, 1), round(head_pitch, 2),
            round(head_yaw, 2), round(head_roll, 2), round(perclos, 2),
            drowsiness_state, round(vigilance_score, 2), round(microsleep_risk, 4)
        ))

        alert_id = None
        if alert_required:
            alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
            cursor.execute("""
                INSERT INTO drowsiness_alerts (
                    alert_id, driver_id, timestamp, severity,
                    alert_type, ear, mar, vigilance_score, recommended_action
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert_id, driver_id, now_str, severity,
                alert_type, ear, mar, round(vigilance_score, 2), recommended_action
            ))

        record_audit_log(cursor, "FATIGUE_INFERENCE", "AI_FATIGUE_ENGINE", {
            "driver_id": driver_id,
            "drowsiness_state": drowsiness_state,
            "vigilance_score": round(vigilance_score, 2),
            "microsleep_risk": round(microsleep_risk, 4),
            "alert_required": alert_required
        })

        conn.commit()
        conn.close()

        return {
            "id": telemetry_id,
            "driver_id": driver_id,
            "drowsiness_state": drowsiness_state,
            "drowsiness_score": round(float(1.0 - vigilance_score / 100.0), 4),
            "vigilance_score": round(vigilance_score, 2),
            "microsleep_risk": round(microsleep_risk, 4),
            "ear": round(ear, 4),
            "mar": round(mar, 4),
            "blink_duration_ms": round(blink_dur, 1),
            "blink_frequency_cpm": round(blink_freq, 1),
            "head_pitch_degrees": round(head_pitch, 2),
            "head_yaw_degrees": round(head_yaw, 2),
            "head_roll_degrees": round(head_roll, 2),
            "perclos_pct": round(perclos, 2),
            "probabilities": {cls: round(float(p), 4) for cls, p in zip(self.classes, probs)},
            "alert_required": alert_required,
            "alert_id": alert_id,
            "severity": severity,
            "alert_type": alert_type,
            "alert_message": f"⚠️ {severity} DROWSINESS DETECTED! {recommended_action}" if alert_required else "✅ Driver is Alert and Attentive",
            "recommended_action": recommended_action,
            "timestamp": now_str,
            "model": "PyTorch Deep Residual Fatigue Net & Dual-Head Attention Regressor"
        }
