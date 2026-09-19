from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class RefineClauseRequest(BaseModel):
    raw_text: str = Field(..., description="User informal description of clause")
    document_type: str = Field("tenancy_agreement", description="Type of contract")
    language: str = Field("bn", description="Output language: bn or en")

class RefineClauseResponse(BaseModel):
    refined_clause: str
    title: str
    risk_level: str
    explanation: str

class ExplainClauseRequest(BaseModel):
    clause_text: str = Field(..., description="Legal clause to explain")
    language: str = Field("bn", description="Language for explanation")

class ExplainClauseResponse(BaseModel):
    simple_explanation: str
    key_obligations: List[str]
    potential_risks: List[str]

class AuditContractRequest(BaseModel):
    document_type: str
    data: Dict[str, Any]

class AuditIssue(BaseModel):
    severity: str
    title: str
    description: str
    suggestion: str

class AuditContractResponse(BaseModel):
    score: int
    summary: str
    issues: List[AuditIssue]

class GenerateDocumentRequest(BaseModel):
    document_type: str
    language: str = "bn"
    data: Dict[str, Any]

class GenerateDocumentResponse(BaseModel):
    title: str
    rendered_html: str
    raw_data: Dict[str, Any]

class SaveContractRequest(BaseModel):
    id: Optional[str] = None
    owner_id: Optional[str] = None
    title: str
    document_type: str
    language: str = "bn"
    data: Dict[str, Any]

class AuditUploadRequest(BaseModel):
    raw_text: str
    filename: Optional[str] = "document.pdf"

class LegalChatRequest(BaseModel):
    question: str
    contract_context: Optional[str] = ""

class StampCalculateRequest(BaseModel):
    doc_type: str
    rent_amount: Optional[float] = 0
    duration_months: Optional[int] = 12
    deposit_amount: Optional[float] = 0
    total_capital: Optional[float] = 0

class RemoteSignRequest(BaseModel):
    signature_data: str
    target: Optional[str] = "party2"

class GenerateNoticeRequest(BaseModel):
    notice_type: str = Field(..., description="vacate_notice | renewal_notice | demand_notice")
    contract_data: Dict[str, Any] = Field(default_factory=dict)
    custom_reason: Optional[str] = ""

class GenerateNoticeResponse(BaseModel):
    notice_type: str
    title: str
    subject: str
    body: str
    date: str

class GenerateHashRequest(BaseModel):
    content: str = ""
    doc_type: Optional[str] = ""
    data: Optional[Dict[str, Any]] = None

class VerifyHashRequest(BaseModel):
    content: str
    expected_hash: str

class ApplyWatermarkRequest(BaseModel):
    html_content: str
    watermark_type: Optional[str] = "draft"
