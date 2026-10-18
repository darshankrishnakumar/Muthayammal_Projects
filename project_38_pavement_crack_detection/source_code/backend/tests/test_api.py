import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestCrackAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_cracks_list(self):
        res = self.client.get("/api/cracks/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("incidents", res.json())

    def test_analyze(self):
        res = self.client.post("/api/cracks/analyze", json={"road_name": "Test Highway", "chainage_km": 12.0})
        self.assertEqual(res.status_code, 200)
        self.assertIn("metrics", res.json())

if __name__ == "__main__":
    unittest.main()
