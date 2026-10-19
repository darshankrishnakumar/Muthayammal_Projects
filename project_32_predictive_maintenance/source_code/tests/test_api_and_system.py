"""
Automated QA Verification Suite for Project 32
Predictive Maintenance of Industrial Machines Using Multivariate Sensor Data and Deep Learning
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
    get_connection, get_machines, get_history, get_stats,
    get_audit_logs, get_work_orders, log_audit, DB_PATH
)
from pdm_engine import pdm_engine, MachineHealthClassifierNet, RULRegressorNet

class TestProject32PredictiveMaintenanceSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_01_health_status(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "running")
        self.assertEqual(data["port"], 5032)
        self.assertEqual(data["monitored_assets"], 5)
        self.assertIn("PyTorch", data["model"])
        self.assertIn("WAL", data["storage"])

    def test_02_pytorch_models_loaded(self):
        self.assertIsNotNone(pdm_engine.classifier)
        self.assertIsNotNone(pdm_engine.regressor)
        self.assertIsNotNone(pdm_engine.scalers)
        cls_weights = os.path.join(BACKEND_DIR, "pdm_classifier_weights.pt")
        reg_weights = os.path.join(BACKEND_DIR, "pdm_rul_weights.pt")
        self.assertTrue(os.path.isfile(cls_weights))
        self.assertTrue(os.path.isfile(reg_weights))
        self.assertGreater(os.path.getsize(cls_weights), 10000)
        self.assertGreater(os.path.getsize(reg_weights), 10000)

    def test_03_sqlite_wal_mode(self):
        conn = get_connection()
        mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        conn.close()
        self.assertEqual(mode.lower(), "wal")

    def test_04_machines_seed_count(self):
        machines = get_machines()
        self.assertEqual(len(machines), 5)
        names = {m["name"] for m in machines}
        self.assertIn("Screw Compressor A-101", names)
        self.assertIn("Centrifugal Pump B-204", names)
        self.assertIn("Induction Motor C-302", names)
        self.assertIn("Gas Turbine Generator D-401", names)
        self.assertIn("Conveyor Drive Unit E-505", names)

    def test_05_machines_endpoint(self):
        res = self.client.get("/api/machines")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(len(data), 5)
        for m in data:
            self.assertIn("nominal_rpm", m)
            self.assertIn("nominal_temp", m)
            self.assertIn("nominal_vib", m)
            self.assertIn("criticality", m)

    def test_06_machine_types(self):
        machines = get_machines()
        types = {m["name"]: m["type"] for m in machines}
        self.assertEqual(types["Screw Compressor A-101"], "Rotary Screw Compressor")
        self.assertEqual(types["Gas Turbine Generator D-401"], "Co-Gen Gas Turbine")

    def test_07_normal_baseline_scenario(self):
        res = self.client.post("/api/analyze", json={
            "machine": "Screw Compressor A-101",
            "scenario": "normal"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["fault_mode"], "Normal Baseline")
        self.assertGreaterEqual(data["health_score"], 85.0)
        self.assertEqual(data["urgency"], "NONE")
        self.assertGreaterEqual(data["rul_hours"], 1500.0)

    def test_08_fault_scenario(self):
        res = self.client.post("/api/analyze", json={
            "machine": "Gas Turbine Generator D-401",
            "scenario": "fault"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertNotEqual(data["fault_mode"], "Normal Baseline")
        self.assertLessEqual(data["health_score"], 65.0)
        self.assertIn(data["urgency"], ["URGENT", "IMMEDIATE", "SCHEDULED"])

    def test_09_flat_features_inference(self):
        res = self.client.post("/api/analyze", json={
            "machine": "Centrifugal Pump B-204",
            "temperature_c": 72.0,
            "vibration_mm_s": 2.8,
            "pressure_bar": 12.0
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("health_score", data)
        self.assertIn("fault_mode", data)
        self.assertIn("rul_hours", data)

    def test_10_pressure_psi_conversion(self):
        res = self.client.post("/api/analyze", json={
            "machine": "Screw Compressor A-101",
            "temperature_c": 75.0,
            "vibration_mms": 1.2,
            "pressure_psi": 120.0
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("telemetry", data)
        # 120 psi is ~8.27 bar
        self.assertAlmostEqual(data["telemetry"]["pressure_bar"], 8.27, places=1)

    def test_11_health_score_range(self):
        for _ in range(10):
            res = pdm_engine.analyze("Induction Motor C-302", {
                "temperature_c": float(np.random.uniform(50, 110)),
                "vibration_mm_s": float(np.random.uniform(0.4, 4.5))
            }, persist=False)
            self.assertGreaterEqual(res["health_score"], 0.0)
            self.assertLessEqual(res["health_score"], 100.0)

    def test_12_rul_hours_positive(self):
        for _ in range(10):
            res = pdm_engine.analyze("Conveyor Drive Unit E-505", {
                "temperature_c": float(np.random.uniform(40, 95)),
                "vibration_mm_s": float(np.random.uniform(1.0, 5.0))
            }, persist=False)
            self.assertGreaterEqual(res["rul_hours"], 24.0)

    def test_13_fft_harmonics_output(self):
        res = pdm_engine.analyze("Screw Compressor A-101", persist=False)
        self.assertIn("fft_harmonics", res)
        self.assertEqual(len(res["fft_harmonics"]), 8)

    def test_14_history_endpoint(self):
        res = self.client.get("/api/history?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        first = data[0]
        self.assertIn("machine", first)
        self.assertIn("health_score", first)
        self.assertIn("fault_mode", first)
        self.assertIn("telemetry", first)

    def test_15_stats_endpoint(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_inspections", data)
        self.assertIn("critical_urgencies", data)
        self.assertIn("avg_fleet_health_score", data)
        self.assertIn("connected_assets", data)

    def test_16_database_tables_exist(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        expected = {'machines', 'sensor_telemetry', 'diagnostic_inspections', 'maintenance_work_orders', 'audit_log'}
        for t in expected:
            self.assertIn(t, tables)

    def test_17_audit_logging(self):
        initial_logs = get_audit_logs(limit=10)
        log_audit("TEST_VERIFICATION", "Testing PDM automated verification log", "INFO")
        updated_logs = get_audit_logs(limit=10)
        self.assertGreaterEqual(len(updated_logs), len(initial_logs))
        self.assertEqual(updated_logs[0]["event_type"], "TEST_VERIFICATION")

    def test_18_work_order_dispatch(self):
        payload = {
            "machine": "Gas Turbine Generator D-401",
            "fault_mode": "Outer Race Bearing Spall",
            "urgency": "IMMEDIATE",
            "work_order_code": "WO-TEST-2026-999",
            "technician": "Vibration Specialist Elena Rostova",
            "action_taken": "Scheduled emergency shaft decoupling & bearing replacement",
            "status": "DISPATCHED"
        }
        res = self.client.post("/api/work-order", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("work_order_id", data)

    def test_19_work_orders_get_endpoint(self):
        res = self.client.get("/api/work-orders")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_20_model_metadata_endpoint(self):
        res = self.client.get("/api/model/info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("models", data)
        self.assertIn("dataset_samples", data)

    def test_21_bearing_spall_vibration_sensitivity(self):
        res_norm = pdm_engine.analyze("Centrifugal Pump B-204", {
            "temperature_c": 64.0,
            "vibration_mm_s": 0.8
        }, persist=False)
        res_spall = pdm_engine.analyze("Centrifugal Pump B-204", {
            "temperature_c": 82.0,
            "vibration_mm_s": 4.2
        }, persist=False)
        self.assertGreater(res_norm["health_score"], res_spall["health_score"])

    def test_22_stator_overheating_thermal_sensitivity(self):
        res_hot = pdm_engine.analyze("Induction Motor C-302", {
            "temperature_c": 115.0,
            "vibration_mm_s": 1.4
        }, persist=False)
        self.assertLess(res_hot["health_score"], 70.0)

    def test_23_index_page_served(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Predictive Maintenance", html)

    def test_24_static_file_not_found(self):
        res = self.client.get("/nonexistent_pdm_resource.js")
        self.assertEqual(res.status_code, 404)

    def test_25_dataset_csv_and_json_exist(self):
        csv_file = os.path.join(DATA_DIR, "industrial_pdm_telemetry.csv")
        json_file = os.path.join(DATA_DIR, "industrial_pdm_telemetry.json")
        self.assertTrue(os.path.isfile(csv_file))
        self.assertTrue(os.path.isfile(json_file))
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = sum(1 for _ in f)
        self.assertGreaterEqual(lines, 5500)

    def test_26_dataset_features_complete(self):
        csv_file = os.path.join(DATA_DIR, "industrial_pdm_telemetry.csv")
        with open(csv_file, 'r', encoding='utf-8') as f:
            header = f.readline().strip().split(',')
        required = ["temperature_c", "vibration_mm_s", "pressure_bar", "rpm", "oil_viscosity_cst", "acoustic_emission_db"]
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
            cls_out = pdm_engine.classifier(sample_tensor)
            reg_out = pdm_engine.regressor(sample_tensor)
        self.assertEqual(cls_out.shape, (1, 6))
        self.assertEqual(reg_out.shape, (1, 2))
        self.assertFalse(torch.isnan(cls_out).any())
        self.assertFalse(torch.isnan(reg_out).any())

if __name__ == "__main__":
    unittest.main()
