import unittest
import os
import sys
import importlib.util

class TestPROJECT035(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app.py"))
        spec = importlib.util.spec_from_file_location("app_mod_35", app_path)
        cls.app_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.app_mod)
        cls.client = cls.app_mod.app.test_client()

    def test_deliverables_exist(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "requirements.txt")), "requirements.txt must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "docs", "technical_documentation.docx")), "technical_documentation.docx must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "presentations", "project_presentation.pptx")), "project_presentation.pptx must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, ".env.example")), ".env.example must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "walkthrough", "walkthrough_script.md")), "walkthrough_script.md must exist")

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsNotNone(data)
        self.assertTrue("status" in data or "service" in data)

    def test_functional_inference(self):
        num = 35
        if num == 31:
            res = self.client.post("/api/predict", json={"rainfall_mm": 120.0, "river_level_m": 4.5, "soil_moisture": 85.0})
            self.assertEqual(res.status_code, 200)
            self.assertIn("alert_level", res.get_json())
        elif num == 32:
            res = self.client.post("/api/analyze", json={"temperature_c": 85.0, "vibration_mms": 6.2, "pressure_psi": 140.0})
            self.assertEqual(res.status_code, 200)
            self.assertIn("health_score", res.get_json())
        elif num == 33:
            res = self.client.post("/api/predict", json={"component_id": "COMP-TURB-01", "operating_hours": 4500})
            self.assertEqual(res.status_code, 200)
            self.assertIn("airworthiness_status", res.get_json())
        elif num == 34:
            res = self.client.post("/api/detect", json={"sector_id": "SEC-NORTH-01", "damage_type": "POTHOLE"})
            self.assertEqual(res.status_code, 200)
            self.assertIn("pci_rating", res.get_json())
        elif num == 35:
            res = self.client.post("/api/analyze", json={"ear": 0.18, "mar": 0.65})
            self.assertEqual(res.status_code, 200)
            self.assertIn("drowsiness_state", res.get_json())

if __name__ == "__main__":
    unittest.main()
