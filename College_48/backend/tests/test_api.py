import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestFreshnessAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_batches(self):
        res = self.client.get("/api/freshness/batches")
        self.assertEqual(res.status_code, 200)
        self.assertIn("batches", res.json())

    def test_evaluate(self):
        res = self.client.post("/api/freshness/evaluate", json={
            "product_name": "Test Item",
            "food_category": "MEAT_POULTRY",
            "simulate_spoilage": False
        })
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.json()["metrics"]["freshness_score"], 80.0)

if __name__ == "__main__":
    unittest.main()
