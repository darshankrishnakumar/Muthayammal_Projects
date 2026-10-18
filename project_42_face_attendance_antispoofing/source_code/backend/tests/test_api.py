import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestAttendanceAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_students(self):
        res = self.client.get("/api/attendance/students")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.json()["count"], 1)

    def test_verify_real(self):
        res = self.client.post("/api/attendance/verify", json={"student_index": 0, "simulate_spoof_attack": False})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["metrics"]["status"], "PRESENT")

    def test_verify_spoof(self):
        res = self.client.post("/api/attendance/verify", json={"student_index": 1, "simulate_spoof_attack": True})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["metrics"]["status"], "REJECTED_SPOOF")

if __name__ == "__main__":
    unittest.main()
