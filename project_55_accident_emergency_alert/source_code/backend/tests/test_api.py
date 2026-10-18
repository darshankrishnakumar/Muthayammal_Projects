"""
REST API Integration and Health Tests for Project 55.
"""

import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db


class TestAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data["status"], ["HEALTHY", "DEGRADED"])
        self.assertIn("inference_hardware", data)
        self.assertIn("models_loaded", data)

    def test_list_cameras(self):
        response = self.client.get("/api/streams/cameras")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("cameras", data)
        self.assertGreaterEqual(data["count"], 1)
        cam = data["cameras"][0]
        self.assertIn("camera_id", cam)
        self.assertIn("stream_endpoint", cam)

    def test_list_incidents(self):
        response = self.client.get("/api/incidents/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("incidents", data)
        self.assertIn("count", data)

    def test_analytics_summary(self):
        response = self.client.get("/api/analytics/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("kpis", data)
        self.assertIn("severity_distribution", data)
        self.assertIn("model_comparison", data)
        self.assertLessEqual(data["kpis"]["mean_time_to_detect_sec"], 1.5)


if __name__ == "__main__":
    unittest.main()
