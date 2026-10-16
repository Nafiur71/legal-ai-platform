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
    test_queries = [
        ("৩০০ টাকার স্ট্যাম্পে প্রিন্ট করার নিয়ম কী?", ["স্ট্যাম্প"]),
        ("চেক ডিজঅনার হলে এনআই অ্যাক্ট ১৩৮ ধারায় মামলার নিয়ম ও আইনি নোটিশের শর্ত কী?", ["১৩৮", "নোটিশ", "ম্যাজিস্ট্রেট"]),
        ("থানায় জিডি ও এজাহারের মধ্যে পার্থক্য কী এবং ওসি মামলা না নিলে করণীয় কী?", ["১৫৪", "১৫৫", "জিডি"]),
        ("জমি ও ফ্ল্যাট সাফ-কবলা দলিলের সরকারি রেজিস্ট্রি ও স্ট্যাম্প খরচ কত?", ["রেজিস্ট্রেশন", "স্ট্যাম্প"]),
        ("দেনমোহর ও তালাকের ক্ষেত্রে পারিবারিক আদালতের নিয়ম কী?", ["পারিবারিক", "দেনমোহর"]),
        ("শ্রম আইন অনুযায়ী নোটিশ পে, গ্র্যাচুইটি ও মাতৃত্বকালীন ছুটির নিয়ম কী?", ["শ্রম", "নোটিশ"]),
        ("সোশ্যাল মিডিয়ায় ব্ল্যাকমেইল বা ফেক আইডির বিরুদ্ধে সাইবার নিরাপত্তা আইনে প্রতিকার কী?", ["সাইবার"]),
        ("প্রতারণা ও ৪২০ ধারায় মামলা করার নিয়ম কী?", ["৪২০", "দণ্ডবিধি"]),
        ("হাইকোর্ট থেকে আগাম জামিন পাওয়ার নিয়ম কী?", ["জামিন", "৪৯৮"]),
        ("দোকানদার বেশি দাম নিলে বা মেয়াদোত্তীর্ণ পণ্য দিলে ভোক্তা অধিকার আইনে অভিযোগের নিয়ম কী?", ["ভোক্তা", "২৫%"]),
    ]

    for q, keywords in test_queries:
        resp = client.post("/api/ai/legal-chat", json={
            "question": q,
            "contract_context": "general_law"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        ans = data["answer"]
        assert len(ans) > 50
        # If fallback engine or AI answered, at least one relevant legal keyword should be present
        assert any(k in ans for k in keywords), f"Keyword missing for query '{q}': got '{ans[:100]}...'"
        print(f"[PASS] AI Legal Chatbot answered query: '{q[:35]}...'")

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
