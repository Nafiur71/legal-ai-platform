import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestEnglishMode(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.templates = [
            'tenancy_agreement',
            'nda_agreement',
            'freelance_contract',
            'partnership_agreement',
            'employment_agreement'
        ]

    def test_english_rendering_all_templates(self):
        for doc_type in self.templates:
            res = self.client.post('/api/generate', json={
                'document_type': doc_type,
                'language': 'en',
                'data': {}
            })
            self.assertEqual(res.status_code, 200)
            html = res.json().get('rendered_html', '')
            self.assertIn("GOVERNMENT OF THE PEOPLE'S REPUBLIC OF BANGLADESH", html)
            self.assertIn("NON-JUDICIAL STAMP (300 BDT)", html)
            self.assertIn("DIGITALLY CERTIFIED", html)
            self.assertIn("AND", html)
            print(f"[PASS] Template {doc_type} rendered successfully in English")

    def test_english_pdf_generation(self):
        res = self.client.post('/api/export/pdf', json={
            'document_type': 'tenancy_agreement',
            'language': 'en',
            'data': {
                'landlord_name': 'John Doe',
                'tenant_name': 'Jane Smith'
            }
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('content-type'), 'application/pdf')
        self.assertTrue(len(res.content) > 1000)
        print(f"[PASS] English PDF generated successfully (Size: {len(res.content)} bytes)")

    def test_english_docx_generation(self):
        res = self.client.post('/api/export/docx', json={
            'document_type': 'partnership_agreement',
            'language': 'en',
            'data': {
                'partner1_name': 'Alice Smith',
                'partner2_name': 'Bob Jones'
            }
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.wordprocessingml.document', res.headers.get('content-type'))
        self.assertTrue(len(res.content) > 1000)
        print(f"[PASS] English DOCX generated successfully (Size: {len(res.content)} bytes)")

if __name__ == '__main__':
    unittest.main()
