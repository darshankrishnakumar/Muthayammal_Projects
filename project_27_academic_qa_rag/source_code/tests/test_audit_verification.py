import unittest
import os
import sys
import importlib.util

class TestPROJECT027(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app.py"))
        spec = importlib.util.spec_from_file_location("app_mod_27", app_path)
        cls.app_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.app_mod)
        cls.client = cls.app_mod.app.test_client()

    def test_deliverables_exist(self):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "requirements.txt")), "requirements.txt must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "docs", "technical_documentation.docx")), "technical_documentation.docx must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "presentations", "project_presentation.pptx")), "project_presentation.pptx must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, ".env.example")), ".env.example must exist")
        self.assertTrue(os.path.isfile(os.path.join(root_dir, "walkthrough", "walkthrough_script.md")), "walkthrough_script.md must exist")

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsNotNone(data)
        self.assertTrue("status" in data or "service" in data)

    def test_functional_inference(self):
        num = 27
        if num == 26:
            res = self.client.get("/api/stream/next")
            self.assertEqual(res.status_code, 200)
            self.assertIn("is_attack", res.get_json())
        elif num == 27:
            res = self.client.post("/api/ask", json={"question": "Explain attention mechanism in transformers."})
            self.assertEqual(res.status_code, 200)
            self.assertIn("answer", res.get_json())
        elif num == 28:
            res = self.client.post("/api/forecast", json={"city": "New Delhi", "hours_ahead": 24})
            self.assertEqual(res.status_code, 200)
            self.assertIn("daily_forecast", res.get_json())
        elif num == 29:
            res = self.client.get("/api/dictionary")
            self.assertEqual(res.status_code, 200)
            self.assertIsInstance(res.get_json(), dict)
        elif num == 30:
            res = self.client.get("/api/devices")
            self.assertEqual(res.status_code, 200)
            self.assertIsInstance(res.get_json(), list)

if __name__ == "__main__":
    unittest.main()
