import sys
import os
import io
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestPhase6Features(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_dynamic_qr_code_rendering(self):
        res = self.client.post("/api/generate", json={
            "document_type": "tenancy_agreement",
            "data": {
                "landlord_name": "করিম সাহেব",
                "tenant_name": "রহিম উদ্দিন",
                "rent_amount": "25000"
            },
            "language": "bn"
        })
        self.assertEqual(res.status_code, 200)
        html = res.json()["rendered_html"]
        self.assertIn("data:image/png;base64,", html)
        self.assertIn("/verify/", html)
        print("[PASS] Dynamic QR Code and Verification link verified in rendered HTML")

    def test_multi_party_contract_lifecycle_and_verification(self):
        # 1. Save contract as draft
        save_res = self.client.post("/api/contracts", json={
            "title": "বাণিজ্যিক অফিস চুক্তিপত্র",
            "document_type": "tenancy_agreement",
            "language": "bn",
            "data": {
                "landlord_name": "আব্দুল কাদের",
                "tenant_name": "জাফর ইকবাল",
                "rent_amount": "50000"
            }
        })
        self.assertEqual(save_res.status_code, 200)
        cid = save_res.json()["id"]

        # Verify initial status is draft
        get_res = self.client.get(f"/api/contracts/{cid}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["status"], "draft")

        # 2. Party 1 signs -> status becomes pending_party2
        p1_sign_res = self.client.post(f"/api/contracts/share/{cid}/sign", json={
            "signature_data": "data:image/png;base64,mockparty1sig",
            "target": "party1"
        })
        self.assertEqual(p1_sign_res.status_code, 200)
        get_res = self.client.get(f"/api/contracts/{cid}")
        self.assertEqual(get_res.json()["status"], "pending_party2")

        # 3. Party 2 signs via remote signing endpoint -> status becomes completed
        p2_sign_res = self.client.post(f"/api/contracts/share/{cid}/sign", json={
            "signature_data": "data:image/png;base64,mockparty2sig",
            "target": "party2"
        })
        self.assertEqual(p2_sign_res.status_code, 200)
        get_res = self.client.get(f"/api/contracts/{cid}")
        self.assertEqual(get_res.json()["status"], "completed")
        self.assertTrue(bool(get_res.json()["sha256_hash"]))

        # 4. Verify public landing page renders successfully
        verify_page_res = self.client.get(f"/verify/{cid}")
        self.assertEqual(verify_page_res.status_code, 200)
        self.assertIn("স্মার্টলিগ্যাল ডিজিটাল সত্যতা যাচাই পোর্টাল", verify_page_res.text)
        self.assertIn("VERIFIED", verify_page_res.text)

        # 5. Verify JSON API
        verify_api_res = self.client.get(f"/api/verify/{cid}")
        self.assertEqual(verify_api_res.status_code, 200)
        self.assertTrue(verify_api_res.json()["is_valid"])
        self.assertEqual(verify_api_res.json()["status"], "completed")

        # 6. Verify dedicated remote signing page renders
        sign_page_res = self.client.get(f"/sign/{cid}")
        self.assertEqual(sign_page_res.status_code, 200)
        self.assertIn("আইনি চুক্তিপত্র পর্যালোচনা ও স্বাক্ষর পোর্টাল", sign_page_res.text)

        # 7. Verify Certificate of Completion renders
        cert_res = self.client.get(f"/api/contracts/{cid}/certificate")
        self.assertEqual(cert_res.status_code, 200)
        self.assertIn("অডিট ট্রেইল ও সমাপ্তি সনদ", cert_res.text)
        print("[PASS] Full Multi-party signing lifecycle, verification, and audit trail verified!")

    def test_file_upload_ai_audit(self):
        # Create a mock text file
        mock_text = """
        COMMERCIAL LEASE AGREEMENT
        Between Landlord ABC Corp and Tenant XYZ Ltd.
        Monthly Rent: 50,000 BDT.
        Security Deposit: 20,000 BDT.
        Termination: Landlord may terminate this lease without any prior notice.
        """
        file_obj = io.BytesIO(mock_text.encode("utf-8"))
        res = self.client.post("/api/ai/upload-file-audit", files={
            "file": ("sample_contract.txt", file_obj, "text/plain")
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("score", data)
        self.assertIn("risks_found", data)
        print(f"[PASS] File upload AI Audit verified! Detected score: {data['score']}")

if __name__ == "__main__":
    unittest.main()
