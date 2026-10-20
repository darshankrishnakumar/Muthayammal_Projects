import os
import sys
import unittest
import torch
import numpy as np
from fastapi.testclient import TestClient

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.session import init_db, SessionLocal
from backend.app.db.models import EnergyOptimizationPlan, AuditLedger
from backend.app.ml.lstm_energy_model import MultiHorizonEnergyLSTM
from backend.app.ml.grid_regressor_model import GridPeakAndCarbonEmissionRegressorNet
from backend.app.ml.inference_engine import energy_engine

class TestProject51CompleteSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    # 1. Project Deliverables Tests
    def test_01_requirements_file_exists(self):
        req_path = os.path.join(BASE_DIR, "..", "requirements.txt")
        self.assertTrue(os.path.isfile(req_path), "requirements.txt must exist")

    def test_02_env_example_file_exists(self):
        env_path = os.path.join(BASE_DIR, "..", ".env.example")
        self.assertTrue(os.path.isfile(env_path), ".env.example must exist")

    def test_03_walkthrough_script_exists(self):
        wt_path = os.path.join(BASE_DIR, "..", "walkthrough", "walkthrough_script.md")
        self.assertTrue(os.path.isfile(wt_path), "walkthrough_script.md must exist")

    def test_04_dataset_6000_exists(self):
        csv_path = os.path.join(BASE_DIR, "data", "energy_telemetry_6000.csv")
        self.assertTrue(os.path.isfile(csv_path), "data/energy_telemetry_6000.csv must exist")

    def test_05_weights_lstm_exists(self):
        w_path = os.path.join(BASE_DIR, "backend", "models", "multi_horizon_lstm_weights.pt")
        self.assertTrue(os.path.isfile(w_path), "multi_horizon_lstm_weights.pt must exist")

    def test_06_weights_regressor_exists(self):
        w_path = os.path.join(BASE_DIR, "backend", "models", "grid_regressor_weights.pt")
        self.assertTrue(os.path.isfile(w_path), "grid_regressor_weights.pt must exist")

    def test_07_metadata_json_exists(self):
        meta_path = os.path.join(BASE_DIR, "backend", "models", "model_metadata.json")
        self.assertTrue(os.path.isfile(meta_path), "model_metadata.json must exist")

    def test_08_scalers_json_exists(self):
        scalers_path = os.path.join(BASE_DIR, "backend", "models", "energy_scalers.json")
        self.assertTrue(os.path.isfile(scalers_path), "energy_scalers.json must exist")

    # 2. Health & Gateway Tests
    def test_09_health_endpoint_status(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertEqual(data["project_id"], "PROJECT-051")
        self.assertEqual(data["port"], 5051)
        self.assertTrue(data["database_wal_mode"], "Database must be in SQLite WAL mode")

    def test_10_health_models_parameters(self):
        res = self.client.get("/api/health/")
        data = res.json()
        models = data["models"]
        self.assertGreater(models["lstm_parameters"], 140000)
        self.assertGreater(models["grid_regressor_parameters"], 10000)
        self.assertGreater(models["total_parameters"], 150000)

    # 3. Analytics Endpoint Tests
    def test_11_analytics_summary(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total_dispatch_plans"], 6000)
        self.assertGreater(data["mean_peak_shaving_pct"], 15.0)
        self.assertGreater(data["total_daily_savings_usd"], 10000.0)
        self.assertEqual(data["model_performance"]["mape_pct"], 3.42)
        self.assertEqual(data["model_performance"]["rmse_kwh"], 12.8)

    def test_12_analytics_breakdown(self):
        res = self.client.get("/api/analytics/summary")
        data = res.json()
        b_down = data["facility_breakdown"]
        self.assertIn("COMMERCIAL_OFFICE_CAMPUS", b_down)
        self.assertIn("INDUSTRIAL_MANUFACTURING_PLANT", b_down)
        self.assertIn("DATA_CENTER_HYPERSCALE", b_down)
        self.assertIn("MUNICIPAL_HOSPITAL_COMPLEX", b_down)

    # 4. Presets Endpoint Tests
    def test_13_presets_availability(self):
        res = self.client.get("/api/energy/presets")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        presets = data["presets"]
        self.assertEqual(len(presets), 4)
        preset_ids = [p["id"] for p in presets]
        self.assertIn("tech_campus", preset_ids)
        self.assertIn("auto_assembly", preset_ids)
        self.assertIn("cloud_datacenter", preset_ids)
        self.assertIn("metro_hospital", preset_ids)

    # 5. Plans Retrieval Tests
    def test_14_plans_pagination(self):
        res = self.client.get("/api/energy/plans?skip=0&limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["count"], 10)
        self.assertGreaterEqual(data["total"], 6000)
        self.assertEqual(len(data["plans"]), 10)

    def test_15_plans_filtering_by_archetype(self):
        res = self.client.get("/api/energy/plans?facility_archetype=COMMERCIAL_OFFICE_CAMPUS&limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        for p in data["plans"]:
            self.assertEqual(p["facility_archetype"], "COMMERCIAL_OFFICE_CAMPUS")

    # 6. Optimization & Dual Model Forward Inference Tests
    def test_16_optimize_tech_campus(self):
        payload = {
            "building_facility": "Tech Campus Science Complex A",
            "facility_archetype": "COMMERCIAL_OFFICE_CAMPUS",
            "base_load_kw": 480.0,
            "ambient_temp_c": 26.5,
            "relative_humidity_pct": 58.0,
            "tou_tariff_cents_kwh": 18.5,
            "renewable_penetration_pct": 35.0
        }
        res = self.client.post("/api/energy/optimize", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        m = data["metrics"]
        self.assertEqual(len(m["forecast_24h"]), 24)
        self.assertEqual(len(m["optimized_24h"]), 24)
        self.assertGreater(m["forecasted_peak_kwh"], 0)
        self.assertGreater(m["optimized_peak_kwh"], 0)
        self.assertGreater(m["peak_shaving_reduction_pct"], 10.0)
        self.assertGreater(m["estimated_daily_savings_usd"], 0)
        self.assertEqual(len(m["evidence_hash"]), 64)

    def test_17_optimize_industrial_plant(self):
        payload = {
            "building_facility": "Automotive Stamping Assembly 4",
            "facility_archetype": "INDUSTRIAL_MANUFACTURING_PLANT",
            "base_load_kw": 850.0,
            "ambient_temp_c": 28.0,
            "relative_humidity_pct": 52.0,
            "tou_tariff_cents_kwh": 22.0,
            "renewable_penetration_pct": 24.0
        }
        res = self.client.post("/api/energy/optimize", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        m = data["metrics"]
        self.assertGreater(m["forecasted_peak_kwh"], 500.0)
        self.assertGreater(m["estimated_daily_savings_usd"], 100.0)

    def test_18_optimize_custom_features(self):
        payload = {
            "building_facility": "Hyperscale Cloud Facility DC-2",
            "facility_archetype": "DATA_CENTER_HYPERSCALE",
            "base_load_kw": 1200.0,
            "ambient_temp_c": 21.0,
            "relative_humidity_pct": 45.0,
            "tou_tariff_cents_kwh": 14.2,
            "renewable_penetration_pct": 48.0,
            "custom_features": {
                "ambient_temp_c": 21.0,
                "relative_humidity_pct": 45.0,
                "solar_irradiance_wm2": 620.0,
                "wind_speed_ms": 6.5,
                "occupancy_rate": 0.95,
                "base_load_kw": 1200.0,
                "ev_charging_load_kw": 150.0,
                "tou_tariff_cents_kwh": 14.2,
                "renewable_penetration_pct": 48.0,
                "grid_frequency_hz": 60.001
            }
        }
        res = self.client.post("/api/energy/optimize", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        m = data["metrics"]
        self.assertGreater(m["optimized_peak_kwh"], 0)

    # 7. Cryptographic Audit Ledger Tests
    def test_19_audit_ledger_genesis_block(self):
        res = self.client.get("/api/energy/audit-logs?limit=200")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["chain_valid"], "SHA-256 block hash chain must be 100% valid")
        self.assertGreaterEqual(data["total_blocks"], 150)
        db = SessionLocal()
        genesis = db.query(AuditLedger).filter(AuditLedger.block_index == 0).first()
        self.assertIsNotNone(genesis)
        self.assertEqual(genesis.event_type, "GENESIS_BLOCK")
        self.assertEqual(genesis.previous_hash, "0000000000000000000000000000000000000000000000000000000000000000")
        self.assertEqual(len(genesis.block_hash), 64)
        db.close()

    def test_20_audit_ledger_continuous_chaining(self):
        db = SessionLocal()
        blocks = db.query(AuditLedger).order_by(AuditLedger.block_index.asc()).limit(50).all()
        for i in range(1, len(blocks)):
            self.assertEqual(blocks[i].previous_hash, blocks[i-1].block_hash, f"Block {i} previous hash mismatch")
        db.close()

    def test_21_optimize_appends_audit_block(self):
        res_before = self.client.get("/api/energy/audit-logs?limit=5")
        count_before = res_before.json()["total_blocks"]

        payload = {
            "building_facility": "Metro General Healthcare Complex",
            "facility_archetype": "MUNICIPAL_HOSPITAL_COMPLEX",
            "base_load_kw": 620.0,
            "ambient_temp_c": 25.0,
            "relative_humidity_pct": 60.0,
            "tou_tariff_cents_kwh": 19.8,
            "renewable_penetration_pct": 30.0
        }
        res = self.client.post("/api/energy/optimize", json=payload)
        self.assertEqual(res.status_code, 200)
        block = res.json()["audit_block"]
        self.assertGreater(block["block_index"], 0)
        self.assertEqual(len(block["block_hash"]), 64)

        res_after = self.client.get("/api/energy/audit-logs?limit=5")
        self.assertEqual(res_after.json()["total_blocks"], count_before + 1)

    # 8. Neural Model Unit Tests
    def test_22_lstm_forward_pass_shape(self):
        model = MultiHorizonEnergyLSTM(in_features=5, hidden_dim=64, horizon=24)
        dummy = torch.randn(4, 24, 5)
        out = model(dummy)
        self.assertEqual(out.shape, (4, 24))

    def test_23_lstm_parameter_count(self):
        model = MultiHorizonEnergyLSTM(in_features=5, hidden_dim=64, horizon=24)
        p = sum(p.numel() for p in model.parameters() if p.requires_grad)
        self.assertEqual(p, 145496)

    def test_24_grid_regressor_forward_pass_keys(self):
        model = GridPeakAndCarbonEmissionRegressorNet()
        dummy = torch.randn(3, 12)
        out = model(dummy)
        self.assertIn("forecasted_peak_kwh", out)
        self.assertIn("grid_stress_index", out)
        self.assertIn("carbon_intensity_gco2", out)
        self.assertIn("curtailment_risk_prob", out)
        self.assertIn("peak_shaving_potential_pct", out)

    def test_25_grid_regressor_output_ranges(self):
        model = GridPeakAndCarbonEmissionRegressorNet()
        model.eval()
        dummy = torch.randn(5, 12)
        with torch.no_grad():
            out = model(dummy)
            stress = out["grid_stress_index"].squeeze()
            curt = out["curtailment_risk_prob"].squeeze()
            shave = out["peak_shaving_potential_pct"].squeeze()

            self.assertTrue((stress >= 0.0).all() and (stress <= 100.0).all())
            self.assertTrue((curt >= 0.0).all() and (curt <= 1.0).all())
            self.assertTrue((shave >= 0.0).all() and (shave <= 40.0).all())

    def test_26_grid_regressor_parameter_count(self):
        model = GridPeakAndCarbonEmissionRegressorNet()
        p = sum(p.numel() for p in model.parameters() if p.requires_grad)
        self.assertEqual(p, 12613)

    # 9. Database ACID & Integrity Tests
    def test_27_database_wal_pragma_verified(self):
        from sqlalchemy import text
        db = SessionLocal()
        res = db.execute(text("PRAGMA journal_mode;")).fetchone()
        self.assertEqual(str(res[0]).lower(), "wal")
        db.close()

    def test_28_database_total_rows_at_least_6000(self):
        db = SessionLocal()
        cnt = db.query(EnergyOptimizationPlan).count()
        self.assertGreaterEqual(cnt, 6000)
        db.close()

    def test_29_database_no_null_evidence_hashes(self):
        db = SessionLocal()
        null_hashes = db.query(EnergyOptimizationPlan).filter(EnergyOptimizationPlan.evidence_hash.is_(None)).count()
        self.assertEqual(null_hashes, 0)
        db.close()

    def test_30_synthesizes_valid_sequence(self):
        t = energy_engine.synthesize_past_sequence(500.0, 25.0, 15.0)
        self.assertEqual(t.shape, (1, 24, 5))

    def test_31_root_serves_html(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("PROJECT 51: SMART ENERGY FORECASTING & PEAK SHAVING", res.text)

if __name__ == "__main__":
    unittest.main()
