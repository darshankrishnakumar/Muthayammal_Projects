import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestMfgAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_parts(self):
        res = self.client.get("/api/inspection/parts")
        self.assertEqual(res.status_code, 200)
        self.assertIn("parts", res.json())

    def test_scan(self):
        res = self.client.post("/api/inspection/scan", json={"simulate_defect": "CRACK"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["metrics"]["inspection_verdict"], "REJECT")

if __name__ == "__main__":
    unittest.main()
