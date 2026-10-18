import unittest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.main import app
from backend.app.db.session import init_db

class TestPROJECT045(unittest.TestCase):
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
        num = 45
        if num == 41:
            res = self.client.get("/api/grading/items")
            self.assertEqual(res.status_code, 200)
            self.assertIn("items", res.json())
        elif num == 42:
            res = self.client.get("/api/attendance/students")
            self.assertEqual(res.status_code, 200)
            self.assertGreaterEqual(res.json()["count"], 1)
        elif num == 43:
            res = self.client.get("/api/forensics/audits")
            self.assertEqual(res.status_code, 200)
            self.assertIn("audits", res.json())
        elif num == 44:
            res = self.client.get("/api/screening/jobs")
            self.assertEqual(res.status_code, 200)
            self.assertGreaterEqual(res.json()["count"], 1)
        elif num == 45:
            res = self.client.get("/api/career/roles")
            self.assertEqual(res.status_code, 200)
            self.assertGreaterEqual(res.json()["count"], 1)

if __name__ == "__main__":
    unittest.main()
