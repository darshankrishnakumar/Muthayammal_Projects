import unittest
import os

class TestPROJECT011(unittest.TestCase):
    def test_requirements_exist(self):
        root_req = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'requirements.txt'))
        self.assertTrue(os.path.isfile(root_req), "requirements.txt must exist at project root")

    def test_docs_exist(self):
        doc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'technical_documentation.docx'))
        self.assertTrue(os.path.isfile(doc_path), "technical_documentation.docx must exist in docs/")

    def test_presentation_exists(self):
        pres_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'presentations', 'project_presentation.pptx'))
        self.assertTrue(os.path.isfile(pres_path), "project_presentation.pptx must exist in presentations/")

if __name__ == '__main__':
    unittest.main()
