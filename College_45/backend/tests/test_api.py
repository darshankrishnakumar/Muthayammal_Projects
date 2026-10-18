import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestCareerAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_roles(self):
        res = self.client.get("/api/career/roles")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.json()["count"], 1)

    def test_analyze(self):
        res = self.client.post("/api/career/analyze", json={
            "user_name": "Test User",
            "current_skills": "Python, SQL",
            "target_role_id": "ROLE-DATA"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("readiness_score", res.json()["metrics"])

if __name__ == "__main__":
    unittest.main()
