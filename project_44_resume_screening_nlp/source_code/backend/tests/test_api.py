import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestScreeningAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_jobs(self):
        res = self.client.get("/api/screening/jobs")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.json()["count"], 1)

    def test_match(self):
        res = self.client.post("/api/screening/match", json={
            "candidate_name": "Test Candidate",
            "candidate_skills": "PyTorch, Python, Docker",
            "experience_years": 4.0,
            "job_id": "JOB-AI-LEAD"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("overall_match_score", res.json()["metrics"])

if __name__ == "__main__":
    unittest.main()
