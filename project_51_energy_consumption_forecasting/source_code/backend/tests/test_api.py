import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.app.main import app
from backend.app.db.session import init_db

class TestEnergyAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_plans(self):
        res = self.client.get("/api/energy/plans")
        self.assertEqual(res.status_code, 200)
        self.assertIn("plans", res.json())

    def test_optimize(self):
        res = self.client.post("/api/energy/optimize", json={
            "building_facility": "Test Facility",
            "base_load_kw": 500.0
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("peak_shaving_reduction_pct", res.json()["metrics"])

if __name__ == "__main__":
    unittest.main()
