import unittest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import init_db

class TestWeatherAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_forecasts(self):
        res = self.client.get("/api/weather/forecasts")
        self.assertEqual(res.status_code, 200)
        self.assertIn("records", res.json())

    def test_nowcast(self):
        res = self.client.post("/api/weather/nowcast", json={
            "location_station": "Station Test Alpha",
            "lead_time_hours": 3,
            "temperature_c": 30.0,
            "pressure_hpa": 990.0,
            "wind_kmh": 70.0,
            "humidity_pct": 95.0,
            "radar_reflectivity_dbz": 55.0
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("event_class", res.json()["metrics"])

if __name__ == "__main__":
    unittest.main()
