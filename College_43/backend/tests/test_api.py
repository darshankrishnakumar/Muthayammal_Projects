import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestForgeryAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_audits(self):
        res = self.client.get("/api/forensics/audits")
        self.assertEqual(res.status_code, 200)
        self.assertIn("audits", res.json())

    def test_analyze(self):
        res = self.client.post("/api/forensics/analyze", json={"document_title": "Test Doc", "simulate_forgery": True})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["metrics"]["forgery_verdict"], "FORGED")

if __name__ == "__main__":
    unittest.main()
