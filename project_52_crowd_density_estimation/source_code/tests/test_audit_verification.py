import unittest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.main import app
from backend.app.db.session import init_db

class TestPROJECT052(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_deliverables_exist(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "requirements.txt")), "requirements.txt must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "docs", "technical_documentation.docx")), "technical_documentation.docx must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "presentations", "project_presentation.pptx")), "project_presentation.pptx must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, ".env.example")), ".env.example must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "walkthrough", "walkthrough_script.md")), "walkthrough_script.md must exist")

    def test_health_endpoint(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_functional_inference(self):
        num = 52
        if num == 51:
            res = self.client.get("/api/energy/plans")
            self.assertEqual(res.status_code, 200)
            self.assertIn("plans", res.json())
        elif num == 52:
            res = self.client.get("/api/crowd/events")
            self.assertEqual(res.status_code, 200)
            self.assertIn("events", res.json())
        elif num == 53:
            res = self.client.get("/api/rail/defects")
            self.assertEqual(res.status_code, 200)
            self.assertIn("records", res.json())
        elif num == 54:
            res = self.client.get("/api/weather/forecasts")
            self.assertEqual(res.status_code, 200)
            self.assertIn("records", res.json())
        elif num == 55:
            res = self.client.get("/api/streams/cameras")
            self.assertEqual(res.status_code, 200)
            self.assertIn("cameras", res.json())

if __name__ == "__main__":
    unittest.main()
