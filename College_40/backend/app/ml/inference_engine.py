import torch
import numpy as np
import os
from backend.app.ml.dual_stream_fire_model import DualStreamFireSmokeNet
from backend.app.core.config import settings

HAZARD_CLASSES = ["NORMAL", "SMOKE_DETECTED", "FLAME_DETECTED", "DUAL_FIRE_SMOKE_HAZARD"]

class FireInferenceEngine:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
        self.model = DualStreamFireSmokeNet().to(self.device)
        if os.path.exists(settings.MODEL_WEIGHTS_PATH):
            try:
                self.model.load_state_dict(torch.load(settings.MODEL_WEIGHTS_PATH, map_location=self.device))
            except Exception as e:
                print(f"Fire weights load error: {e}")
        self.model.eval()

    def inspect_surveillance(self, img_np: np.ndarray, flicker_profile: np.ndarray):
        img_t = torch.tensor(img_np, dtype=torch.float32).unsqueeze(0).to(self.device)
        flicker_t = torch.tensor(flicker_profile, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(img_t, flicker_t)
            probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()
            pred_idx = int(np.argmax(probs))
            conf = float(probs[pred_idx])

        hazard = HAZARD_CLASSES[pred_idx]
        if pred_idx == 3:
            tier = "TIER_3_CRITICAL"
        elif pred_idx == 2:
            tier = "TIER_2_ACTIVE"
        elif pred_idx == 1:
            tier = "TIER_1_EARLY"
        else:
            tier = "NONE"

        return {
            "hazard_type": hazard,
            "severity_tier": tier,
            "confidence": round(conf, 3),
            "is_emergency": pred_idx != 0,
            "flicker_hz": round(float(np.argmax(flicker_profile) * 2.5 + 4.0), 1)
        }

fire_engine = FireInferenceEngine()
