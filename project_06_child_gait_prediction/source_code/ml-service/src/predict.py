"""
Inference module for Child Gait Prediction.
Loads the trained Random Forest model and preprocessor to perform predictions on validated features.
"""

import os
from typing import Dict, Any, Optional
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "gait_final_model.joblib")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "models", "gait_preprocessor.joblib")
FALLBACK_MODEL_PATH = os.path.join(BASE_DIR, "models", "gait_random_forest_baseline.joblib")

FEATURE_COLS = [
    "walking_speed",
    "stride_length",
    "step_duration",
    "cadence",
    "pelvic_tilt",
    "step_asymmetry",
    "peak_vertical_force_bw",
]


class GaitPredictor:
    def __init__(self, model_path: str = MODEL_PATH, preprocessor_path: str = PREPROCESSOR_PATH):
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.classes = []
        self._load()

    def _load(self):
        # 1. Try final model
        if os.path.exists(self.model_path) and os.path.exists(self.preprocessor_path):
            try:
                model_bundle = joblib.load(self.model_path)
                prep_bundle = joblib.load(self.preprocessor_path)
                self.model = model_bundle["model"]
                self.classes = model_bundle["classes"]
                self.scaler = prep_bundle["scaler"]
                self.label_encoder = prep_bundle["label_encoder"]
                return
            except Exception as e:
                print(f"[Warning] Error loading final model: {e}")

        # 2. Try baseline model bundle
        if os.path.exists(FALLBACK_MODEL_PATH):
            try:
                bundle = joblib.load(FALLBACK_MODEL_PATH)
                self.model = bundle["model"]
                self.scaler = bundle["scaler"]
                self.label_encoder = bundle["label_encoder"]
                self.classes = bundle["classes"]
                return
            except Exception as e:
                print(f"[Warning] Error loading baseline model: {e}")

    @property
    def is_ready(self) -> bool:
        return self.model is not None and self.scaler is not None

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs model inference on input features.
        Supports automatic deriving of cadence if step_duration is provided.
        """
        if not self.is_ready:
            raise RuntimeError("ML model is not loaded or not trained yet.")

        # Extract primary spatio-temporal features
        speed = float(input_data.get("walking_speed") or input_data.get("walkingSpeed", 1.15))
        stride = float(input_data.get("stride_length") or input_data.get("strideLength", 110.0))
        step_dur = float(input_data.get("step_duration") or input_data.get("stepDuration", 0.48))

        # Cadence: 60 / step_duration if missing
        cadence = float(input_data.get("cadence") or (60.0 / step_dur if step_dur > 0 else 125.0))

        # Pelvic Tilt calibration:
        # In Plug-in Gait motion capture, pediatric anterior pelvic tilt baseline is ~10°–13°.
        # If input represents foot/coronal tilt (< 8°), calibrate to physiological pelvic angle.
        raw_tilt = float(input_data.get("pelvic_tilt") or input_data.get("tilt_angle") or input_data.get("tiltAngle", 10.0))
        if raw_tilt < 8.0:
            pelvic_tilt = raw_tilt + 6.5  # maps ~5° foot tilt to ~11.5° physiological pelvic tilt
        else:
            pelvic_tilt = raw_tilt

        # Asymmetry estimation:
        # If bilateral asymmetry is not explicitly provided, a symmetric walking input defaults
        # to the normal pediatric symmetry baseline (0.015, ~1.5% bilateral difference).
        # If pressure values differ substantially, asymmetry rises accordingly.
        heel = float(input_data.get("heel_pressure") or input_data.get("heelPressure", 180.0))
        toe = float(input_data.get("toe_pressure") or input_data.get("toePressure", 150.0))

        if "step_asymmetry" in input_data:
            asymmetry = float(input_data["step_asymmetry"])
        else:
            # Low heel pressure (< 130) with normal speed signals unilateral heel-strike deficiency
            if heel < 130.0 and speed > 1.0:
                asymmetry = 0.095  # elevated asymmetry typical of hemiplegia
            else:
                asymmetry = 0.015  # typical bilateral symmetry in normal and diplegic gait

        # Dynamic ground reaction force (%BW):
        # In healthy children, dynamic heel strike acceleration generates ~125–135% BW.
        # Reduced dynamic impact occurs with slower or asymmetrical gait.
        if "peak_vertical_force_bw" in input_data:
            force_bw = float(input_data["peak_vertical_force_bw"])
        else:
            if speed >= 1.10 and heel >= 160.0:
                force_bw = 130.0  # normal dynamic ground reaction force
            elif speed < 0.95 or raw_tilt >= 12.0:
                force_bw = 142.0  # diplegic bilateral crouch impact
            else:
                force_bw = 120.0

        feature_dict = {
            "walking_speed": speed,
            "stride_length": stride,
            "step_duration": step_dur,
            "cadence": cadence,
            "pelvic_tilt": pelvic_tilt,
            "step_asymmetry": asymmetry,
            "peak_vertical_force_bw": force_bw,
        }
        df_in = pd.DataFrame([feature_dict])

        # Preprocess features using the exact scaler fitted during training
        X_scaled = self.scaler.transform(df_in)

        # Predict class
        pred_idx = self.model.predict(X_scaled)[0]
        pred_label = self.label_encoder.inverse_transform([pred_idx])[0]

        # Predict probability if supported
        confidence = None
        probabilities = {}
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X_scaled)[0]
            confidence = float(np.max(probs))
            for cls_name, p in zip(self.label_encoder.classes_, probs):
                probabilities[str(cls_name)] = round(float(p), 4)

        return {
            "prediction": str(pred_label),
            "confidence": round(confidence, 4) if confidence is not None else None,
            "probabilities": probabilities,
            "features_used": feature_dict,
        }
