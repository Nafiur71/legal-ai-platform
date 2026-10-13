import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os
import io
from fastapi import FastAPI, HTTPException, Response, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from app.config import FRONTEND_DIR, STATIC_DIR, PORT, HOST
from app.schemas.document_schemas import (
    RefineClauseRequest, RefineClauseResponse,
    ExplainClauseRequest, ExplainClauseResponse,
    AuditContractRequest, AuditContractResponse,
    GenerateDocumentRequest, GenerateDocumentResponse,
    SaveContractRequest, AuditUploadRequest,
    LegalChatRequest, StampCalculateRequest, RemoteSignRequest,
    GenerateNoticeRequest, GenerateNoticeResponse,
    GenerateHashRequest, VerifyHashRequest, ApplyWatermarkRequest
)
from app.services.template_engine import template_engine
from app.services.ai_service import ai_service
from app.services.pdf_service import pdf_service
from app.services.stamp_calculator import stamp_calculator
from app.services.notice_generator import notice_generator
from app.services.security_service import security_service
from app.database import save_contract, list_contracts, get_contract, delete_contract, update_remote_signature

app = FastAPI(
    title="Smart AI Legal Automation Platform",
    description="Intelligent legal contract generator with AI assistant chatbot, stamp calculator, remote signing & PDF export.",
    version="3.0.0 (Phase 5 Production)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Smart AI Legal Automation Platform", "version": "2.5.0"}

@app.get("/api/templates")
def list_available_templates():
    return template_engine.list_templates()

@app.post("/api/generate", response_model=GenerateDocumentResponse)
def generate_document(req: GenerateDocumentRequest):
    try:
        render_data = dict(req.data)
        if req.show_stamp is not None:
            render_data["show_stamp"] = req.show_stamp

        html = template_engine.render_html(req.document_type, render_data, req.language)
        if req.watermark_type and req.watermark_type.lower() not in ["none", ""]:
            html = security_service.apply_watermark(html, req.watermark_type)

        meta = template_engine.get_template_meta(req.document_type)
        title = meta["title_bn"] if req.language == "bn" else meta["title_en"]
        return GenerateDocumentResponse(
            title=title,
            rendered_html=html,
            raw_data=req.data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rendering error: {str(e)}")

@app.post("/api/ai/refine-clause", response_model=RefineClauseResponse)
def refine_clause(req: RefineClauseRequest):
    try:
        res = ai_service.refine_clause(req.raw_text, req.document_type, req.language)
        return RefineClauseResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/explain-clause", response_model=ExplainClauseResponse)
def explain_clause(req: ExplainClauseRequest):
    try:
        res = ai_service.explain_clause(req.clause_text, req.language)
        return ExplainClauseResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/audit", response_model=AuditContractResponse)
def audit_contract(req: AuditContractRequest):
    try:
        res = ai_service.audit_contract(req.document_type, req.data)
        return AuditContractResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/audit-upload")
def audit_uploaded_document(req: AuditUploadRequest):
    try:
        res = ai_service.audit_uploaded_document(req.raw_text, req.filename)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/upload-file-audit")
async def upload_file_for_audit(file: UploadFile = File(...)):
    try:
        content_bytes = await file.read()
        filename = file.filename or "uploaded_contract.pdf"
        extracted_text = ""

        if filename.lower().endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(content_bytes))
                extracted_text = "\n".join([page.extract_text() or "" for page in reader.pages])
            except Exception as pe:
                extracted_text = f"PDF text extraction note: {str(pe)}"
        elif filename.lower().endswith(".docx"):
            try:
                import docx
                doc = docx.Document(io.BytesIO(content_bytes))
                extracted_text = "\n".join([p.text for p in doc.paragraphs if p.text])
            except Exception as de:
                extracted_text = f"DOCX text extraction note: {str(de)}"
        else:
            extracted_text = content_bytes.decode("utf-8", errors="ignore")

        if not extracted_text or len(extracted_text.strip()) < 10:
            extracted_text = f"Uploaded contract from file: {filename}. Standard commercial legal draft with default clauses."

        res = ai_service.audit_uploaded_document(extracted_text, filename=filename)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File audit failed: {str(e)}")

# AI Legal Assistant Chatbot
@app.post("/api/ai/legal-chat")
def legal_assistant_chat(req: LegalChatRequest):
    try:
        answer = ai_service.ask_legal_assistant(req.question, req.contract_context)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Bangladesh Stamp Duty Calculator
@app.post("/api/tools/stamp-calculator")
def calculate_stamp(req: StampCalculateRequest):
    try:
        return stamp_calculator.calculate_stamp_duty(
            doc_type=req.doc_type,
            rent_amount=req.rent_amount or 0,
            duration_months=req.duration_months or 12,
            deposit_amount=req.deposit_amount or 0,
            total_capital=req.total_capital or 0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Phase 5: Legal Notice Generator
@app.post("/api/tools/generate-notice", response_model=GenerateNoticeResponse)
def generate_legal_notice(req: GenerateNoticeRequest):
    try:
        res = notice_generator.generate_notice(
            notice_type=req.notice_type,
            contract_data=req.contract_data,
            custom_reason=req.custom_reason or ""
        )
        return GenerateNoticeResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notice generation error: {str(e)}")

# Phase 5: Cryptographic SHA-256 Fingerprint Generator
@app.post("/api/tools/generate-hash")
def generate_contract_hash(req: GenerateHashRequest):
    try:
        if req.content:
            sha = security_service.compute_sha256(req.content)
            short_h = sha[:12].upper()
            return {
                "sha256": sha,
                "short_hash": short_h,
                "ref_id": f"SLA-SEC-{short_h}",
                "status": "SECURED_SHA256"
            }
        else:
            return security_service.generate_fingerprint(
                doc_type=req.doc_type or "general",
                data=req.data or {}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hashing error: {str(e)}")

# Phase 5: Cryptographic Hash Verification
@app.post("/api/tools/verify-hash")
def verify_contract_hash(req: VerifyHashRequest):
    try:
        return security_service.verify_integrity(req.content, req.expected_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")

# Phase 5: Watermark Application
@app.post("/api/tools/apply-watermark")
def apply_watermark_route(req: ApplyWatermarkRequest):
    try:
        watermarked = security_service.apply_watermark(
            html=req.html_content,
            watermark_type=req.watermark_type or "draft"
        )
        return {"rendered_html": watermarked}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Watermark error: {str(e)}")

# Database Contract Management
@app.get("/api/contracts")
def get_all_contracts():
    return list_contracts()

@app.post("/api/contracts")
def save_new_contract(req: SaveContractRequest, request: Request):
    try:
        client_ip = request.client.host if request.client else "127.0.0.1"
        cid = save_contract(req.title, req.document_type, req.language, req.data, req.id, client_ip)
        return {"status": "saved", "id": cid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contracts/{contract_id}")
def fetch_single_contract(contract_id: str):
    item = get_contract(contract_id)
    if not item:
        raise HTTPException(status_code=404, detail="Contract not found")
    return item

@app.delete("/api/contracts/{contract_id}")
def remove_single_contract(contract_id: str):
    success = delete_contract(contract_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found")
    return {"status": "deleted", "id": contract_id}

# Dedicated Remote Sign Page (Party 2)
@app.get("/sign/{contract_id}", response_class=HTMLResponse)
def remote_signing_page(contract_id: str):
    item = get_contract(contract_id)
    if not item:
        # Search by ref_id or SLA-BD-xxxx
        for c in list_contracts():
            if c.get("id", "").lower() == contract_id.lower() or c.get("data", {}).get("ref_id", "").lower() == contract_id.lower():
                item = get_contract(c["id"])
                break
    if not item:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    html = template_engine.render_html(item["document_type"], item["data"], item.get("language", "bn"))
    tmpl = template_engine.env.get_template("signing_portal.html")
    rendered_portal = tmpl.render(contract=item, rendered_html=html)
    return HTMLResponse(content=rendered_portal)

# Remote Share & Signing API
@app.get("/api/contracts/share/{contract_id}")
def get_shared_contract(contract_id: str):
    item = get_contract(contract_id)
    if not item:
        for c in list_contracts():
            if c.get("id", "").lower() == contract_id.lower() or c.get("data", {}).get("ref_id", "").lower() == contract_id.lower():
                item = get_contract(c["id"])
                break
    if not item:
        raise HTTPException(status_code=404, detail="Contract not found")
    html = template_engine.render_html(item["document_type"], item["data"], item.get("language", "bn"))
    return {
        "id": item["id"],
        "title": item["title"],
        "document_type": item["document_type"],
        "language": item.get("language", "bn"),
        "rendered_html": html,
        "data": item["data"]
    }

@app.post("/api/contracts/share/{contract_id}/sign")
def submit_remote_signature(contract_id: str, req: RemoteSignRequest, request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    success = update_remote_signature(contract_id, req.signature_data, req.target or "party2", client_ip)
    if not success:
        # Check by ref_id
        for c in list_contracts():
            if c.get("id", "").lower() == contract_id.lower() or c.get("data", {}).get("ref_id", "").lower() == contract_id.lower():
                success = update_remote_signature(c["id"], req.signature_data, req.target or "party2", client_ip)
                contract_id = c["id"]
                break
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found")
    return {"status": "signature_saved", "id": contract_id}

# Public Verification Landing Page (QR Code target)
@app.get("/verify/{contract_id}", response_class=HTMLResponse)
def verify_contract_page(contract_id: str):
    item = get_contract(contract_id)
    if not item:
        for c in list_contracts():
            if c.get("id", "").lower() == contract_id.lower() or c.get("data", {}).get("ref_id", "").lower() == contract_id.lower() or f"sla-bd-{c.get('id', '').lower()}" == contract_id.lower():
                item = get_contract(c["id"])
                break
    is_verified = bool(item)
    if not item:
        item = {
            "id": contract_id,
            "ref_id": contract_id,
            "title": "অনিশ্চিত বা অপ্রাপ্ত দলিল (Unverified Contract)",
            "document_type": "Unknown",
            "party1_name": "অজ্ঞাত",
            "party2_name": "অজ্ঞাত",
            "status": "unverified",
            "created_at": "N/A",
            "sha256_hash": "N/A"
        }
    tmpl = template_engine.env.get_template("verification_portal.html")
    html_page = tmpl.render(contract=item, is_verified=is_verified)
    return HTMLResponse(content=html_page)

# Public Verification JSON API
@app.get("/api/verify/{contract_id}")
def verify_contract_api(contract_id: str):
    item = get_contract(contract_id)
    if not item:
        for c in list_contracts():
            if c.get("id", "").lower() == contract_id.lower() or c.get("data", {}).get("ref_id", "").lower() == contract_id.lower() or f"sla-bd-{c.get('id', '').lower()}" == contract_id.lower():
                item = get_contract(c["id"])
                break
    if not item:
        return {"is_valid": False, "status": "not_found", "message": "Contract record not found"}
    return {
        "is_valid": True,
        "id": item["id"],
        "ref_id": item.get("data", {}).get("ref_id", f"SLA-BD-{item['id'].upper()}"),
        "title": item["title"],
        "document_type": item["document_type"],
        "status": item.get("status", "draft"),
        "party1_name": item.get("party1_name", ""),
        "party2_name": item.get("party2_name", ""),
        "party1_signed_at": item.get("party1_signed_at", ""),
        "party2_signed_at": item.get("party2_signed_at", ""),
        "sha256_hash": item.get("sha256_hash", ""),
        "created_at": item["created_at"],
        "updated_at": item["updated_at"]
    }

# Certificate of Completion & Digital Audit Trail
@app.get("/api/contracts/{contract_id}/certificate", response_class=HTMLResponse)
def get_certificate_of_completion(contract_id: str):
    item = get_contract(contract_id)
    if not item:
        for c in list_contracts():
            if c.get("id", "").lower() == contract_id.lower() or c.get("data", {}).get("ref_id", "").lower() == contract_id.lower():
                item = get_contract(c["id"])
                break
    if not item:
        raise HTTPException(status_code=404, detail="Contract not found")
    tmpl = template_engine.env.get_template("certificate_of_completion.html")
    html_page = tmpl.render(contract=item)
    return HTMLResponse(content=html_page)

@app.post("/api/export/pdf")
def export_pdf(req: GenerateDocumentRequest):
    try:
        render_data = dict(req.data)
        if req.show_stamp is not None:
            render_data["show_stamp"] = req.show_stamp

        html = template_engine.render_html(req.document_type, render_data, req.language)
        if req.watermark_type and req.watermark_type.lower() not in ["none", ""]:
            html = security_service.apply_watermark(html, req.watermark_type)

        pdf_bytes = pdf_service.convert_html_to_pdf(html)
        filename = f"{req.document_type}_{req.language}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.post("/api/export/docx")
def export_docx(req: GenerateDocumentRequest):
    try:
        docx_stream = template_engine.generate_docx(req.document_type, req.data, req.language)
        filename = f"{req.document_type}.docx"
        return StreamingResponse(
            docx_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX generation failed: {str(e)}")

# Mount static frontend
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Frontend not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
