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
from damage_engine import engine, DEFECT_CLASSES, SECTORS_REGISTRY

class TestRoadDamageSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_01_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("port"), 5034)
        self.assertEqual(data.get("classes_supported"), 5)

    def test_02_sectors_list(self):
        res = self.client.get("/api/sectors")
        self.assertEqual(res.status_code, 200)
        sectors = res.get_json()
        self.assertGreaterEqual(len(sectors), 5)
        ids = [s["sector_id"] for s in sectors]
        self.assertIn("SEC-NORTH-01", ids)
        self.assertIn("SEC-URBAN-02", ids)
        self.assertIn("SEC-IND-03", ids)
        self.assertIn("SEC-RES-04", ids)
        self.assertIn("SEC-MTN-05", ids)

    def test_03_defects_catalog(self):
        res = self.client.get("/api/defects/catalog")
        self.assertEqual(res.status_code, 200)
        catalog = res.get_json()
        self.assertEqual(len(catalog), 5)
        codes = [d["code"] for d in catalog]
        self.assertIn("D40", codes)
        self.assertIn("D20", codes)
        self.assertIn("D00", codes)
        self.assertIn("D10", codes)
        self.assertIn("D43", codes)

    def test_04_stats_endpoint(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("total_surveys", data)
        self.assertIn("total_defects_catalogued", data)
        self.assertIn("mean_pavement_condition_index", data)
        self.assertEqual(data.get("yolo_map50"), "86.4%")

    def test_05_history_endpoint(self):
        res = self.client.get("/api/history?limit=10")
        self.assertEqual(res.status_code, 200)
        history = res.get_json()
        self.assertIsInstance(history, list)
        if len(history) > 0:
            self.assertIn("pci_score", history[0])
            self.assertIn("pci_rating", history[0])

    def test_06_detect_highway_sector(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-NORTH-01"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["sector_id"], "SEC-NORTH-01")
        self.assertIn("pci_rating", data)
        self.assertGreater(data["pci_score"], 0)

    def test_07_detect_urban_arterial(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-URBAN-02"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["sector_id"], "SEC-URBAN-02")
        self.assertEqual(data["speed_limit_kmh"], 60)

    def test_08_detect_industrial_ring(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-IND-03"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["sector_id"], "SEC-IND-03")

    def test_09_detect_residential_boulevard(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-RES-04"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["sector_id"], "SEC-RES-04")

    def test_10_detect_mountain_pass(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-MTN-05"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["sector_id"], "SEC-MTN-05")

    def test_11_detect_pothole_explicit(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-NORTH-01", "damage_type": "POTHOLE"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("pci_rating", data)
        self.assertGreater(len(data["defects"]), 0)
        self.assertEqual(data["defects"][0]["code"], "D40")

    def test_12_detect_alligator_explicit(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-URBAN-02", "damage_type": "ALLIGATOR"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["defects"][0]["code"], "D20")

    def test_13_detect_crack_explicit(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-RES-04", "damage_type": "D00"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["defects"][0]["code"], "D00")

    def test_14_detect_rutting_explicit(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-IND-03", "damage_type": "RUTTING"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["defects"][0]["code"], "D43")

    def test_15_detect_severe_scenario(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-NORTH-01", "scenario": "severe"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertLess(data["pci_score"], 45.0)
        self.assertEqual(data["pci_rating"], "POOR (CRITICAL RESURFACING)")

    def test_16_detect_clean_scenario(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-NORTH-01", "scenario": "clean"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(data["pci_score"], 70.0)
        self.assertEqual(data["pci_rating"], "GOOD (STRUCTURALLY SOUND)")
        self.assertEqual(len(data["defects"]), 0)

    def test_17_bounding_box_coordinates(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-URBAN-02", "damage_type": "D40"})
        data = res.get_json()
        for d in data.get("defects", []):
            bbox = d.get("bbox", {})
            self.assertTrue(0.0 <= bbox["x"] <= 1.0)
            self.assertTrue(0.0 <= bbox["y"] <= 1.0)
            self.assertTrue(0.0 <= bbox["w"] <= 1.0)
            self.assertTrue(0.0 <= bbox["h"] <= 1.0)

    def test_18_physical_telemetry_payload(self):
        res = self.client.post("/api/detect", json={"sector_id": "SEC-NORTH-01"})
        telem = res.get_json().get("physical_telemetry", {})
        self.assertIn("damaged_area_sqm", telem)
        self.assertIn("pothole_depth_cm", telem)
        self.assertIn("crack_width_mm", telem)
        self.assertIn("traffic_volume_vpd", telem)
        self.assertIn("heavy_axle_pct", telem)
        self.assertIn("pavement_age_years", telem)
        self.assertIn("drainage_quality_idx", telem)
        self.assertIn("freeze_thaw_cycles", telem)

    def test_19_work_orders_get(self):
        res = self.client.get("/api/work-orders")
        self.assertEqual(res.status_code, 200)
        orders = res.get_json()
        self.assertIsInstance(orders, list)
        self.assertGreaterEqual(len(orders), 1)

    def test_20_work_orders_post(self):
        payload = {
            "sector_id": "SEC-NORTH-01",
            "priority": "CRITICAL",
            "remediation_scope": "Full depth milling and asphalt overlay on deep rutting sections",
            "assigned_contractor": "Apex Highway Maintenance Corp",
            "budget_allocated_usd": 15000
        }
        res = self.client.post("/api/work-orders", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("MWO-2026", data.get("order_id"))

    def test_21_audit_logs_get(self):
        res = self.client.get("/api/audit-logs?limit=5")
        self.assertEqual(res.status_code, 200)
        logs = res.get_json()
        self.assertIsInstance(logs, list)
        self.assertGreaterEqual(len(logs), 1)

    def test_22_model_info_endpoint(self):
        res = self.client.get("/api/model/info")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("framework", data)
        self.assertIn("yolo_damage_classifier", data["models"])
        self.assertIn("pavement_condition_regressor", data["models"])
        self.assertEqual(data["dataset_sample_size"], 6000)

    def test_23_sqlite_wal_mode(self):
        conn = get_db_connection()
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        conn.close()
        self.assertEqual(journal_mode.lower(), "wal")

    def test_24_sqlite_tables_exist(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        for t in ["road_sectors", "damage_inspections", "pavement_defects", "municipal_work_orders", "audit_log"]:
            self.assertIn(t, tables)

    def test_25_sector_alias_resolution(self):
        sec1 = engine.resolve_sector("highway")
        self.assertEqual(sec1["id"], "SEC-NORTH-01")
        sec2 = engine.resolve_sector("downtown")
        self.assertEqual(sec2["id"], "SEC-URBAN-02")
        sec3 = engine.resolve_sector("cargo")
        self.assertEqual(sec3["id"], "SEC-IND-03")
        sec4 = engine.resolve_sector("suburban")
        self.assertEqual(sec4["id"], "SEC-RES-04")
        sec5 = engine.resolve_sector("mountain")
        self.assertEqual(sec5["id"], "SEC-MTN-05")

    def test_26_damage_class_alias_resolution(self):
        idx1, d1 = engine.resolve_damage_class("pothole")
        self.assertEqual(d1["code"], "D40")
        idx2, d2 = engine.resolve_damage_class("alligator")
        self.assertEqual(d2["code"], "D20")
        idx3, d3 = engine.resolve_damage_class("longitudinal")
        self.assertEqual(d3["code"], "D00")
        idx4, d4 = engine.resolve_damage_class("transverse")
        self.assertEqual(d4["code"], "D10")
        idx5, d5 = engine.resolve_damage_class("rutting")
        self.assertEqual(d5["code"], "D43")

    def test_27_index_serving(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"AI Road Damage Detection", res.data)

    def test_28_not_found_handling(self):
        res = self.client.get("/non_existent_page_xyz")
        self.assertEqual(res.status_code, 404)

    def test_29_dataset_file_integrity(self):
        csv_path = os.path.join(BASE_DIR, "source_code", "data", "rdd2022_pavement_surveys_6000.csv")
        self.assertTrue(os.path.exists(csv_path))
        with open(csv_path, "r") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 6001)

    def test_30_model_weights_integrity(self):
        cls_weights = os.path.join(BASE_DIR, "source_code", "backend", "models", "road_damage_classifier_weights.pt")
        reg_weights = os.path.join(BASE_DIR, "source_code", "backend", "models", "pavement_condition_weights.pt")
        self.assertTrue(os.path.exists(cls_weights))
        self.assertTrue(os.path.exists(reg_weights))
        self.assertGreater(os.path.getsize(cls_weights), 10000)
        self.assertGreater(os.path.getsize(reg_weights), 10000)

if __name__ == "__main__":
    unittest.main()
