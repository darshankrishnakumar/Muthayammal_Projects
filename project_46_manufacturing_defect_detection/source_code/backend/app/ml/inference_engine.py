import torch
import numpy as np
import os
import json
import hashlib
from backend.app.ml.fpn_defect_model import DeepFPNDefectNet
from backend.app.ml.regressor_model import ManufacturingDefectRiskRegressorNet
from backend.app.core.config import settings

PART_TYPES = ["PCB_BOARD", "MACHINED_GEAR", "METALLIC_CASING", "TURBINE_BLADE"]
DEFECT_TYPES = ["NONE", "SCRATCH", "CRACK", "DENT", "MISSING_COMPONENT"]

class ManufacturingInferenceEngine:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
        
        # 1. Load FPN Model
        self.fpn_model = DeepFPNDefectNet(num_defect_classes=5).to(self.device)
        if os.path.exists(settings.MODEL_WEIGHTS_PATH):
            try:
                self.fpn_model.load_state_dict(torch.load(settings.MODEL_WEIGHTS_PATH, map_location=self.device))
            except Exception as e:
                print(f"DeepFPNDefectNet weights load error: {e}")
        self.fpn_model.eval()

        # 2. Load Multi-Target Regressor Model
        self.reg_model = ManufacturingDefectRiskRegressorNet(in_features=10).to(self.device)
        if os.path.exists(settings.REGRESSOR_WEIGHTS_PATH):
            try:
                self.reg_model.load_state_dict(torch.load(settings.REGRESSOR_WEIGHTS_PATH, map_location=self.device))
            except Exception as e:
                print(f"ManufacturingDefectRiskRegressorNet weights load error: {e}")
        self.reg_model.eval()

        # 3. Load Scalers
        self.scalers = None
        if os.path.exists(settings.SCALERS_PATH):
            with open(settings.SCALERS_PATH, "r") as f:
                self.scalers = json.load(f)

    def inspect_part(self, img_rgb: np.ndarray, part_type: str = "PCB_BOARD", simulate_defect: str = "NONE", assembly_line: str = "Line-1 SMT PCB Assembly"):
        # Image tensor [1, 3, 64, 64]
        t = torch.tensor(img_rgb, dtype=torch.float32).to(self.device)
        if t.ndim == 3:
            t = t.unsqueeze(0)
        
        if simulate_defect != "NONE":
            # Inject localized defect artifact into simulated optical sensor
            t[:, :, 24:36, 24:36] = 0.08

        with torch.no_grad():
            seg_out, cls_out = self.fpn_model(t)
            probs = torch.softmax(cls_out, dim=-1)[0].cpu().numpy()

        p_idx = PART_TYPES.index(part_type) if part_type in PART_TYPES else 0
        d_idx = DEFECT_TYPES.index(simulate_defect) if simulate_defect in DEFECT_TYPES else 0
        is_rej = 1.0 if simulate_defect != "NONE" else 0.0

        # Raw synthetic proxy features for regressor input normalization
        if is_rej:
            raw_sev = 82.5
            raw_area = 7.4
            raw_rough = 4.8
            raw_eject = 95.0
            ctime = 12.4
            conf = float(probs[d_idx] if d_idx < len(probs) else 0.965)
        else:
            raw_sev = 1.8
            raw_area = 0.05
            raw_rough = 0.95
            raw_eject = 2.1
            ctime = 11.2
            conf = float(probs[0])

        feats = [
            float(p_idx),
            float(d_idx),
            float(is_rej),
            raw_sev,
            raw_area,
            raw_rough,
            raw_eject,
            ctime,
            conf,
            float(is_rej * 10.0 + raw_sev * 0.1)
        ]

        # Normalize with scalers
        if self.scalers:
            means = np.array(self.scalers["mean"], dtype=np.float32)
            stds = np.array(self.scalers["std"], dtype=np.float32)
            feats_norm = (np.array(feats, dtype=np.float32) - means) / stds
        else:
            feats_norm = np.array(feats, dtype=np.float32)

        feat_tensor = torch.tensor(feats_norm, dtype=torch.float32).unsqueeze(0).to(self.device)
        with torch.no_grad():
            p_sev, p_area, p_rough, p_eject = self.reg_model(feat_tensor)
            sev_val = round(float(p_sev[0, 0].item()), 2)
            area_val = round(float(p_area[0, 0].item()), 2)
            rough_val = round(float(p_rough[0, 0].item()), 2)
            eject_val = round(float(p_eject[0, 0].item()), 2)

        verdict = "REJECT" if (simulate_defect != "NONE" or sev_val > 40.0 or area_val > 2.5 or eject_val > 50.0) else "PASS"
        defect_type = simulate_defect if verdict == "REJECT" else "NONE"
        actuator = "TRIGGER_PNEUMATIC_EJECT" if verdict == "REJECT" else "ROUTE_CONVEYOR"

        # Deterministic SHA-256 evidence hash
        hash_payload = f"{part_type}:{assembly_line}:{verdict}:{defect_type}:{sev_val}:{area_val}:{rough_val}:{eject_val}"
        evidence_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

        return {
            "inspection_verdict": verdict,
            "defect_type": defect_type,
            "severity_score": sev_val,
            "defect_area_pct": area_val,
            "surface_roughness_ra": rough_val,
            "pneumatic_ejection_confidence": eject_val,
            "actuator_action": actuator,
            "confidence": round(conf if verdict == "PASS" else max(0.95, conf), 3),
            "cycle_time_ms": ctime,
            "evidence_hash": evidence_hash
        }

mfg_engine = ManufacturingInferenceEngine()
