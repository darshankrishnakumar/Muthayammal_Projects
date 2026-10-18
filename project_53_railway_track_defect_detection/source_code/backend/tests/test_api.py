import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestRailAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_defects(self):
        res = self.client.get("/api/rail/defects")
        self.assertEqual(res.status_code, 200)
        self.assertIn("records", res.json())

    def test_inspect(self):
        res = self.client.post("/api/rail/inspect", json={
            "chainage_km": "KM 148.500",
            "track_segment": "Line 2 Spur",
            "simulated_condition": "crack"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("defect_type", res.json()["metrics"])

if __name__ == "__main__":
    unittest.main()
