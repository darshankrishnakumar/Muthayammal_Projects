import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestFruitAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_items(self):
        res = self.client.get("/api/grading/items")
        self.assertEqual(res.status_code, 200)
        self.assertIn("items", res.json())

    def test_inspect(self):
        res = self.client.post("/api/grading/inspect", json={"conveyor_lane": 1, "defect_sim": "BRUISE"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("metrics", res.json())

if __name__ == "__main__":
    unittest.main()
