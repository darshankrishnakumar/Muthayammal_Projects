import os
import time
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

class NIDSInferenceEngine:
    def __init__(self, models_dir: Optional[str] = None):
        if models_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            models_dir = os.path.join(base_dir, "models")
        
        self.models_dir = models_dir
        self.rf_model = None
        self.et_model = None
        self.iso_forest = None
        self.preprocessor = None
        self.label_encoder = None
        self.metrics = {}
        self.load_models()

    def load_models(self):
        rf_path = os.path.join(self.models_dir, "rf_nids_classifier.joblib")
        et_path = os.path.join(self.models_dir, "et_nids_classifier.joblib")
        iso_path = os.path.join(self.models_dir, "isolation_forest_anomaly.joblib")
        prep_path = os.path.join(self.models_dir, "nsl_preprocessor.joblib")
        le_path = os.path.join(self.models_dir, "label_encoder.joblib")
        metrics_path = os.path.join(self.models_dir, "nids_metrics.json")

        if os.path.exists(rf_path):
            self.rf_model = joblib.load(rf_path)
        if os.path.exists(et_path):
            self.et_model = joblib.load(et_path)
        if os.path.exists(iso_path):
            self.iso_forest = joblib.load(iso_path)
        if os.path.exists(prep_path):
            self.preprocessor = joblib.load(prep_path)
        if os.path.exists(le_path):
            self.label_encoder = joblib.load(le_path)
        if os.path.exists(metrics_path):
            with open(metrics_path, "r") as f:
                self.metrics = json.load(f)

    def is_ready(self) -> bool:
        return all([
            self.rf_model is not None,
            self.et_model is not None,
            self.iso_forest is not None,
            self.preprocessor is not None,
            self.label_encoder is not None
        ])

    def get_feature_columns(self):
        num_cols = [
            'duration', 'src_bytes', 'dst_bytes', 'wrong_fragment', 'urgent', 'hot',
            'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell', 'su_attempted',
            'num_root', 'num_file_creations', 'num_shells', 'num_access_files',
            'count', 'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
            'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
            'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
            'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate', 'dst_host_srv_rerror_rate'
        ]
        cat_cols = ['protocol_type', 'service', 'flag']
        return num_cols, cat_cols

    def build_feature_dataframe(self, packet_data: Dict[str, Any]) -> pd.DataFrame:
        num_cols, cat_cols = self.get_feature_columns()
        all_cols = num_cols + cat_cols

        # Defaults representing baseline benign flow
        defaults = {
            'duration': 0,
            'protocol_type': 'tcp',
            'service': 'http',
            'flag': 'SF',
            'src_bytes': 215,
            'dst_bytes': 1500,
            'wrong_fragment': 0,
            'urgent': 0,
            'hot': 0,
            'num_failed_logins': 0,
            'logged_in': 1,
            'num_compromised': 0,
            'root_shell': 0,
            'su_attempted': 0,
            'num_root': 0,
            'num_file_creations': 0,
            'num_shells': 0,
            'num_access_files': 0,
            'count': 1,
            'srv_count': 1,
            'serror_rate': 0.0,
            'srv_serror_rate': 0.0,
            'rerror_rate': 0.0,
            'srv_rerror_rate': 0.0,
            'same_srv_rate': 1.0,
            'diff_srv_rate': 0.0,
            'srv_diff_host_rate': 0.0,
            'dst_host_count': 100,
            'dst_host_srv_count': 100,
            'dst_host_same_srv_rate': 1.0,
            'dst_host_diff_srv_rate': 0.0,
            'dst_host_same_src_port_rate': 0.05,
            'dst_host_srv_diff_host_rate': 0.0,
            'dst_host_serror_rate': 0.0,
            'dst_host_srv_serror_rate': 0.0,
            'dst_host_rerror_rate': 0.0,
            'dst_host_srv_rerror_rate': 0.0
        }

        # Override defaults with provided packet parameters
        row = {}
        for col in all_cols:
            if col in packet_data:
                row[col] = packet_data[col]
            else:
                row[col] = defaults.get(col, 0)

        return pd.DataFrame([row])

    def predict_packet(self, packet_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        if not self.is_ready():
            raise RuntimeError("NIDS models are not loaded or preprocessor missing.")

        df = self.build_feature_dataframe(packet_data)
        X_trans = self.preprocessor.transform(df)

        # 1. Random Forest Predictions
        rf_pred_idx = int(self.rf_model.predict(X_trans)[0])
        rf_proba = self.rf_model.predict_proba(X_trans)[0]

        # 2. Extra Trees Predictions
        et_pred_idx = int(self.et_model.predict(X_trans)[0])
        et_proba = self.et_model.predict_proba(X_trans)[0]

        # 3. Ensemble Blending (Weighted Average: 55% RF + 45% ET)
        ensemble_proba = (0.55 * rf_proba) + (0.45 * et_proba)
        ensemble_pred_idx = int(np.argmax(ensemble_proba))
        predicted_category = self.label_encoder.inverse_transform([ensemble_pred_idx])[0]
        confidence = float(ensemble_proba[ensemble_pred_idx])

        # Probability breakdown per class
        classes = list(self.label_encoder.classes_)
        class_probabilities = {
            cls_name: round(float(prob), 4)
            for cls_name, prob in zip(classes, ensemble_proba)
        }

        # 4. Isolation Forest Anomaly Detection
        # decision_function gives signed distance: negative means anomalous, positive means inlier
        iso_score_raw = float(self.iso_forest.decision_function(X_trans)[0])
        # Normalize anomaly score to [0, 100%]
        # Typical range of decision_function is roughly -0.3 to +0.2
        anomaly_score_pct = round(float(np.clip((0.15 - iso_score_raw) / 0.35 * 100, 0, 100)), 1)
        is_anomalous = bool(iso_score_raw < 0 or anomaly_score_pct > 55.0)

        # 5. Threat Level & Mitigation
        if predicted_category == 'Normal':
            if is_anomalous:
                threat_level = "SUSPICIOUS_ANOMALY"
                action = "FLAG: Zero-day pattern detected by Isolation Forest. Route to sandbox analyzer."
            else:
                threat_level = "BENIGN"
                action = "ALLOW: Standard verified network session."
        elif predicted_category == 'DoS':
            threat_level = "CRITICAL_ATTACK"
            action = "BLOCK: High-frequency denial-of-service signatures detected. Rate-limit and throttle host."
        elif predicted_category == 'Probe':
            threat_level = "HIGH_ALERT"
            action = "ALERT: Port scan or host reconnaissance activity detected. Blacklist source IP."
        elif predicted_category == 'R2L':
            threat_level = "HIGH_ALERT"
            action = "RESTRICT: Unauthorized remote access attempt detected. Revoke session credentials."
        elif predicted_category == 'U2R':
            threat_level = "CRITICAL_ATTACK"
            action = "ISOLATE: Privilege escalation attempt identified. Quarantine endpoint and initiate audit."
        else:
            threat_level = "MODERATE"
            action = "MONITOR: Packet requires elevated monitoring."

        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "predicted_category": predicted_category,
            "confidence": round(confidence, 4),
            "threat_level": threat_level,
            "is_anomaly": is_anomalous,
            "anomaly_score_pct": anomaly_score_pct,
            "isolation_score_raw": round(iso_score_raw, 4),
            "recommended_action": action,
            "class_probabilities": class_probabilities,
            "models_evaluated": {
                "random_forest_prediction": self.label_encoder.inverse_transform([rf_pred_idx])[0],
                "extra_trees_prediction": self.label_encoder.inverse_transform([et_pred_idx])[0],
                "ensemble_consensus": (rf_pred_idx == et_pred_idx)
            },
            "latency_ms": latency_ms,
            "timestamp": time.time()
        }

    def get_presets(self) -> Dict[str, Dict[str, Any]]:
        return {
            "syn_flood_dos": {
                "name": "Neptune SYN Flood (DoS Attack)",
                "description": "Rapid succession of TCP SYN packets with no completion, saturating connection state tables.",
                "data": {
                    "duration": 0,
                    "protocol_type": "tcp",
                    "service": "private",
                    "flag": "S0",
                    "src_bytes": 0,
                    "dst_bytes": 0,
                    "count": 250,
                    "srv_count": 20,
                    "serror_rate": 1.0,
                    "srv_serror_rate": 1.0,
                    "same_srv_rate": 0.08,
                    "diff_srv_rate": 0.06,
                    "dst_host_count": 255,
                    "dst_host_srv_count": 10,
                    "dst_host_same_srv_rate": 0.04,
                    "dst_host_diff_srv_rate": 0.06,
                    "dst_host_serror_rate": 1.0,
                    "dst_host_srv_serror_rate": 1.0
                }
            },
            "port_scan_probe": {
                "name": "Port Sweep (Probe Reconnaissance)",
                "description": "Systematic probe of ports across a range of hosts using TCP RST responses.",
                "data": {
                    "duration": 0,
                    "protocol_type": "tcp",
                    "service": "private",
                    "flag": "RSTR",
                    "src_bytes": 0,
                    "dst_bytes": 0,
                    "count": 1,
                    "srv_count": 1,
                    "serror_rate": 0.0,
                    "rerror_rate": 1.0,
                    "same_srv_rate": 1.0,
                    "diff_srv_rate": 0.0,
                    "dst_host_count": 133,
                    "dst_host_srv_count": 1,
                    "dst_host_diff_srv_rate": 0.65,
                    "dst_host_same_src_port_rate": 0.64,
                    "dst_host_rerror_rate": 0.65
                }
            },
            "normal_http_session": {
                "name": "Benign Web Browsing (HTTP Session)",
                "description": "Standard legitimate HTTP transaction over TCP with complete handshake.",
                "data": {
                    "duration": 1,
                    "protocol_type": "tcp",
                    "service": "http",
                    "flag": "SF",
                    "src_bytes": 280,
                    "dst_bytes": 3520,
                    "logged_in": 1,
                    "count": 3,
                    "srv_count": 5,
                    "serror_rate": 0.0,
                    "srv_serror_rate": 0.0,
                    "rerror_rate": 0.0,
                    "same_srv_rate": 1.0,
                    "diff_srv_rate": 0.0,
                    "dst_host_count": 45,
                    "dst_host_srv_count": 230,
                    "dst_host_same_srv_rate": 1.0,
                    "dst_host_diff_srv_rate": 0.0,
                    "dst_host_serror_rate": 0.0,
                    "dst_host_rerror_rate": 0.0
                }
            },
            "ssh_brute_force_r2l": {
                "name": "Password Brute-Force (R2L Unauthorized Access)",
                "description": "Repeated failed login authentication attempts over Telnet/SSH service.",
                "data": {
                    "duration": 2,
                    "protocol_type": "tcp",
                    "service": "telnet",
                    "flag": "SF",
                    "src_bytes": 125,
                    "dst_bytes": 178,
                    "hot": 2,
                    "num_failed_logins": 5,
                    "logged_in": 0,
                    "count": 1,
                    "srv_count": 1,
                    "serror_rate": 0.0,
                    "dst_host_count": 15,
                    "dst_host_srv_count": 15,
                    "dst_host_same_srv_rate": 1.0,
                    "dst_host_diff_srv_rate": 0.0
                }
            },
            "buffer_overflow_u2r": {
                "name": "Buffer Overflow (U2R Privilege Escalation)",
                "description": "Exploit payload designed to execute arbitrary code with root shell privileges.",
                "data": {
                    "duration": 45,
                    "protocol_type": "tcp",
                    "service": "telnet",
                    "flag": "SF",
                    "src_bytes": 2400,
                    "dst_bytes": 4800,
                    "hot": 3,
                    "logged_in": 1,
                    "root_shell": 1,
                    "su_attempted": 1,
                    "num_root": 5,
                    "num_file_creations": 2,
                    "num_shells": 1,
                    "count": 1,
                    "srv_count": 1
                }
            },
            "zero_day_anomaly": {
                "name": "Zero-Day Exfiltration (Unsupervised Anomaly)",
                "description": "Novel out-of-distribution traffic signature with abnormal fragmentation and volume.",
                "data": {
                    "duration": 450,
                    "protocol_type": "udp",
                    "service": "other",
                    "flag": "OTH",
                    "src_bytes": 985000,
                    "dst_bytes": 845000,
                    "urgent": 8,
                    "hot": 18,
                    "num_compromised": 42,
                    "count": 480,
                    "srv_count": 480
                }
            }
        }
