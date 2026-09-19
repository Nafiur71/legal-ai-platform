import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Response, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from app.services.document_parser import extract_text_from_bytes
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
from app.services.cache_service import ai_cache, ai_rate_limiter
from app.database import (
    init_db, save_contract, list_contracts,
    get_contract, delete_contract, update_remote_signature, IS_POSTGRES
)

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (PostgreSQL or SQLite WAL mode) on startup
    await init_db()
    # Pre-warm Chromium in background so initial PDF export is lightning fast
    asyncio.create_task(pdf_service.warm_up_async())
    yield

app = FastAPI(
    title="Smart AI Legal Automation Platform",
    description="High-concurrency intelligent legal contract generator with AI assistant, stamp calculator, remote signing & PDF export.",
    version="3.5.0 (High-Concurrency Async)",
    lifespan=lifespan
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
async def health_check():
    cache_stats = await ai_cache.get_stats()
    return {
        "status": "healthy",
        "service": "Smart AI Legal Automation Platform",
        "database_mode": "PostgreSQL (asyncpg)" if IS_POSTGRES else "SQLite (WAL mode)",
        "active_cache_items": cache_stats.get("active_cached_items", 0),
        "version": "3.5.0-production"
    }

@app.get("/api/templates")
async def list_available_templates():
    return template_engine.list_templates()

@app.post("/api/generate", response_model=GenerateDocumentResponse)
async def generate_document(req: GenerateDocumentRequest):
    try:
        html = template_engine.render_html(req.document_type, req.data, req.language)
        meta = template_engine.get_template_meta(req.document_type)
        title = meta["title_bn"] if req.language == "bn" else meta["title_en"]
        return GenerateDocumentResponse(
            title=title,
            rendered_html=html,
            raw_data=req.data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rendering error: {str(e)}")

async def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    allowed, wait_sec = await ai_rate_limiter.check(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded (12 requests/minute). Please wait {wait_sec} seconds before submitting more AI requests."
        )

@app.get("/api/cache/stats")
async def get_cache_statistics():
    return await ai_cache.get_stats()

@app.post("/api/ai/refine-clause", response_model=RefineClauseResponse)
async def refine_clause(req: RefineClauseRequest, request: Request):
    await check_rate_limit(request)
    try:
        res = await ai_service.refine_clause(req.raw_text, req.document_type, req.language)
        return RefineClauseResponse(**res)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/explain-clause", response_model=ExplainClauseResponse)
async def explain_clause(req: ExplainClauseRequest, request: Request):
    await check_rate_limit(request)
    try:
        res = await ai_service.explain_clause(req.clause_text, req.language)
        return ExplainClauseResponse(**res)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/audit", response_model=AuditContractResponse)
async def audit_contract(req: AuditContractRequest, request: Request):
    await check_rate_limit(request)
    try:
        res = await ai_service.audit_contract(req.document_type, req.data)
        return AuditContractResponse(**res)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/audit-upload")
async def audit_uploaded_document(req: AuditUploadRequest, request: Request):
    await check_rate_limit(request)
    try:
        res = await ai_service.audit_uploaded_document(req.raw_text, req.filename)
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Legal Assistant Chatbot
@app.post("/api/ai/legal-chat")
async def legal_assistant_chat(req: LegalChatRequest, request: Request):
    await check_rate_limit(request)
    try:
        answer = await ai_service.ask_legal_assistant(req.question, req.contract_context)
        return {"answer": answer}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Bangladesh Stamp Duty Calculator
@app.post("/api/tools/stamp-calculator")
async def calculate_stamp(req: StampCalculateRequest):
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

# Extract Text from Uploaded Documents (PDF, DOCX, TXT)
@app.post("/api/tools/extract-file-text")
async def extract_file_text_endpoint(file: UploadFile = File(...)):
    try:
        content_bytes = await file.read()
        if not content_bytes:
            raise HTTPException(status_code=400, detail="ফাইলটিতে কোনো তথ্য পাওয়া যায়নি।")
        if len(content_bytes) > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="ফাইলের সাইজ ১৫ মেগাবাইটের বেশি হতে পারবে না।")

        filename = file.filename or "uploaded_document.txt"
        extracted_text, detected_format = extract_text_from_bytes(content_bytes, filename)

        if not extracted_text or not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="ফাইলটি থেকে কোনো টেক্সট পড়া যায়নি। ফাইলটি স্ক্যান করা ইমেজ বা পাসওয়ার্ড প্রটেক্টেড কিনা যাচাই করুন।"
            )

        return {
            "success": True,
            "filename": filename,
            "detected_format": detected_format,
            "extracted_text": extracted_text.strip(),
            "character_count": len(extracted_text.strip()),
            "word_count": len(extracted_text.strip().split())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ফাইল প্রক্রিয়াকরণে ত্রুটি: {str(e)}")

# Legal Notice Generator
@app.post("/api/tools/generate-notice", response_model=GenerateNoticeResponse)
async def generate_legal_notice(req: GenerateNoticeRequest):
    try:
        res = notice_generator.generate_notice(
            notice_type=req.notice_type,
            contract_data=req.contract_data,
            custom_reason=req.custom_reason or ""
        )
        return GenerateNoticeResponse(**res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notice generation error: {str(e)}")

# Cryptographic SHA-256 Fingerprint Generator
@app.post("/api/tools/generate-hash")
async def generate_contract_hash(req: GenerateHashRequest):
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

# Cryptographic Hash Verification
@app.post("/api/tools/verify-hash")
async def verify_contract_hash(req: VerifyHashRequest):
    try:
        return security_service.verify_integrity(req.content, req.expected_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")

# Watermark Application
@app.post("/api/tools/apply-watermark")
async def apply_watermark_route(req: ApplyWatermarkRequest):
    try:
        watermarked = security_service.apply_watermark(
            html=req.html_content,
            watermark_type=req.watermark_type or "draft"
        )
        return {"rendered_html": watermarked}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Watermark error: {str(e)}")

def get_session_id(request: Request) -> str:
    session_id = request.headers.get("X-Session-ID") or request.query_params.get("session_id")
    if not session_id or not session_id.strip():
        return "default_user"
    return session_id.strip()

# Database Contract Management (Async & Multi-User Isolated)
@app.get("/api/contracts")
async def get_all_contracts(request: Request):
    session_id = get_session_id(request)
    return await list_contracts(owner_id=session_id)

@app.post("/api/contracts")
async def save_new_contract(req: SaveContractRequest, request: Request):
    session_id = req.owner_id or get_session_id(request)
    try:
        cid = await save_contract(req.title, req.document_type, req.language, req.data, req.id, owner_id=session_id)
        return {"status": "saved", "id": cid, "owner_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contracts/{contract_id}")
async def fetch_single_contract(contract_id: str, request: Request):
    session_id = get_session_id(request)
    item = await get_contract(contract_id, owner_id=session_id)
    if not item:
        raise HTTPException(status_code=404, detail="Contract not found or unauthorized")
    return item

@app.delete("/api/contracts/{contract_id}")
async def remove_single_contract(contract_id: str, request: Request):
    session_id = get_session_id(request)
    success = await delete_contract(contract_id, owner_id=session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found or unauthorized")
    return {"status": "deleted", "id": contract_id}

# Remote Share & Signing
@app.get("/api/contracts/share/{contract_id}")
async def get_shared_contract(contract_id: str):
    item = await get_contract(contract_id)
    if not item:
        raise HTTPException(status_code=404, detail="Contract not found")
    html = template_engine.render_html(item["document_type"], item["data"], item["language"])
    return {
        "id": item["id"],
        "title": item["title"],
        "document_type": item["document_type"],
        "language": item.get("language", "bn"),
        "rendered_html": html,
        "data": item["data"]
    }

@app.post("/api/contracts/share/{contract_id}/sign")
async def submit_remote_signature(contract_id: str, req: RemoteSignRequest):
    success = await update_remote_signature(contract_id, req.signature_data, req.target or "party2")
    if not success:
        raise HTTPException(status_code=404, detail="Contract not found")
    return {"status": "signature_saved", "id": contract_id}

@app.post("/api/export/pdf")
async def export_pdf(req: GenerateDocumentRequest):
    try:
        html = template_engine.render_html(req.document_type, req.data, req.language)
        pdf_bytes = await pdf_service.convert_html_to_pdf_async(html)
        filename = f"{req.document_type}_{req.language}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.post("/api/export/docx")
async def export_docx(req: GenerateDocumentRequest):
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
async def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Frontend not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
