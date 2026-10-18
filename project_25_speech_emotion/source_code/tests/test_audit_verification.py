import unittest
import os
import sys
import importlib.util

class TestPROJECT025(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "app.py"))
        spec = importlib.util.spec_from_file_location("app_mod_25", app_path)
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
        num = 25
        if num == 21:
            res = self.client.post("/api/predict", json={"time": 100, "amount": 45.0, "features": {"V14": -4.5, "V4": 3.2}})
            self.assertEqual(res.status_code, 200)
            self.assertIn("decision", res.get_json())
        elif num == 22:
            res = self.client.post("/api/classify", json={"complaint": "My card was charged twice unexpectedly."})
            self.assertEqual(res.status_code, 200)
            self.assertIn("category", res.get_json())
        elif num == 23:
            res = self.client.post("/api/summarize", json={"transcript": "Alice: We have to finish the report by Friday. Bob: Agreed."})
            self.assertEqual(res.status_code, 200)
            self.assertIn("executive_summary", res.get_json())
        elif num == 24:
            res = self.client.get("/api/graph")
            self.assertEqual(res.status_code, 200)
            self.assertIn("nodes", res.get_json())
        elif num == 25:
            res = self.client.post("/api/recognize", json={"language": "en", "preset_emotion": "happy"})
            self.assertEqual(res.status_code, 200)
            self.assertIn("emotion", res.get_json())

if __name__ == "__main__":
    unittest.main()
