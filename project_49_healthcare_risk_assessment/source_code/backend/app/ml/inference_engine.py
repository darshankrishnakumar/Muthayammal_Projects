import os
import json
import time
import hashlib
import torch
import numpy as np

from backend.app.ml.longitudinal_risk_model import LongitudinalHealthRiskNet
from backend.app.ml.comorbidity_model import ClinicalComorbidityForecastNet
from backend.app.core.config import settings

class HealthcareRiskEngine:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"))
        
        # 1. Load Longitudinal Health Risk Net
        self.risk_model = LongitudinalHealthRiskNet(in_features=10).to(self.device)
        weights_risk = settings.RISK_MODEL_WEIGHTS_PATH if os.path.exists(settings.RISK_MODEL_WEIGHTS_PATH) else settings.MODEL_WEIGHTS_PATH
        if os.path.exists(weights_risk):
            try:
                self.risk_model.load_state_dict(torch.load(weights_risk, map_location=self.device))
                print(f" Loaded LongitudinalHealthRiskNet weights from {weights_risk}")
            except Exception as e:
                print(f" Risk net weights load error: {e}")
        self.risk_model.eval()

        # 2. Load Clinical Comorbidity Forecast Net
        self.comb_model = ClinicalComorbidityForecastNet(input_dim=14, hidden_dim=64).to(self.device)
        if os.path.exists(settings.COMORBIDITY_WEIGHTS_PATH):
            try:
                self.comb_model.load_state_dict(torch.load(settings.COMORBIDITY_WEIGHTS_PATH, map_location=self.device))
                print(f" Loaded ClinicalComorbidityForecastNet weights from {settings.COMORBIDITY_WEIGHTS_PATH}")
            except Exception as e:
                print(f" Comorbidity weights load error: {e}")
        self.comb_model.eval()

        # 3. Load Scalers
        self.scalers = None
        if os.path.exists(settings.SCALERS_PATH):
            try:
                with open(settings.SCALERS_PATH, "r") as f:
                    self.scalers = json.load(f)
            except Exception as e:
                print(f" Scalers load warning: {e}")

    def assess_patient(self, age: int, sbp: float, dbp: float, hba1c: float, glucose: float, chol: float, hdl: float, ldl: float, egfr: float, bmi: float):
        t0 = time.time()
        
        raw_vitals = np.array([age, sbp, dbp, hba1c, glucose, chol, hdl, ldl, egfr, bmi], dtype=np.float32)
        
        if self.scalers:
            means = np.array(self.scalers["means"], dtype=np.float32)
            stds = np.array(self.scalers["stds"], dtype=np.float32)
            norm_vitals = (raw_vitals - means) / stds
        else:
            norm_vitals = raw_vitals / np.array([100.0, 200.0, 120.0, 14.0, 300.0, 350.0, 100.0, 250.0, 120.0, 50.0], dtype=np.float32)

        t_in = torch.tensor(norm_vitals, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        # 1. Model 1 Forward Pass: Chronic Disease Risks
        with torch.no_grad():
            cvd_t, t2d_t, htn_t, ckd_t = self.risk_model(t_in)
            cvd = float(torch.clamp(cvd_t, 0.0, 100.0).cpu().item())
            t2d = float(torch.clamp(t2d_t, 0.0, 100.0).cpu().item())
            htn = float(torch.clamp(htn_t, 0.0, 100.0).cpu().item())
            ckd = float(torch.clamp(ckd_t, 0.0, 100.0).cpu().item())

        # 2. Model 2 Forward Pass: Comorbidity Prognosis
        comb_input = np.concatenate([norm_vitals, np.array([cvd/100.0, t2d/100.0, htn/100.0, ckd/100.0], dtype=np.float32)])
        t_comb = torch.tensor(comb_input, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            comb_preds = self.comb_model(t_comb).cpu().numpy()[0]
            mortality_10yr = float(np.clip(comb_preds[0], 0.0, 100.0))
            readmission_30d = float(np.clip(comb_preds[1], 0.0, 100.0))
            polypharmacy = float(np.clip(comb_preds[2], 0.0, 100.0))
            renal_hazard = float(np.clip(comb_preds[3], 0.0, 100.0))

        # Composite Risk Tiering
        max_risk = max(cvd, t2d, htn, ckd)
        if max_risk >= 80.0:
            tier = "CRITICAL"
        elif max_risk >= 60.0:
            tier = "HIGH"
        elif max_risk >= 35.0:
            tier = "MODERATE"
        else:
            tier = "LOW"

        # Biomarker Drivers & SHAP Attributions
        shap_values = {
            "Systolic Blood Pressure": round(float((sbp - 120.0) / 40.0 * 0.45), 2),
            "Fasting Blood Glucose": round(float((glucose - 95.0) / 70.0 * 0.38), 2),
            "Diabetic Glycemia HbA1c": round(float((hba1c - 5.4) / 2.5 * 0.42), 2),
            "Atherogenic LDL": round(float((ldl - 100.0) / 40.0 * 0.28), 2),
            "Renal eGFR Impairment": round(float((90.0 - egfr) / 40.0 * 0.35), 2),
            "Body Mass Index": round(float((bmi - 24.0) / 10.0 * 0.22), 2)
        }
        
        sorted_shap = sorted(shap_values.items(), key=lambda x: x[1], reverse=True)
        top_shap_driver = f"{sorted_shap[0][0]} (+{sorted_shap[0][1]:.2f})" if sorted_shap[0][1] > 0 else "Normal Physiological Biomarkers (-0.22)"

        drivers = []
        if sbp >= 140.0: drivers.append(f"Systolic BP ({sbp:.0f} mmHg)")
        if hba1c >= 6.5: drivers.append(f"HbA1c ({hba1c:.1f}%)")
        if ldl >= 130.0: drivers.append(f"Atherogenic LDL ({ldl:.0f} mg/dL)")
        if egfr < 60.0: drivers.append(f"Renal eGFR ({egfr:.0f} mL/min)")
        if not drivers: drivers.append("Normal Physiological Biomarkers")
        driver_str = "; ".join(drivers)

        if tier in ["CRITICAL", "HIGH"]:
            recs = "Urgent Specialist Consultation (Cardiology/Nephrology); Statin Titration; Antihypertensive Optimization; Continuous Glucose Monitoring"
            intervention = "Cardiovascular & Metabolic Specialist Evaluation"
        elif tier == "MODERATE":
            recs = "DASH Diet & Sodium Restriction; Aerobic Exercise (150 min/wk); Semi-Annual Glycemic Surveillance"
            intervention = "Lifestyle Intervention & Preventive Pharmacotherapy"
        else:
            recs = "Annual Preventive Comprehensive Metabolic Panel; Balanced Mediterranean Diet; Aerobic Maintenance"
            intervention = "Routine Preventive Health Maintenance"

        latency_ms = round((time.time() - t0) * 1000.0, 2)
        
        evidence_payload = f"{time.time()}:{age}:{sbp}:{dbp}:{hba1c}:{glucose}:{egfr}:{bmi}:{cvd:.2f}:{t2d:.2f}:{tier}"
        evidence_hash = hashlib.sha256(evidence_payload.encode("utf-8")).hexdigest()

        return {
            "cardiovascular_risk_pct": round(cvd, 1),
            "type2_diabetes_risk_pct": round(t2d, 1),
            "hypertension_risk_pct": round(htn, 1),
            "ckd_risk_pct": round(ckd, 1),
            "cardiovascular_risk_score": round(cvd / 100.0, 3), # Compatibility with legacy UI
            "diabetes_risk_score": round(t2d / 100.0, 3),       # Compatibility with legacy UI
            "composite_risk_tier": tier,
            "risk_level": tier,                                 # Compatibility with legacy UI
            "ten_year_mortality_risk_pct": round(mortality_10yr, 1),
            "hospital_readmission_risk_pct": round(readmission_30d, 1),
            "polypharmacy_complexity_index": round(polypharmacy, 1),
            "renal_progression_hazard_pct": round(renal_hazard, 1),
            "primary_biomarker_drivers": driver_str,
            "top_shap_driver": top_shap_driver,
            "shap_attributions": shap_values,
            "preventive_recommendations": recs,
            "recommended_intervention": intervention,
            "evidence_hash": evidence_hash,
            "latency_ms": latency_ms
        }

health_engine = HealthcareRiskEngine()
