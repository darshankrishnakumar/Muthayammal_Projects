import unittest
import os
import sys
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "source_code", "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import app
from database import get_db_connection
from aviation_engine import engine, COMPONENTS_REGISTRY

class TestAviationRULSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_01_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("port"), 5033)
        self.assertIn("service", data)
        self.assertIn("monitored_components", data)

    def test_02_components_list(self):
        res = self.client.get("/api/components")
        self.assertEqual(res.status_code, 200)
        comps = res.get_json()
        self.assertGreaterEqual(len(comps), 5)
        ids = [c["component_id"] for c in comps]
        self.assertIn("COMP-TURB-01", ids)
        self.assertIn("COMP-HPC-02", ids)
        self.assertIn("COMP-BRG-03", ids)
        self.assertIn("COMP-FMU-04", ids)
        self.assertIn("COMP-LPT-05", ids)

    def test_03_stats_endpoint(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_assessments", data)
        self.assertIn("avg_fleet_health_score", data)
        self.assertIn("grounded_critical", data)
        self.assertEqual(data.get("faa_compliance_rate"), "100%")

    def test_04_history_endpoint(self):
        res = self.client.get("/api/history?limit=10")
        self.assertEqual(res.status_code, 200)
        history = res.get_json()
        self.assertIsInstance(history, list)
        if len(history) > 0:
            self.assertIn("airworthiness_status", history[0])
            self.assertIn("health_score", history[0])

    def test_05_predict_hpt_blades(self):
        res = self.client.post("/api/predict", json={"component_id": "COMP-TURB-01", "cycles": 2000})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["component_id"], "COMP-TURB-01")
        self.assertIn("airworthiness_status", data)
        self.assertGreater(data["health_score"], 0)
        self.assertGreater(data["rul_cycles"], 0)

    def test_06_predict_hpc_rotor(self):
        res = self.client.post("/api/predict", json={"component_id": "COMP-HPC-02", "cycles": 1500})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["component_id"], "COMP-HPC-02")
        self.assertEqual(data["engine_model"], "GE90-115B")

    def test_07_predict_bearing(self):
        res = self.client.post("/api/predict", json={"component_id": "COMP-BRG-03", "cycles": 5200})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["component_id"], "COMP-BRG-03")
        self.assertIn("GROUNDED", data["airworthiness_status"])

    def test_08_predict_fmu(self):
        res = self.client.post("/api/predict", json={"component_id": "COMP-FMU-04", "cycles": 2500})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["component_id"], "COMP-FMU-04")
        self.assertIn("AIRWORTHY", data["airworthiness_status"])

    def test_09_predict_lpt_stator(self):
        res = self.client.post("/api/predict", json={"component_id": "COMP-LPT-05", "cycles": 5000})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["component_id"], "COMP-LPT-05")
        self.assertIn("MAINTENANCE DUE SOON", data["airworthiness_status"])

    def test_10_predict_via_operating_hours(self):
        res = self.client.post("/api/predict", json={"component_id": "COMP-TURB-01", "operating_hours": 8400})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["flight_cycles_completed"], 3000)
        self.assertIn("airworthiness_status", data)

    def test_11_predict_worn_scenario(self):
        res = self.client.post("/api/predict", json={"component": "High-Pressure Turbine (HPT) Blades", "scenario": "worn"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertLess(data["health_score"], 45.0)

    def test_12_predict_fresh_scenario(self):
        res = self.client.post("/api/predict", json={"component": "High-Pressure Turbine (HPT) Blades", "scenario": "fresh"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreater(data["health_score"], 70.0)

    def test_13_degradation_curve_format(self):
        res = self.client.post("/api/predict", json={"component_id": "COMP-HPC-02", "cycles": 3000})
        data = res.get_json()
        curve = data.get("degradation_curve", [])
        self.assertEqual(len(curve), 11)
        self.assertTrue(curve[0] >= curve[-1])

    def test_14_cmapss_sensor_telemetry(self):
        res = self.client.post("/api/predict", json={"component_id": "COMP-TURB-01", "cycles": 2500})
        sensors = res.get_json().get("cmapss_sensors", {})
        self.assertIn("t50_lpt_outlet_temp_r", sensors)
        self.assertIn("p30_hpc_pressure_psia", sensors)
        self.assertIn("nc_core_speed_rpm", sensors)
        self.assertIn("nf_fan_speed_rpm", sensors)
        self.assertIn("fuel_flow_ratio_pps_psi", sensors)
        self.assertIn("egt_margin_deg_c", sensors)
        self.assertIn("vibration_broadband_g", sensors)

    def test_15_model_info_endpoint(self):
        res = self.client.get("/api/model/info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("framework", data)
        self.assertIn("airworthiness_classifier", data["models"])
        self.assertIn("rul_regressor", data["models"])
        self.assertEqual(data["dataset_sample_size"], 6000)

    def test_16_shop_orders_get(self):
        res = self.client.get("/api/shop-orders")
        self.assertEqual(res.status_code, 200)
        orders = res.get_json()
        self.assertIsInstance(orders, list)
        self.assertGreaterEqual(len(orders), 1)

    def test_17_shop_orders_post(self):
        payload = {
            "component_id": "COMP-TURB-01",
            "priority": "CRITICAL",
            "defect_summary": "High cycle creep detected via automated acoustic emission inspection",
            "assigned_technician": "Dr. R. Vance",
            "estimated_downtime_hrs": 36.0
        }
        res = self.client.post("/api/shop-orders", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("MSO-2026", data.get("order_id"))

    def test_18_audit_logs_get(self):
        res = self.client.get("/api/audit-logs?limit=5")
        self.assertEqual(res.status_code, 200)
        logs = res.get_json()
        self.assertIsInstance(logs, list)
        self.assertGreaterEqual(len(logs), 1)

    def test_19_sqlite_wal_mode(self):
        conn = get_db_connection()
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        conn.close()
        self.assertEqual(journal_mode.lower(), "wal")

    def test_20_sqlite_tables_exist(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        for t in ["aircraft_components", "flight_telemetry", "rul_predictions", "maintenance_shop_orders", "audit_log"]:
            self.assertIn(t, tables)

    def test_21_engine_alias_resolution(self):
        comp1 = engine.resolve_component("hpt")
        self.assertEqual(comp1["id"], "COMP-TURB-01")
        comp2 = engine.resolve_component("compressor")
        self.assertEqual(comp2["id"], "COMP-HPC-02")
        comp3 = engine.resolve_component("bearing")
        self.assertEqual(comp3["id"], "COMP-BRG-03")
        comp4 = engine.resolve_component("fmu")
        self.assertEqual(comp4["id"], "COMP-FMU-04")
        comp5 = engine.resolve_component("lpt")
        self.assertEqual(comp5["id"], "COMP-LPT-05")

    def test_22_index_serving(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Aircraft Turbofan Remaining Useful Life", res.data)

    def test_23_not_found_handling(self):
        res = self.client.get("/non_existent_page_xyz")
        self.assertEqual(res.status_code, 404)

    def test_24_rul_flight_hours_ratio(self):
        res = self.client.post("/api/predict", json={"component_id": "COMP-HPC-02", "cycles": 1000})
        data = res.get_json()
        ratio = data["rul_flight_hours"] / max(1, data["rul_cycles"])
        self.assertAlmostEqual(ratio, 2.8, delta=0.05)

    def test_25_probabilities_sum(self):
        res = self.client.post("/api/predict", json={"component_id": "COMP-FMU-04", "cycles": 3000})
        probs = res.get_json().get("status_probabilities", {})
        total_p = sum(probs.values())
        self.assertAlmostEqual(total_p, 1.0, places=2)

    def test_26_dataset_file_integrity(self):
        csv_path = os.path.join(BASE_DIR, "source_code", "data", "nasa_cmapss_turbofan_6000.csv")
        self.assertTrue(os.path.exists(csv_path))
        with open(csv_path, "r") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 6001)  # header + 6000 rows

    def test_27_model_weights_integrity(self):
        cls_weights = os.path.join(BASE_DIR, "source_code", "backend", "models", "aviation_classifier_weights.pt")
        reg_weights = os.path.join(BASE_DIR, "source_code", "backend", "models", "turbofan_rul_weights.pt")
        self.assertTrue(os.path.exists(cls_weights))
        self.assertTrue(os.path.exists(reg_weights))
        self.assertGreater(os.path.getsize(cls_weights), 10000)
        self.assertGreater(os.path.getsize(reg_weights), 10000)

    def test_28_database_persistence_cycle(self):
        conn = get_db_connection()
        count_before = conn.execute("SELECT COUNT(*) FROM rul_predictions;").fetchone()[0]
        conn.close()

        res = self.client.post("/api/predict", json={"component_id": "COMP-TURB-01", "cycles": 1800})
        self.assertEqual(res.status_code, 200)

        conn = get_db_connection()
        count_after = conn.execute("SELECT COUNT(*) FROM rul_predictions;").fetchone()[0]
        conn.close()
        self.assertEqual(count_after, count_before + 1)

if __name__ == "__main__":
    unittest.main()
