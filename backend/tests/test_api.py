from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] in ["ok", "healthy"]
    print("[PASS] Health Check Passed")

def test_list_templates():
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 3
    ids = [t["id"] for t in data]
    assert "tenancy_agreement" in ids
    assert "nda_agreement" in ids
    assert "freelance_contract" in ids
    print("[PASS] List Templates Passed (Found 3 legal templates)")

def test_generate_document():
    resp = client.post("/api/generate", json={
        "document_type": "tenancy_agreement",
        "language": "bn",
        "data": {
            "execution_date": "১২ সেপ্টেম্বর, ২০২৬",
            "landlord_name": "মো: রফিকুল ইসলাম",
            "tenant_name": "মো: তানভীর আহমেদ",
            "rent_amount": "২৫,০০০"
        }
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "rendered_html" in body
    assert "রফিকুল ইসলাম" in body["rendered_html"]
    assert "২৫,০০০" in body["rendered_html"]
    print("[PASS] Document Generation HTML Passed")

def test_ai_refine_clause():
    resp = client.post("/api/ai/refine-clause", json={
        "raw_text": "ভাড়াটিয়া কোনো পোষা কুকুর বা বিড়াল রাখতে পারবে না",
        "document_type": "tenancy_agreement",
        "language": "bn"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "refined_clause" in data
    assert len(data["refined_clause"]) > 10
    print("[PASS] AI Clause Refine Passed:", data["title"])

def test_ai_explain_clause():
    resp = client.post("/api/ai/explain-clause", json={
        "clause_text": "২য় পক্ষ ১ম পক্ষকে ৩ মাসের সমপরিমাণ টাকা ফেরতযোগ্য জামানত প্রদান করিবেন।",
        "language": "bn"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "simple_explanation" in data
    assert len(data["key_obligations"]) > 0
    print("[PASS] AI Clause Explainer Passed")

def test_ai_audit():
    resp = client.post("/api/ai/audit", json={
        "document_type": "tenancy_agreement",
        "data": {
            "rent_amount": 30000,
            "deposit_amount": 10000,
            "notice_period_months": 1
        }
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "score" in data
    assert len(data["issues"]) > 0
    print(f"[PASS] AI Contract Audit Passed (Score: {data['score']}/100, Issues: {len(data['issues'])})")

def test_export_pdf():
    resp = client.post("/api/export/pdf", json={
        "document_type": "tenancy_agreement",
        "language": "bn",
        "data": {
            "landlord_name": "টেস্ট মালিক",
            "tenant_name": "টেস্ট ভাড়াটিয়া"
        }
    })
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 1000
    print(f"[PASS] PDF Generation Passed (Size: {len(resp.content)} bytes)")

def test_export_docx():
    resp = client.post("/api/export/docx", json={
        "document_type": "tenancy_agreement",
        "language": "bn",
        "data": {
            "landlord_name": "টেস্ট মালিক",
            "tenant_name": "টেস্ট ভাড়াটিয়া"
        }
    })
    assert resp.status_code == 200
    assert len(resp.content) > 1000
    print(f"[PASS] Word DOCX Generation Passed (Size: {len(resp.content)} bytes)")

def test_index_frontend():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "SmartLegal AI" in resp.text
    print("[PASS] Frontend HTML Serving Passed")

if __name__ == "__main__":
    test_health()
    test_list_templates()
    test_generate_document()
    test_ai_refine_clause()
    test_ai_explain_clause()
    test_ai_audit()
    test_export_pdf()
    test_export_docx()
    test_index_frontend()
    print("\n[SUCCESS] ALL 9 TEST SUITES PASSED SUCCESSFULLY!")
