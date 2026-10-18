import unittest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.main import app
from backend.app.db.session import init_db

class TestPROJECT048(unittest.TestCase):
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
        num = 48
        if num == 46:
            res = self.client.get("/api/inspection/parts")
            self.assertEqual(res.status_code, 200)
            self.assertIn("parts", res.json())
        elif num == 47:
            res = self.client.get("/api/engagement/timeline")
            self.assertEqual(res.status_code, 200)
            self.assertIn("snapshots", res.json())
        elif num == 48:
            res = self.client.get("/api/freshness/batches")
            self.assertEqual(res.status_code, 200)
            self.assertIn("batches", res.json())
        elif num == 49:
            res = self.client.get("/api/patients/assessments")
            self.assertEqual(res.status_code, 200)
            self.assertIn("assessments", res.json())
        elif num == 50:
            res = self.client.get("/api/idp/documents")
            self.assertEqual(res.status_code, 200)
            self.assertIn("documents", res.json())

if __name__ == "__main__":
    unittest.main()
