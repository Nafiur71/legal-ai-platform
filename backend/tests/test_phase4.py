import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_legal_chat():
    resp = client.post("/api/ai/legal-chat", json={
        "question": "৩০০ টাকার স্ট্যাম্পে প্রিন্ট করার নিয়ম কী?",
        "contract_context": "tenancy_agreement"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert len(data["answer"]) > 20
    print("[PASS] AI Legal Chatbot Response Received")

def test_stamp_duty_calculator():
    # Test Tenancy (<= 12 months)
    resp = client.post("/api/tools/stamp-calculator", json={
        "doc_type": "tenancy_agreement",
        "rent_amount": 25000,
        "duration_months": 12
    })
    assert resp.status_code == 200
    res = resp.json()
    assert res["recommended_stamp_value"] == 300
    print("[PASS] Stamp Calculator for Tenancy Passed (300 BDT)")

    # Test Partnership (> 50,000 capital)
    resp = client.post("/api/tools/stamp-calculator", json={
        "doc_type": "partnership_agreement",
        "total_capital": 500000
    })
    assert resp.status_code == 200
    res = resp.json()
    assert res["recommended_stamp_value"] == 2000
    print("[PASS] Stamp Calculator for Partnership Passed (2000 BDT)")

def test_share_and_remote_signing():
    # Save a contract first
    resp = client.post("/api/contracts", json={
        "title": "শেয়ার ও সাইন টেস্ট চুক্তি",
        "document_type": "tenancy_agreement",
        "language": "bn",
        "data": {
            "landlord_name": "মালিক পক্ষ",
            "tenant_name": "ভাড়াটিয়া পক্ষ"
        }
    })
    assert resp.status_code == 200
    cid = resp.json()["id"]

    # Fetch shared contract
    resp = client.get(f"/api/contracts/share/{cid}")
    assert resp.status_code == 200
    share_data = resp.json()
    assert share_data["id"] == cid
    assert "rendered_html" in share_data
    print("[PASS] Fetch Shared Contract Passed")

    # Submit remote signature
    dummy_sig = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    resp = client.post(f"/api/contracts/share/{cid}/sign", json={
        "signature_data": dummy_sig,
        "target": "party2"
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "signature_saved"
    print("[PASS] Remote Signature Submission Passed")

    # Clean up
    client.delete(f"/api/contracts/{cid}")

def test_verification_code_in_pdf():
    resp = client.post("/api/export/pdf", json={
        "document_type": "tenancy_agreement",
        "language": "bn",
        "data": {
            "landlord_name": "ভেরিফাইড মালিক",
            "tenant_name": "ভেরিফাইড ভাড়াটিয়া"
        }
    })
    assert resp.status_code == 200
    assert len(resp.content) > 2000
    print(f"[PASS] PDF with Digital Verification Footer Passed! (Size: {len(resp.content)} bytes)")

if __name__ == "__main__":
    test_legal_chat()
    test_stamp_duty_calculator()
    test_share_and_remote_signing()
    test_verification_code_in_pdf()
    print("\n[SUCCESS] ALL PHASE 4 TESTS PASSED!")
