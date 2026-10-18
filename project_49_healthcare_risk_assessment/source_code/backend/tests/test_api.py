import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestHealthAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_assessments(self):
        res = self.client.get("/api/patients/assessments")
        self.assertEqual(res.status_code, 200)
        self.assertIn("assessments", res.json())

    def test_assess(self):
        res = self.client.post("/api/patients/assess", json={
            "full_name": "Test Patient",
            "patient_id": "PAT-TEST",
            "age": 55,
            "gender": "Female",
            "systolic_bp": 140.0,
            "diastolic_bp": 90.0,
            "hba1c": 6.8,
            "fasting_glucose": 130.0,
            "cholesterol": 210.0,
            "hdl": 50.0,
            "ldl": 140.0,
            "egfr": 75.0,
            "bmi": 28.5
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("cardiovascular_risk_pct", res.json()["metrics"])

if __name__ == "__main__":
    unittest.main()
