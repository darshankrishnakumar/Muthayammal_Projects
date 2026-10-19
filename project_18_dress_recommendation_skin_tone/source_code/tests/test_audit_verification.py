import os
import unittest

class TestProject18AuditVerification(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def test_requirements_file_exists(self):
        req_path = os.path.join(self.root_dir, "requirements.txt")
        self.assertTrue(os.path.exists(req_path), f"requirements.txt missing at {req_path}")

    def test_technical_documentation_exists(self):
        docx_path = os.path.join(self.root_dir, "docs", "technical_documentation.docx")
        self.assertTrue(os.path.exists(docx_path), f"technical_documentation.docx missing at {docx_path}")

    def test_project_presentation_exists(self):
        pptx_path = os.path.join(self.root_dir, "presentations", "project_presentation.pptx")
        self.assertTrue(os.path.exists(pptx_path), f"project_presentation.pptx missing at {pptx_path}")

if __name__ == "__main__":
    unittest.main()
