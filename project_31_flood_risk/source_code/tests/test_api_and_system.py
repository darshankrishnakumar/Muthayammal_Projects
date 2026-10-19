"""
Automated QA Verification Suite for Project 31
Urban Flood Risk Prediction & Early Warning System
28 Comprehensive Unit & Integration Tests (100% Pass Rate Target)
"""

import os
import sys
import json
import unittest
import numpy as np
import torch
import sqlite3

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", "backend"))
DATA_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", "data"))
ROOT_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app
from database import (
    get_connection, get_zones, get_history, get_stats,
    get_audit_logs, get_dispatches, log_audit, DB_PATH
)
from flood_engine import flood_engine, FloodRiskClassifierNet, InundationDepthRegressorNet

class TestProject31FloodRiskSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_01_health_status(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "running")
        self.assertEqual(data["port"], 5031)
        self.assertEqual(data["monitored_basins"], 5)
        self.assertIn("PyTorch", data["model"])
        self.assertIn("WAL", data["storage"])

    def test_02_pytorch_models_loaded(self):
        self.assertIsNotNone(flood_engine.classifier)
        self.assertIsNotNone(flood_engine.regressor)
        self.assertIsNotNone(flood_engine.scalers)
        cls_weights = os.path.join(BACKEND_DIR, "flood_risk_classifier_weights.pt")
        reg_weights = os.path.join(BACKEND_DIR, "inundation_regressor_weights.pt")
        self.assertTrue(os.path.isfile(cls_weights))
        self.assertTrue(os.path.isfile(reg_weights))
        self.assertGreater(os.path.getsize(cls_weights), 10000)
        self.assertGreater(os.path.getsize(reg_weights), 10000)

    def test_03_sqlite_wal_mode(self):
        conn = get_connection()
        mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal")

    def test_04_basins_seed_count(self):
        zones = get_zones()
        self.assertEqual(len(zones), 5)
        names = {z["name"] for z in zones}
        self.assertIn("Riverside Embankment District", names)
        self.assertIn("Bay Coastal Lowlands", names)
        self.assertIn("Downtown Metropolitan Core", names)
        self.assertIn("Industrial Valley Sector", names)
        self.assertIn("Upland Ridge Buffer", names)

    def test_05_basins_endpoint(self):
        res = self.client.get("/api/zones")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 5)
        for b in data:
            self.assertIn("dem_elevation_m", b)
            self.assertIn("river_threshold_m", b)
            self.assertIn("type", b)
            self.assertIn("population_density", b)

    def test_06_basin_elevation_hierarchy(self):
        zones = get_zones()
        zone_dict = {z["name"]: z for z in zones}
        self.assertLess(zone_dict["Bay Coastal Lowlands"]["dem_elevation_m"], zone_dict["Downtown Metropolitan Core"]["dem_elevation_m"])
        self.assertGreater(zone_dict["Upland Ridge Buffer"]["dem_elevation_m"], 80.0)

    def test_07_benign_weather_prediction(self):
        payload = {
            "zone": "Riverside Embankment District",
            "features": {
                "rainfall_mm": 10.0,
                "river_level_m": 2.5,
                "soil_moisture": 0.30,
                "storm_surge_m": 0.1
            }
        }
        res = self.client.post("/api/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["alert_level"], "NORMAL")
        self.assertEqual(data["inundation_depth_m"], 0.0)
        self.assertGreaterEqual(data["lead_time_hours"], 12.0)

    def test_08_critical_deluge_prediction(self):
        payload = {
            "zone": "Bay Coastal Lowlands",
            "features": {
                "rainfall_mm": 250.0,
                "river_level_m": 7.5,
                "soil_moisture": 0.95,
                "storm_surge_m": 2.5
            }
        }
        res = self.client.post("/api/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["alert_level"], "CRITICAL")
        self.assertGreater(data["inundation_depth_m"], 0.8)
        self.assertLessEqual(data["lead_time_hours"], 5.0)

    def test_09_warning_flash_flood_prediction(self):
        payload = {
            "zone": "Riverside Embankment District",
            "features": {
                "rainfall_mm": 130.0,
                "river_level_m": 6.8,
                "soil_moisture": 0.85,
                "storm_surge_m": 0.8
            }
        }
        res = self.client.post("/api/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn(data["alert_level"], ["WARNING", "CRITICAL"])
        self.assertGreater(data["inundation_depth_m"], 0.0)

    def test_10_inundation_depth_non_negative(self):
        for _ in range(10):
            res = flood_engine.predict("Industrial Valley Sector", {
                "rainfall_mm": float(np.random.uniform(5, 200)),
                "river_level_m": float(np.random.uniform(2, 9)),
                "soil_moisture": float(np.random.uniform(0.2, 0.9))
            }, persist=False)
            self.assertGreaterEqual(res["inundation_depth_m"], 0.0)

    def test_11_lead_time_positive(self):
        for _ in range(10):
            res = flood_engine.predict("Downtown Metropolitan Core", {
                "rainfall_mm": float(np.random.uniform(5, 250)),
                "river_level_m": float(np.random.uniform(2, 10)),
                "soil_moisture": float(np.random.uniform(0.2, 0.95))
            }, persist=False)
            self.assertGreaterEqual(res["lead_time_hours"], 1.0)

    def test_12_history_endpoint(self):
        res = self.client.get("/api/history?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        first = data[0]
        self.assertIn("zone", first)
        self.assertIn("alert_level", first)
        self.assertIn("inundation_depth_m", first)
        self.assertIn("telemetry", first)

    def test_13_stats_endpoint(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_assessments", data)
        self.assertIn("critical_zones", data)
        self.assertIn("warning_zones", data)
        self.assertIn("system_readiness_pct", data)

    def test_14_database_tables_exist(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        expected = {'river_basins', 'hydrological_readings', 'flood_predictions', 'emergency_dispatches', 'audit_log'}
        for t in expected:
            self.assertIn(t, tables)

    def test_15_audit_logging(self):
        initial_logs = get_audit_logs(limit=10)
        log_audit("TEST_EVENT", "Automated QA verification test event", "INFO")
        updated_logs = get_audit_logs(limit=10)
        self.assertGreaterEqual(len(updated_logs), len(initial_logs))
        self.assertEqual(updated_logs[0]["event_type"], "TEST_EVENT")

    def test_16_emergency_dispatch_endpoint(self):
        payload = {
            "zone": "Riverside Embankment District",
            "alert_level": "WARNING",
            "dispatch_team": "Mobile Levee Reinforcement Unit 3",
            "action_taken": "Reinforced barrier bags along south river bank",
            "status": "EN_ROUTE",
            "protocol": "Sector 3 secondary barrier reinforcement"
        }
        res = self.client.post("/api/dispatch", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("dispatch_id", data)

    def test_17_dispatches_get_endpoint(self):
        res = self.client.get("/api/dispatches")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_18_model_metadata_endpoint(self):
        res = self.client.get("/api/model/info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("models", data)
        self.assertIn("dataset_samples", data)

    def test_19_flat_parameter_input(self):
        payload = {
            "zone": "Downtown Metropolitan Core",
            "rainfall_mm": 115.0,
            "river_level_m": 6.8,
            "soil_moisture": 78.0
        }
        res = self.client.post("/api/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("alert_level", data)
        self.assertIn("inundation_depth_m", data)

    def test_20_nested_features_input(self):
        payload = {
            "zone": "Industrial Valley Sector",
            "features": {
                "rainfall_mm": 50.0,
                "river_level_m": 4.0,
                "soil_moisture": 0.50
            }
        }
        res = self.client.post("/api/predict", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["zone"], "Industrial Valley Sector")

    def test_21_estuary_storm_surge_sensitivity(self):
        res_calm = flood_engine.predict("Bay Coastal Lowlands", {
            "rainfall_mm": 80.0,
            "river_level_m": 3.5,
            "soil_moisture": 0.60,
            "storm_surge_m": 0.1
        }, persist=False)
        res_surge = flood_engine.predict("Bay Coastal Lowlands", {
            "rainfall_mm": 80.0,
            "river_level_m": 3.5,
            "soil_moisture": 0.60,
            "storm_surge_m": 2.8
        }, persist=False)
        self.assertGreaterEqual(res_surge["risk_pct"], res_calm["risk_pct"])

    def test_22_upland_plateau_resilience(self):
        res_upland = flood_engine.predict("Upland Ridge Buffer", {
            "rainfall_mm": 120.0,
            "river_level_m": 6.0,
            "soil_moisture": 0.70
        }, persist=False)
        res_coastal = flood_engine.predict("Bay Coastal Lowlands", {
            "rainfall_mm": 120.0,
            "river_level_m": 6.0,
            "soil_moisture": 0.70
        }, persist=False)
        self.assertLess(res_upland["risk_pct"], res_coastal["risk_pct"])

    def test_23_index_page_served(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Urban Flood Risk", html)

    def test_24_static_file_not_found(self):
        res = self.client.get("/nonexistent_asset_404.html")
        self.assertEqual(res.status_code, 404)

    def test_25_dataset_csv_and_json_exist(self):
        csv_file = os.path.join(DATA_DIR, "flood_hydrological_telemetry.csv")
        json_file = os.path.join(DATA_DIR, "flood_hydrological_telemetry.json")
        self.assertTrue(os.path.isfile(csv_file))
        self.assertTrue(os.path.isfile(json_file))
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = sum(1 for _ in f)
        self.assertGreaterEqual(lines, 5500)

    def test_26_dataset_features_complete(self):
        csv_file = os.path.join(DATA_DIR, "flood_hydrological_telemetry.csv")
        with open(csv_file, 'r', encoding='utf-8') as f:
            header = f.readline().strip().split(',')
        required = ["rainfall_mm", "river_stage_m", "river_threshold_m", "soil_moisture", "storm_surge_m", "dem_elevation_m"]
        for col in required:
            self.assertIn(col, header)

    def test_27_deliverables_structure(self):
        self.assertTrue(os.path.isdir(os.path.join(ROOT_DIR, "docs")))
        self.assertTrue(os.path.isdir(os.path.join(ROOT_DIR, "presentations")))
        self.assertTrue(os.path.isfile(os.path.join(ROOT_DIR, "requirements.txt")))
        self.assertTrue(os.path.isfile(os.path.join(ROOT_DIR, ".env.example")))

    def test_28_model_tensor_eval_modes(self):
        sample_tensor = torch.zeros((1, 8), dtype=torch.float32)
        with torch.no_grad():
            cls_out = flood_engine.classifier(sample_tensor)
            reg_out = flood_engine.regressor(sample_tensor)
        self.assertEqual(cls_out.shape, (1, 4))
        self.assertEqual(reg_out.shape, (1, 2))
        self.assertFalse(torch.isnan(cls_out).any())
        self.assertFalse(torch.isnan(reg_out).any())

if __name__ == "__main__":
    unittest.main()
