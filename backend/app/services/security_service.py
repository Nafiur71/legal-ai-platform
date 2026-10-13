import hashlib
import json
import re
import io
import base64
from datetime import datetime
from typing import Dict, Any, Optional
import qrcode

class SecurityService:
    @staticmethod
    def generate_qr_code_base64(data: str) -> str:
        """Generates a base64 PNG data-uri for a QR code."""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=4,
                border=1,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#0f172a", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/png;base64,{b64}"
        except Exception:
            return ""

    @staticmethod
    def normalize_content(content: str) -> str:
        """Removes volatile whitespace and HTML tags to extract raw canonical text for hashing."""
        # Strip HTML tags
        text = re.sub(r'<[^>]+>', ' ', content)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @classmethod
    def compute_sha256(cls, content: str) -> str:
        """Computes deterministic SHA-256 hash for document content."""
        canonical_text = cls.normalize_content(content)
        return hashlib.sha256(canonical_text.encode('utf-8')).hexdigest()

    @classmethod
    def generate_fingerprint(cls, doc_type: str, data: Dict[str, Any], raw_html: Optional[str] = "") -> Dict[str, Any]:
        """Generates a cryptographic fingerprint badge and reference ID for a contract."""
        source_text = raw_html if raw_html else json.dumps(data, sort_keys=True, ensure_ascii=False)
        sha_hash = cls.compute_sha256(source_text)
        short_hash = sha_hash[:12].upper()
        ref_id = f"SLA-SEC-{short_hash}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "ref_id": ref_id,
            "sha256": sha_hash,
            "short_hash": short_hash,
            "timestamp": timestamp,
            "status": "SECURED_SHA256"
        }

    @classmethod
    def verify_integrity(cls, content: str, expected_hash: str) -> Dict[str, Any]:
        """Verifies whether document content matches the provided SHA-256 fingerprint."""
        computed = cls.compute_sha256(content)
        expected_clean = expected_hash.strip().lower()
        if expected_clean.startswith("sla-sec-"):
            expected_clean = expected_clean.replace("sla-sec-", "")

        # Require at least 12 characters (short hash length) to prevent empty or trivial prefix bypass
        if len(expected_clean) < 12:
            is_match = False
        else:
            is_match = (computed.lower() == expected_clean) or (computed[:len(expected_clean)].lower() == expected_clean)

        return {
            "is_valid": is_match,
            "computed_hash": computed,
            "expected_hash": expected_hash,
            "tampered": not is_match,
            "message": "দলিলটি সম্পূর্ণ অবিকৃত রয়েছে (Document is authentic and un-tampered)" if is_match else "সতর্কতা: দলিলটিতে অননুমোদিত পরিবর্তন শনাক্ত হয়েছে! (Warning: Content tampered or modified!)"
        }

    @staticmethod
    def apply_watermark(html: str, watermark_type: str = "draft") -> str:
        """Injects watermark styles and markup into rendered contract HTML."""
        labels = {
            "draft": "খসড়া • DRAFT COPY",
            "confidential": "গোপনীয় • CONFIDENTIAL",
            "sample": "নমুনা • SAMPLE ONLY"
        }
        text = labels.get(watermark_type.lower(), "খসড়া • DRAFT COPY")

        watermark_css = f"""
<style id="sla-watermark-styles">
  .sla-watermark-overlay {{
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-35deg);
    font-size: 54pt;
    font-weight: 900;
    color: rgba(220, 38, 38, 0.12);
    text-transform: uppercase;
    letter-spacing: 6px;
    pointer-events: none;
    z-index: 9999;
    white-space: nowrap;
    user-select: none;
    text-align: center;
    border: 8px dashed rgba(220, 38, 38, 0.15);
    padding: 18px 40px;
    border-radius: 12px;
  }}
  @media print {{
    .sla-watermark-overlay {{
      display: block !important;
      color: rgba(180, 20, 20, 0.15) !important;
      border-color: rgba(180, 20, 20, 0.15) !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
  }}
</style>
<div class="sla-watermark-overlay" id="sla-watermark-banner">{text}</div>
"""
        if "</body>" in html:
            return html.replace("</body>", f"{watermark_css}</body>")
        return html + watermark_css

security_service = SecurityService()
