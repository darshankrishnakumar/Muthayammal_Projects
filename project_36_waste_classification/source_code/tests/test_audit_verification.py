import unittest
import os
import sys
import importlib.util

class TestPROJECT036(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        num = 36
        if num in [36, 37]:
            app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app.py"))
            spec = importlib.util.spec_from_file_location("app_mod_36", app_path)
            cls.app_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.app_mod)
            cls.client = cls.app_mod.app.test_client()
        else:
            from fastapi.testclient import TestClient
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
            if num == 38:
                from backend.app.main import app
                from backend.app.db.session import init_db
                init_db()
                cls.client = TestClient(app)
            elif num == 39:
                from backend.app.main import app
                from backend.app.db.session import init_db
                init_db()
                cls.client = TestClient(app)
            elif num == 40:
                from backend.app.main import app
                from backend.app.db.session import init_db
                init_db()
                cls.client = TestClient(app)

    def test_deliverables_exist(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "requirements.txt")), "requirements.txt must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "docs", "technical_documentation.docx")), "technical_documentation.docx must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "presentations", "project_presentation.pptx")), "project_presentation.pptx must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, ".env.example")), ".env.example must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "walkthrough", "walkthrough_script.md")), "walkthrough_script.md must exist")

    def test_health_endpoint(self):
        num = 36
        if num in [36, 37]:
            res = self.client.get("/api/health")
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertIsNotNone(data)
            self.assertTrue("status" in data or "service" in data)
        else:
            res = self.client.get("/api/health/")
            self.assertEqual(res.status_code, 200)

    def test_functional_inference(self):
        num = 36
        if num == 36:
            res = self.client.post("/api/classify", json={"item_type": "plastic_bottle"})
            self.assertEqual(res.status_code, 200)
            self.assertIn("category", res.get_json())
        elif num == 37:
            res = self.client.post("/api/analyze", json={"vehicle_type": "car", "speed_kmh": 95.0, "speed_limit": 60.0})
            self.assertEqual(res.status_code, 200)
            self.assertIn("violations_found", res.get_json())
        elif num == 38:
            res = self.client.post("/api/cracks/analyze", json={"road_name": "Test Highway", "chainage_km": 12.0})
            self.assertEqual(res.status_code, 200)
            self.assertIn("metrics", res.json())
        elif num == 39:
            res = self.client.post("/api/translation/predict", json={"gesture_index": 0})
            self.assertEqual(res.status_code, 200)
            self.assertIn("gloss", res.json())
        elif num == 40:
            res = self.client.post("/api/incidents/analyze", json={"zone_name": "Test Zone", "simulate_flame": True, "simulate_smoke": True})
            self.assertEqual(res.status_code, 200)
            self.assertIn("hazard_type", res.json())

if __name__ == "__main__":
    unittest.main()
