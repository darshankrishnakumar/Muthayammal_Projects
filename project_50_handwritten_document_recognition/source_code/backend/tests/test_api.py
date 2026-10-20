import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.app.main import app
from backend.app.db.session import init_db

class TestIDPAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, 200)

    def test_documents(self):
        res = self.client.get("/api/idp/documents")
        self.assertEqual(res.status_code, 200)
        self.assertIn("documents", res.json())

    def test_process(self):
        res = self.client.post("/api/idp/process", json={
            "document_type": "HOSPITAL_CLINICAL_INTAKE",
            "simulate_cursive_unclear": False
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn("patient_or_client_name", res.json()["metrics"])

if __name__ == "__main__":
    unittest.main()
