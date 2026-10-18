import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestCrowdAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_events(self):
        res = self.client.get("/api/crowd/events")
        self.assertEqual(res.status_code, 200)
        self.assertIn("events", res.json())

    def test_analyze(self):
        res = self.client.post("/api/crowd/analyze", json={
            "zone_name": "Test Terminal B",
            "simulation_level": "high"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("estimated_headcount", res.json()["metrics"])

if __name__ == "__main__":
    unittest.main()
