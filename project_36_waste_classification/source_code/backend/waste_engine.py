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
# 1. PyTorch Neural Architectures
# ─────────────────────────────────────────────────────────────────────────────
class WasteMaterialClassifierNet(nn.Module):
    def __init__(self, in_features=8, num_classes=6):
        super(WasteMaterialClassifierNet, self).__init__()
        self.fc1 = nn.Linear(in_features, 64)
        self.ln1 = nn.LayerNorm(64)
        self.relu = nn.ReLU()
        self.drop = nn.Dropout(0.15)

        self.res1 = nn.Linear(64, 64)
        self.ln_res1 = nn.LayerNorm(64)
        self.res2 = nn.Linear(64, 64)
        self.ln_res2 = nn.LayerNorm(64)

        self.fc2 = nn.Linear(64, 32)
        self.ln2 = nn.LayerNorm(32)
        self.out = nn.Linear(32, num_classes)

    def forward(self, x):
        x = self.drop(self.relu(self.ln1(self.fc1(x))))
        residual = x
        res = self.relu(self.ln_res1(self.res1(x)))
        res = self.ln_res2(self.res2(res))
        x = self.relu(residual + res)
        x = self.drop(self.relu(self.ln2(self.fc2(x))))
        return self.out(x)

class RecyclabilityScoreRegressorNet(nn.Module):
    def __init__(self, in_features=8):
        super(RecyclabilityScoreRegressorNet, self).__init__()
        self.shared = nn.Sequential(
            nn.Linear(in_features, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(64, 48),
            nn.LayerNorm(48),
            nn.ReLU()
        )
        self.head_recyc = nn.Sequential(
            nn.Linear(48, 24),
            nn.ReLU(),
            nn.Linear(24, 1)
        )
        self.head_contam = nn.Sequential(
            nn.Linear(48, 24),
            nn.ReLU(),
            nn.Linear(24, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        f = self.shared(x)
        recyc = self.head_recyc(f)
        contam = self.head_contam(f)
        return recyc, contam

# ─────────────────────────────────────────────────────────────────────────────
# 2. Waste Classification Inference Engine
# ─────────────────────────────────────────────────────────────────────────────
ITEM_PHYSICS_MAP = {
    # Plastic
    "plastic_bottle": {"density_g_cm3": 0.95, "spectral_reflectance_nir": 0.72, "opacity_pct": 35.0, "surface_roughness_um": 2.2, "moisture_content_pct": 2.5, "rigidity_modulus_gpa": 2.1, "magnetic_susceptibility": 0.01, "carbon_footprint_kg_co2": 2.8},
    "polyethylene_container": {"density_g_cm3": 0.96, "spectral_reflectance_nir": 0.70, "opacity_pct": 65.0, "surface_roughness_um": 2.8, "moisture_content_pct": 2.0, "rigidity_modulus_gpa": 2.4, "magnetic_susceptibility": 0.01, "carbon_footprint_kg_co2": 2.9},
    "pet_clamshell": {"density_g_cm3": 1.35, "spectral_reflectance_nir": 0.75, "opacity_pct": 15.0, "surface_roughness_um": 1.8, "moisture_content_pct": 1.5, "rigidity_modulus_gpa": 2.8, "magnetic_susceptibility": 0.01, "carbon_footprint_kg_co2": 3.1},
    # Glass
    "glass_bottle": {"density_g_cm3": 2.50, "spectral_reflectance_nir": 0.85, "opacity_pct": 22.0, "surface_roughness_um": 1.1, "moisture_content_pct": 1.2, "rigidity_modulus_gpa": 68.0, "magnetic_susceptibility": 0.01, "carbon_footprint_kg_co2": 1.1},
    "flint_jar": {"density_g_cm3": 2.52, "spectral_reflectance_nir": 0.88, "opacity_pct": 10.0, "surface_roughness_um": 0.9, "moisture_content_pct": 1.0, "rigidity_modulus_gpa": 70.0, "magnetic_susceptibility": 0.01, "carbon_footprint_kg_co2": 1.0},
    # Metal
    "aluminum_can": {"density_g_cm3": 2.70, "spectral_reflectance_nir": 0.94, "opacity_pct": 99.5, "surface_roughness_um": 3.8, "moisture_content_pct": 1.8, "rigidity_modulus_gpa": 69.0, "magnetic_susceptibility": 0.02, "carbon_footprint_kg_co2": 8.2},
    "tin_canister": {"density_g_cm3": 7.80, "spectral_reflectance_nir": 0.91, "opacity_pct": 99.8, "surface_roughness_um": 5.2, "moisture_content_pct": 2.0, "rigidity_modulus_gpa": 110.0, "magnetic_susceptibility": 0.88, "carbon_footprint_kg_co2": 9.5},
    # Paper
    "office_paper": {"density_g_cm3": 0.78, "spectral_reflectance_nir": 0.70, "opacity_pct": 89.0, "surface_roughness_um": 7.5, "moisture_content_pct": 6.2, "rigidity_modulus_gpa": 1.9, "magnetic_susceptibility": 0.01, "carbon_footprint_kg_co2": 1.4},
    "newspaper": {"density_g_cm3": 0.65, "spectral_reflectance_nir": 0.62, "opacity_pct": 92.0, "surface_roughness_um": 11.0, "moisture_content_pct": 7.5, "rigidity_modulus_gpa": 1.5, "magnetic_susceptibility": 0.01, "carbon_footprint_kg_co2": 1.2},
    # Cardboard
    "corrugated_box": {"density_g_cm3": 0.52, "spectral_reflectance_nir": 0.52, "opacity_pct": 98.5, "surface_roughness_um": 19.5, "moisture_content_pct": 8.5, "rigidity_modulus_gpa": 4.5, "magnetic_susceptibility": 0.01, "carbon_footprint_kg_co2": 1.2},
    "shipping_box": {"density_g_cm3": 0.55, "spectral_reflectance_nir": 0.54, "opacity_pct": 99.0, "surface_roughness_um": 21.0, "moisture_content_pct": 9.0, "rigidity_modulus_gpa": 4.8, "magnetic_susceptibility": 0.01, "carbon_footprint_kg_co2": 1.3},
    # Organic
    "food_scrap": {"density_g_cm3": 0.92, "spectral_reflectance_nir": 0.35, "opacity_pct": 96.0, "surface_roughness_um": 38.0, "moisture_content_pct": 62.0, "rigidity_modulus_gpa": 0.35, "magnetic_susceptibility": 0.01, "carbon_footprint_kg_co2": 0.6},
    "fruit_peel": {"density_g_cm3": 0.85, "spectral_reflectance_nir": 0.40, "opacity_pct": 92.0, "surface_roughness_um": 28.0, "moisture_content_pct": 58.0, "rigidity_modulus_gpa": 0.45, "magnetic_susceptibility": 0.01, "carbon_footprint_kg_co2": 0.5}
}

class WasteClassificationEngine:
    _instance = None

    def __init__(self):
        models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "models"))
        scalers_path = os.path.join(models_dir, "waste_scalers.json")
        clf_weights = os.path.join(models_dir, "waste_classifier_weights.pt")
        reg_weights = os.path.join(models_dir, "recyclability_regressor_weights.pt")

        with open(scalers_path, "r") as f:
            self.scalers = json.load(f)

        self.feature_cols = self.scalers["feature_cols"]
        self.means = self.scalers["means"]
        self.stds = self.scalers["stds"]
        self.categories = self.scalers["categories"]

        self.clf = WasteMaterialClassifierNet(in_features=8, num_classes=6)
        self.clf.load_state_dict(torch.load(clf_weights, map_location=torch.device("cpu")))
        self.clf.eval()

        self.reg = RecyclabilityScoreRegressorNet(in_features=8)
        self.reg.load_state_dict(torch.load(reg_weights, map_location=torch.device("cpu")))
        self.reg.eval()
        print("WasteClassificationEngine initialized with PyTorch models.")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = WasteClassificationEngine()
        return cls._instance

    def classify(self, item_type: str = "plastic_bottle", custom_features: dict = None, conveyor_id: str = "CONV-A1"):
        clean_key = str(item_type or "plastic_bottle").strip().lower().replace(" ", "_").replace("-", "_")
        physics = ITEM_PHYSICS_MAP.get(clean_key, ITEM_PHYSICS_MAP["plastic_bottle"]).copy()

        if custom_features:
            for k, v in custom_features.items():
                if k in physics and v is not None:
                    physics[k] = float(v)

        vec = [physics[col] for col in self.feature_cols]

        norm_vec = []
        for val, col in zip(vec, self.feature_cols):
            m = self.means[col]
            s = self.stds[col]
            norm_vec.append((val - m) / s)

        t_in = torch.tensor([norm_vec], dtype=torch.float32)

        with torch.no_grad():
            clf_logits = self.clf(t_in)
            probs = torch.softmax(clf_logits, dim=1).numpy()[0]
            pred_idx = int(np.argmax(probs))
            category = self.categories[pred_idx]
            confidence_pct = round(float(probs[pred_idx]) * 100.0, 2)

            pr, pc = self.reg(t_in)
            recyclability_score = float(np.clip(pr.numpy()[0][0], 0.0, 100.0))
            contamination_risk = float(np.clip(pc.numpy()[0][0], 0.0, 1.0))

        # Diversion Bin and Actuator Mapping
        bins_map = {
            "Plastic": "BIN-A (Blue - Optical Air Jet #1)",
            "Glass": "BIN-B (Teal - Mechanical Flipper #2)",
            "Metal": "BIN-C (Amber - Eddy Current Diverter #3)",
            "Paper": "BIN-D (Emerald - Pneumatic Suction #4)",
            "Cardboard": "BIN-E (Orange - Rotary Star Screen #5)",
            "Organic": "BIN-F (Lime - Bio-Compost Drop #6)"
        }
        diversion_bin = bins_map.get(category, "BIN-RESIDUAL (Landfill)")

        # Save to database
        conn = get_connection()
        cursor = conn.cursor()

        now_str = datetime.now(timezone.utc).isoformat()
        item_id = f"ITM-{uuid.uuid4().hex[:8].upper()}"

        cursor.execute("""
            INSERT INTO classified_items (
                item_id, conveyor_id, item_type, category, confidence_pct,
                density_g_cm3, spectral_reflectance_nir, opacity_pct,
                surface_roughness_um, moisture_content_pct, rigidity_modulus_gpa,
                magnetic_susceptibility, carbon_footprint_kg_co2,
                recyclability_score, contamination_risk, diversion_bin, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id, conveyor_id, clean_key, category, confidence_pct,
            physics["density_g_cm3"], physics["spectral_reflectance_nir"], physics["opacity_pct"],
            physics["surface_roughness_um"], physics["moisture_content_pct"], physics["rigidity_modulus_gpa"],
            physics["magnetic_susceptibility"], physics["carbon_footprint_kg_co2"],
            round(recyclability_score, 2), round(contamination_risk, 4), diversion_bin, now_str
        ))

        record_audit_log(cursor, "ITEM_CLASSIFICATION", "AI_SORTING_CORE", {
            "item_id": item_id,
            "conveyor_id": conveyor_id,
            "item_type": clean_key,
            "category": category,
            "confidence_pct": confidence_pct,
            "recyclability_score": round(recyclability_score, 2),
            "diversion_bin": diversion_bin
        })

        conn.commit()
        conn.close()

        return {
            "item_id": item_id,
            "conveyor_id": conveyor_id,
            "item_type": clean_key,
            "category": category,
            "confidence_pct": confidence_pct,
            "probabilities": {cat: round(float(p), 4) for cat, p in zip(self.categories, probs)},
            "density_g_cm3": physics["density_g_cm3"],
            "spectral_reflectance_nir": physics["spectral_reflectance_nir"],
            "opacity_pct": physics["opacity_pct"],
            "surface_roughness_um": physics["surface_roughness_um"],
            "moisture_content_pct": physics["moisture_content_pct"],
            "rigidity_modulus_gpa": physics["rigidity_modulus_gpa"],
            "magnetic_susceptibility": physics["magnetic_susceptibility"],
            "carbon_footprint_kg_co2": physics["carbon_footprint_kg_co2"],
            "recyclability_score": round(recyclability_score, 2),
            "contamination_risk": round(contamination_risk, 4),
            "diversion_bin": diversion_bin,
            "actuator_action": f"ACTUATE: Pneumatically route to {diversion_bin}",
            "timestamp": now_str,
            "model": "PyTorch Residual Material Classifier & Dual-Head Recyclability Regressor"
        }
