import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestPROJECT015:
    def test_docs_exist(self):
        doc_path = os.path.join(PROJECT_ROOT, "docs", "technical_documentation.docx")
        assert os.path.exists(doc_path), f"Missing technical_documentation.docx at {doc_path}"

    def test_presentation_exists(self):
        ppt_path = os.path.join(PROJECT_ROOT, "presentations", "project_presentation.pptx")
        assert os.path.exists(ppt_path), f"Missing project_presentation.pptx at {ppt_path}"

    def test_requirements_exist(self):
        req_path = os.path.join(PROJECT_ROOT, "requirements.txt")
        assert os.path.exists(req_path), f"Missing requirements.txt at {req_path}"
