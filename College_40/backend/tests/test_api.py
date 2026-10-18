import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestFireAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_incidents(self):
        res = self.client.get("/api/incidents/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("incidents", res.json())

    def test_analyze(self):
        res = self.client.post("/api/incidents/analyze", json={"zone_name": "Test Zone", "simulate_flame": True, "simulate_smoke": True})
        self.assertEqual(res.status_code, 200)
        self.assertIn("hazard_type", res.json())

if __name__ == "__main__":
    unittest.main()
