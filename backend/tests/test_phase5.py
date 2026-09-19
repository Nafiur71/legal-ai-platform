from fastapi.testclient import TestClient
from app.main import app
from app.services.notice_generator import notice_generator
from app.services.security_service import security_service

client = TestClient(app)

def test_notice_generator_service():
    contract_data = {
        "landlord_name": "রহিম চৌধুরী",
        "tenant_name": "করিম আহমেদ",
        "property_address": "বাড়ি #১২, ধানমন্ডি, ঢাকা",
        "rent_amount": "২৫,০০০"
    }

    # Test Vacate Notice
    vacate = notice_generator.generate_notice("vacate_notice", contract_data, "ব্যক্তিগত ব্যবহারের জন্য")
    assert vacate["notice_type"] == "vacate_notice"
    assert "Vacate Notice" in vacate["title"]
    assert "করিম আহমেদ" in vacate["body"]
    assert "ধানমন্ডি" in vacate["body"]
    print("[PASS] Vacate Notice Generator passed")

    # Test Renewal Notice
    renewal = notice_generator.generate_notice("renewal_notice", contract_data)
    assert renewal["notice_type"] == "renewal_notice"
    assert "Renewal" in renewal["title"]
    assert "২৫,০০০" in renewal["body"]
    print("[PASS] Renewal Notice Generator passed")

    # Test Demand Notice
    demand = notice_generator.generate_notice("demand_notice", contract_data, "বিগত ২ মাসের ভাড়া বকেয়া")
    assert demand["notice_type"] == "demand_notice"
    assert "Demand Notice" in demand["title"]
    assert "বকেয়া" in demand["body"]
    print("[PASS] Demand Notice Generator passed")

def test_api_notice_generator():
    resp = client.post("/api/tools/generate-notice", json={
        "notice_type": "vacate_notice",
        "contract_data": {
            "landlord_name": "আনিসুর রহমান",
            "tenant_name": "ফারহান হাবিব",
            "property_address": "গুলশান-১, ঢাকা",
            "rent_amount": "৫০,০০০"
        },
        "custom_reason": "ফ্ল্যাট সংস্কারের কাজ শুরু হবে"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["notice_type"] == "vacate_notice"
    assert "ফারহান হাবিব" in data["body"]
    print("[PASS] API /api/tools/generate-notice passed")

def test_security_hash_generation():
    text = "আমি প্রথম পক্ষ এবং দ্বিতীয় পক্ষ অত্র চুক্তিতে সম্মত হইলাম।"
    h1 = security_service.compute_sha256(text)
    h2 = security_service.compute_sha256(text)
    assert h1 == h2
    assert len(h1) == 64

    # Tampered test
    tampered_text = "আমি প্রথম পক্ষ এবং দ্বিতীয় পক্ষ অত্র চুক্তিতে সম্মত হইলাম না।"
    h3 = security_service.compute_sha256(tampered_text)
    assert h1 != h3
    print("[PASS] Security SHA-256 generation & sensitivity passed")

def test_api_hash_and_verification():
    content = "বাৎসরিক ভাড়া পরিশোধের শর্তাবলি এবং আইনানুগ অঙ্গীকার।"
    # 1. Generate hash via API
    resp = client.post("/api/tools/generate-hash", json={"content": content})
    assert resp.status_code == 200
    gen_data = resp.json()
    assert "sha256" in gen_data
    sha = gen_data["sha256"]

    # 2. Verify with authentic content
    resp_valid = client.post("/api/tools/verify-hash", json={
        "content": content,
        "expected_hash": sha
    })
    assert resp_valid.status_code == 200
    assert resp_valid.json()["is_valid"] is True
    assert resp_valid.json()["tampered"] is False
    print("[PASS] Hash verification (Authentic) passed")

    # 3. Verify with tampered content
    resp_tampered = client.post("/api/tools/verify-hash", json={
        "content": content + " অতিরিক্ত অননুমোদিত বাক্য।",
        "expected_hash": sha
    })
    assert resp_tampered.status_code == 200
    assert resp_tampered.json()["is_valid"] is False
    assert resp_tampered.json()["tampered"] is True
    print("[PASS] Hash verification (Tampered detection) passed")

def test_watermark_application():
    html_sample = "<html><body><h1>চুক্তিপত্র</h1><p>শর্ত ১</p></body></html>"
    watermarked = security_service.apply_watermark(html_sample, "draft")
    assert "sla-watermark-overlay" in watermarked
    assert "DRAFT" in watermarked

    confidential = security_service.apply_watermark(html_sample, "confidential")
    assert "CONFIDENTIAL" in confidential
    print("[PASS] Watermark injection passed")

    # API test
    resp = client.post("/api/tools/apply-watermark", json={
        "html_content": html_sample,
        "watermark_type": "draft"
    })
    assert resp.status_code == 200
    assert "sla-watermark-overlay" in resp.json()["rendered_html"]
    print("[PASS] API /api/tools/apply-watermark passed")

if __name__ == "__main__":
    print("\n--- RUNNING PHASE 5 TEST SUITE ---")
    test_notice_generator_service()
    test_api_notice_generator()
    test_api_hash_and_verification()
    test_watermark_application()
    print("[SUCCESS] ALL PHASE 5 TESTS PASSED!\n")
