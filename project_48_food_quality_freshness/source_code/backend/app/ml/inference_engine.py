import os
import json
import time
import hashlib
import torch
import numpy as np
from backend.app.ml.spectral_freshness_model import SpectralFreshnessCNN
from backend.app.ml.regressor_model import ShelfLifeForecastRegressorNet
from backend.app.core.config import settings

STAGES = ["STAGE_1_FRESH", "STAGE_2_MARGINAL", "STAGE_3_DETERIORATED"]

class FoodFreshnessEngine:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
        
        # 1. Load CNN Model
        self.cnn_model = SpectralFreshnessCNN().to(self.device)
        weights_cnn = settings.CNN_MODEL_WEIGHTS_PATH if os.path.exists(settings.CNN_MODEL_WEIGHTS_PATH) else settings.MODEL_WEIGHTS_PATH
        if os.path.exists(weights_cnn):
            try:
                self.cnn_model.load_state_dict(torch.load(weights_cnn, map_location=self.device))
                print(f" Loaded SpectralFreshnessCNN weights from {weights_cnn}")
            except Exception as e:
                print(f" CNN weights load error: {e}")
        self.cnn_model.eval()
        
        # 2. Load Regressor Model
        self.reg_model = ShelfLifeForecastRegressorNet(input_dim=10, hidden_dim=64).to(self.device)
        if os.path.exists(settings.REGRESSOR_WEIGHTS_PATH):
            try:
                self.reg_model.load_state_dict(torch.load(settings.REGRESSOR_WEIGHTS_PATH, map_location=self.device))
                print(f" Loaded ShelfLifeForecastRegressorNet weights from {settings.REGRESSOR_WEIGHTS_PATH}")
            except Exception as e:
                print(f" Regressor weights load error: {e}")
        self.reg_model.eval()
        
        # 3. Load Scalers
        self.scalers = None
        if os.path.exists(settings.SCALERS_PATH):
            try:
                with open(settings.SCALERS_PATH, "r") as f:
                    self.scalers = json.load(f)
            except Exception as e:
                print(f" Scalers load warning: {e}")

    def evaluate_item(self, img_rgb: np.ndarray, telemetry: dict = None, simulate_spoilage: bool = False):
        t0 = time.time()
        
        # Prepare image tensor
        if img_rgb.ndim == 3 and img_rgb.shape[0] != 3 and img_rgb.shape[2] == 3:
            img_rgb = np.transpose(img_rgb, (2, 0, 1))
        t_img = torch.tensor(img_rgb, dtype=torch.float32)
        if t_img.ndim == 3:
            t_img = t_img.unsqueeze(0)
        t_img = t_img.to(self.device)
        
        if simulate_spoilage:
            t_img[:, 0, 15:45, 15:45] = 0.92 # Browning
            t_img[:, 1:, 15:45, 15:45] = 0.08
            
        # CNN Forward Pass
        with torch.no_grad():
            cnn_score_t, cnn_shelf_t, stage_logits = self.cnn_model(t_img)
            cnn_score = float(torch.clamp(cnn_score_t, 0.0, 100.0).cpu().item())
            cnn_shelf_h = float(torch.clamp(cnn_shelf_t, 0.0, 240.0).cpu().item())
            stage_idx = int(torch.argmax(stage_logits, dim=1).cpu().item())
            deterioration_stage = STAGES[stage_idx]

        # Prepare 10-D Telemetry Feature Vector
        tel = telemetry or {}
        if simulate_spoilage:
            default_temp = 9.8
            default_hum = 92.0
            default_dur = 144.0
            default_brown = 18.5
            default_tvbn = 32.4
            default_ph = 7.1
            default_eth = 12.0
            default_moist = 88.0
            default_cfu = 6.8
            default_refl = 0.45
        else:
            default_temp = 3.2
            default_hum = 84.0
            default_dur = 24.0
            default_brown = 1.2
            default_tvbn = 8.5
            default_ph = 5.8
            default_eth = 0.2
            default_moist = 72.0
            default_cfu = 2.4
            default_refl = 1.45

        raw_features = np.array([
            tel.get("storage_temp_c", default_temp),
            tel.get("relative_humidity_pct", default_hum),
            tel.get("storage_duration_hours", default_dur),
            tel.get("browning_index", default_brown),
            tel.get("tvbn_mg_per_100g", default_tvbn),
            tel.get("ph_level", default_ph),
            tel.get("ethylene_concentration_ppm", default_eth),
            tel.get("moisture_content_pct", default_moist),
            tel.get("bacterial_log_cfu_g", default_cfu),
            tel.get("reflectance_ratio_650_850", default_refl)
        ], dtype=np.float32)

        # Normalize features
        if self.scalers:
            means = np.array(self.scalers["means"], dtype=np.float32)
            stds = np.array(self.scalers["stds"], dtype=np.float32)
            norm_features = (raw_features - means) / stds
        else:
            norm_features = raw_features

        x_reg = torch.tensor(norm_features, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        # Regressor Forward Pass
        with torch.no_grad():
            preds = self.reg_model(x_reg).cpu().numpy()[0]
            shelf_life_days = float(np.clip(preds[0], 0.0, 21.0))
            spoilage_risk_pct = float(np.clip(preds[1], 0.0, 100.0))
            microbial_risk_pct = float(np.clip(preds[2], 0.0, 100.0))
            cold_chain_comp = float(np.clip(preds[3], 0.0, 100.0))

        # Determine Recommendation
        if deterioration_stage == "STAGE_1_FRESH" and spoilage_risk_pct < 35.0:
            rec = "OPTIMAL_RETAIL_SALE"
        elif deterioration_stage == "STAGE_2_MARGINAL" or (spoilage_risk_pct >= 35.0 and spoilage_risk_pct < 65.0):
            rec = "PRIORITY_DISCOUNT_SALE"
        else:
            rec = "DISCARD_COMPOSTING"

        latency_ms = round((time.time() - t0) * 1000.0, 2)
        
        # Evidence hash
        evidence_payload = f"{time.time()}:{cnn_score:.2f}:{deterioration_stage}:{shelf_life_days:.2f}:{spoilage_risk_pct:.2f}:{raw_features.tolist()}"
        evidence_hash = hashlib.sha256(evidence_payload.encode("utf-8")).hexdigest()

        return {
            "freshness_score": round(cnn_score, 1),
            "deterioration_stage": deterioration_stage,
            "estimated_shelf_life_hours": round(cnn_shelf_h, 1),
            "remaining_shelf_life_days": round(shelf_life_days, 1),
            "spoilage_risk_pct": round(spoilage_risk_pct, 1),
            "microbial_risk_pct": round(microbial_risk_pct, 1),
            "cold_chain_compliance_score": round(cold_chain_comp, 1),
            "browning_index": round(float(raw_features[3]), 2),
            "spoilage_area_pct": round(float(raw_features[3] * 0.8), 2) if raw_features[3] > 4.0 else 0.0,
            "storage_temp_c": round(float(raw_features[0]), 2),
            "relative_humidity_pct": round(float(raw_features[1]), 2),
            "tvbn_mg_per_100g": round(float(raw_features[4]), 2),
            "ph_level": round(float(raw_features[5]), 2),
            "ethylene_concentration_ppm": round(float(raw_features[6]), 3),
            "bacterial_log_cfu_g": round(float(raw_features[8]), 2),
            "recommendation": rec,
            "advisory_note": f"{rec.replace('_', ' ')}: {shelf_life_days:.1f} days remaining at {raw_features[0]:.1f}°C",
            "evidence_hash": evidence_hash,
            "latency_ms": latency_ms
        }

freshness_engine = FoodFreshnessEngine()
