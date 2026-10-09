# Smart AI Legal Automation & Document Generator Platform
## Comprehensive Architecture, Feature Specification & Phase 1 to 5 Documentation

**Project Version:** 3.0.0 (Production Release)  
**Target Jurisdiction:** Bangladesh (Statutory Compliance with The Stamp Act 1899, The Contract Act 1872, and ICT Act 2006)  
**Document Classification:** Engineering Design & Phase Implementation Report  
**Author:** AI Engineering & Pair Programming Team  

---

## 1. Executive Summary

The **Smart AI Legal Automation & Document Generator Platform** is a full-stack, enterprise-grade legal engineering solution designed to eliminate manual typing, legal ambiguity, and fraud in agreement preparation.

Common individuals, businesses, landlords, startups, and legal practitioners can answer dynamic questionnaire forms or speak informally. The platform's backend engine, powered by **Google Gemini AI**, **Jinja2 Template Engines**, and **Headless Chromium Print Automation**, transforms input into court-admissible, pixel-perfect legal contracts and formal notices formatted on **BDT 300 Non-Judicial Stamp Paper simulation** and downloadable as verified A4 PDFs or editable Word (.docx) documents.

---

## 2. Complete Technology Stack & Architecture

| Layer / Domain | Technologies & Libraries | Purpose & Implementation Details |
|---|---|---|
| **Backend Framework** | `Python 3.11`, `FastAPI 0.115+`, `Uvicorn 0.30+` | Asynchronous RESTful API layer, high concurrency, automatic OpenAPI Swagger docs. |
| **Data Validation & Schemas** | `Pydantic v2.8+` | Strict schema validation, request/response models for all contract fields. |
| **Template Engine** | `Jinja2 3.1.4` | Server-side contract generation with inheritance (`base_document.html`). |
| **Artificial Intelligence** | `Google Gemini API` (`gemini-1.5-flash`), `REST / HTTPX` | Clause refinement, risk auditing, clause plain-language explainer, and legal chatbot. |
| **Document Exporting** | `Headless Chromium / Edge`, `python-docx 1.1.2` | Pixel-perfect print-ready A4 PDF generation via CDP flags, editable Microsoft Word exports. |
| **Database & Persistence** | `SQLite3` (Embedded), `Python sqlite3 driver` | Zero-dependency local persistence for drafts, contracts, signatures, and timestamps. |
| **Cryptographic Security** | `hashlib` (SHA-256), canonical text normalizer | Tamper-proof digital fingerprinting ensuring contract integrity post-signature. |
| **Frontend Architecture** | `Vanilla JavaScript (ES6+)`, `HTML5`, `CSS3` | Ultra-fast SPA without bulky framework overhead, reactive UI state management. |
| **Digital E-Signature** | `HTML5 Canvas API`, touch & mouse event stream | On-screen signature drawing, base64 PNG serialization, remote signing capability. |
| **Typography & UI Styling** | `Hind Siliguri` (Bengali Google Font), `Inter`, `FontAwesome 6.4` | Professional legal paper styling, clean corporate split-view workspace. |
| **Containerization & Cloud** | `Docker`, `Docker Compose`, `Debian Slim` | Multi-stage production container with bundled fonts and Chromium dependencies. |

---

## 3. Phase-by-Phase Detailed Implementation & Feature Matrix

```
  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │  Phase 1 (MVP)  │ ──> │ Phase 2 (Corp)  │ ──> │ Phase 3 (E-Sign)│
  └─────────────────┘     └─────────────────┘     └─────────────────┘
                                                           │
  ┌─────────────────┐     ┌─────────────────┐              ▼
  │  Phase 5 (Prod) │ <── │ Phase 4 (AI/Fee)│ <────────────┘
  └─────────────────┘     └─────────────────┘
```

---

### 3.1 Phase 1: Core MVP & Smart Legal Drafting Engine

#### Primary Objective
Establish the foundational legal automation engine capable of taking structured inputs, generating legal agreements, leveraging AI for legal polishing, and producing A4 PDFs.

#### Features Delivered
1. **Dynamic Wizard Form:** Step-by-step navigation (Parties, Terms & Financials, Custom Clauses, Signatures).
2. **Three Standard Legal Templates:**
   - **Tenancy Agreement (বাড়ি/দোকান ভাড়ার চুক্তিপত্র):** Advance deposit, monthly rent, utility bills, tenancy period, notice terms.
   - **Non-Disclosure Agreement (NDA / গোপনীয়তা চুক্তি):** Disclosing/Receiving parties, confidential information definition, exclusions, injunction remedies.
   - **Freelance & Service Agreement (ফ্রিল্যান্স চুক্তিপত্র):** Scope of work, milestone deliverables, IP rights assignment, payment schedules.
3. **AI Clause Refiner:** Converts informal notes into binding legal clauses with risk ratings.
4. **AI Clause Explainer:** Translates archaic legal terminology into plain, easy-to-understand language.
5. **AI Contract Risk Auditor:** Scans contracts for missing safeguards and awards an audit safety score (0-100).
6. **Headless Chrome PDF Exporter:** Generates true vector A4 PDFs matching exact legal paper margins.
7. **DOCX Word Exporter:** Generates formatted Microsoft Word files for offline word-processor editing.

#### Technologies Used
- `FastAPI`, `Jinja2`, `python-docx`, `Google Gemini API`, Headless Chrome CLI, `HTML5/CSS3`.

---

### 3.2 Phase 2: Corporate Templates, Direct Paper Editing & Statutory Stamps

#### Primary Objective
Expand to corporate contracts, enable direct WYSIWYG paper editing, and simulate statutory Non-Judicial Stamp requirements under Bangladesh law.

#### Features Delivered
1. **Two Corporate Templates Added:**
   - **Partnership Deed (অংশীদারি কারবার চুক্তিপত্র):** Capital contributions, profit/loss ratio, bank account operations, dispute arbitration, dissolution terms.
   - **Employment Contract (চাকরির চুক্তিপত্র):** Designation, gross salary breakdown, probation period, leaves, intellectual property, termination rules.
2. **Direct Paper Inline Editing:** Toggleable `contenteditable` mode on the live legal preview paper allowing users to click and edit any word directly on the rendered stamp.
3. **BDT 300 Non-Judicial Stamp Paper Simulation:**
   - Header replicating the official Government of Bangladesh Non-Judicial Stamp.
   - Toggle switch to show or hide the stamp space depending on whether legal paper is pre-purchased or printed blank.
4. **LocalStorage Auto-Draft Persistence:** Browser localStorage saves active form state, preventing accidental data loss on refresh.
5. **Inline AI Explain Buttons:** Every clause on the preview paper has an interactive bulb icon that pops up plain-language obligations and potential risks.

#### Technologies Used
- `HTML5 contenteditable API`, `localStorage API`, CSS print media queries (`@page`, `@media print`).

---

### 3.3 Phase 3: Digital E-Signatures, Contract Database & External File Auditor

#### Primary Objective
Transform the platform into a legally enforceable workflow tool with digital signatures, database contract management, and an auditor for third-party contracts.

#### Features Delivered
1. **Interactive E-Signature Canvas:**
   - Smooth mouse and mobile touch drawing.
   - Separate signature slots for Party 1 (e.g., Landlord/Employer) and Party 2 (e.g., Tenant/Employee).
   - High-resolution base64 PNG embedding into the Jinja2 contract templates.
2. **SQLite Database Contract Repository:**
   - Complete CRUD (Create, Read, Update, Delete) engine for contracts (`legal_contracts.db`).
   - Contract History Modal: view saved contracts, reload into editor, delete old agreements.
3. **External File Upload & AI Legal Auditor:**
   - Supports uploading `.pdf`, `.docx`, or `.txt` contracts or pasting raw contract text.
   - AI evaluates 4 critical parameters: Fairness, Ambiguity, Liability Exposure, and Statutory Compliance.
   - Provides severity-tagged issues (High/Medium/Low) and actionable replacement suggestions.

#### Technologies Used
- `HTML5 Canvas 2D Context`, `SQLite3`, `Pydantic v2`, Base64 image rendering, file-upload parsing.

---

### 3.4 Phase 4: Floating Legal AI Chatbot, Stamp Calculator & Remote Signing

#### Primary Objective
Provide instant legal counsel, statutory fee transparency under The Stamp Act 1899, and remote signature workflows for non-colocated parties.

#### Features Delivered
1. **Floating AI Legal Assistant ("আইনAI সহকারী"):**
   - Floating action button (FAB) opening a reactive legal chatbot.
   - Answers legal queries (e.g., stamp duty rules, eviction procedures, arbitration requirements).
   - Awareness of the user's active contract context.
2. **Bangladesh Stamp Duty Calculator (The Stamp Act, 1899):**
   - Implements Schedule 1 rules for Tenancy (<1 yr: 300 Tk, 1-5 yrs: 2%, >5 yrs: 3%), Partnership (capital-based brackets 500–2,000 Tk), and Trust/Affidavits.
   - Advises exact stamp denominations, penalties for under-stamping, and legal remedies.
3. **Shareable Remote Signing Link:**
   - Generates unique link: `/api/contracts/share/{id}`.
   - Second party opens link on their device, reviews rendered contract, and draws their signature.
   - Signature instantly updates the central database and updates the contract.
4. **Digital Verification Footer & QR Seal:**
   - Reference code generation (`SLA-BD-XXXXX`).
   - Official digital certification badge embedded in PDF footer.

#### Technologies Used
- Full-duplex REST client, `StampAct1899` calculator rules engine, CSS animations, Responsive FAB widget.

---

### 3.5 Phase 5: Legal Notice Engine, Tamper-Proof Security & Docker Production

#### Primary Objective
Provide post-contract dispute handling and notices, cryptographic proof of authenticity, dynamic watermarking, and one-click cloud containerization.

#### Features Delivered
1. **Automated Legal Notice Engine:**
   - **Vacate Notice (বাসা/দোকান ছাড়ার আইনি নোটিশ):** Formal notice citing the Premises Rent Control Act and contract duration.
   - **Contract Renewal Letter (চুক্তি নবায়ন পত্র):** Proposes new rental terms and extension periods.
   - **Demand Notice for Dues (বকেয়া ভাড়ার তাগিদপত্র):** Legal demand specifying default amount and 7-day cure period prior to eviction suit.
   - UI features: 1-click clipboard copy, and direct injection into preview paper.
2. **Tamper-Proof SHA-256 Cryptographic Hash Engine:**
   - Calculates deterministic SHA-256 fingerprint for contract text and terms.
   - **Verification Modal:** Paste any contract text or hash code.
   - Instant visual indicator: **Green (100% Authentic & Un-tampered)** or **Red (Tampered / Content Altered)**.
3. **Dynamic Watermark System:**
   - Toggleable **"খসড়া • DRAFT COPY"** and **"গোপনীয় • CONFIDENTIAL"** diagonal watermark banners.
   - Seamlessly preserved across on-screen preview and `@media print` PDF downloads.
4. **Docker Production Deployment Package:**
   - `Dockerfile`: Debian-slim container with Chromium headless & font libraries.
   - `docker-compose.yml`: Port mapping, volume mounting for database persistence, automated healthchecks.
   - `.dockerignore`: Lean image build optimization.

#### Technologies Used
- `hashlib` SHA-256, Unicode normalizer, Docker multi-stage builds, Docker Compose, Chromium headless container runtime.

---

## 4. Phase Documentation Plan & Directory Structure

To ensure enterprise maintainability and seamless handover, each development phase is documented in its own dedicated directory under `docs/phases/`:

```
legal-ai-platform/
├── docs/
│   └── phases/
│       ├── phase-1-mvp/
│       │   └── README.md              <-- Architecture of MVP, templates & PDF engine
│       ├── phase-2-templates-editing/
│       │   └── README.md              <-- Partnership, Employment, inline edit & 300 Tk stamp
│       ├── phase-3-esign-database/
│       │   └── README.md              <-- Signature canvas, SQLite CRUD & external audit
│       ├── phase-4-chatbot-calculator/
│       │   └── README.md              <-- Legal chatbot, Stamp Act calc & remote sign
│       └── phase-5-bilingual-production/
│           └── README.md              <-- Notice engine, SHA-256 cryptography & Docker
```

---

## 5. Complete API Route Specification

| HTTP Method | API Path | Phase | Request Payload / Params | Response Summary |
|---|---|---|---|---|
| `GET` | `/api/health` | 1 | None | `{"status": "ok", "version": "3.0.0"}` |
| `GET` | `/api/templates` | 1 | None | Array of template metadata and default fields |
| `POST` | `/api/generate` | 1 | `GenerateDocumentRequest` | Rendered HTML and raw data |
| `POST` | `/api/ai/refine-clause` | 1 | `RefineClauseRequest` | Polished legal clause, title, risk rating |
| `POST` | `/api/ai/explain-clause` | 1 | `ExplainClauseRequest` | Plain language summary, obligations, risks |
| `POST` | `/api/ai/audit` | 1 | `AuditContractRequest` | 0-100 safety score, structured vulnerability list |
| `POST` | `/api/export/pdf` | 1 | `GenerateDocumentRequest` | Binary A4 PDF attachment stream |
| `POST` | `/api/export/docx` | 1 | `GenerateDocumentRequest` | Binary Microsoft Word (.docx) stream |
| `GET` | `/api/contracts` | 3 | None | Array of saved contracts in SQLite database |
| `POST` | `/api/contracts` | 3 | `SaveContractRequest` | `{"status": "saved", "id": "..."}` |
| `GET` | `/api/contracts/{id}` | 3 | Path `id` | Single contract JSON object |
| `DELETE` | `/api/contracts/{id}` | 3 | Path `id` | `{"status": "deleted", "id": "..."}` |
| `POST` | `/api/ai/audit-upload` | 3 | `AuditUploadRequest` | Audit report for external document |
| `POST` | `/api/ai/legal-chat` | 4 | `LegalChatRequest` | AI legal advisory answer |
| `POST` | `/api/tools/stamp-calculator`| 4 | `StampCalculateRequest` | Exact stamp duty value & statutory guidelines |
| `GET` | `/api/contracts/share/{id}` | 4 | Path `id` | Shared contract view & sign data |
| `POST` | `/api/contracts/share/{id}/sign`| 4 | `RemoteSignRequest` | Remote signature save confirmation |
| `POST` | `/api/tools/generate-notice` | 5 | `GenerateNoticeRequest` | Formal vacate/renewal/demand notice object |
| `POST` | `/api/tools/generate-hash` | 5 | `GenerateHashRequest` | Deterministic SHA-256 hash & badge ID |
| `POST` | `/api/tools/verify-hash` | 5 | `VerifyHashRequest` | Integrity verification status & match result |
| `POST` | `/api/tools/apply-watermark` | 5 | `ApplyWatermarkRequest` | HTML with injected watermark banner & CSS |

---

## 6. Testing & Quality Verification Summary

All phases have regression test suites located under `backend/tests/`:
- `tests/test_api.py` (Phase 1 & Phase 2 core suite - 9 tests)
- `tests/test_phase3.py` (Phase 3 database & signature suite - 3 tests)
- `tests/test_phase4.py` (Phase 4 chatbot, calculator & remote sign - 3 tests)
- `tests/test_phase5.py` (Phase 5 notice engine, SHA-256 & watermark - 4 tests)

**Execution Status:**  
Total Test Cases: **19/19 (100% Passed)**  
Zero Regressions across all legacy and new modules.

---

## 7. Deployment Instructions

### Method 1: Docker (Cloud / VPS Production)
```bash
# Clone or navigate to the project directory
cd legal-ai-platform

# Build and start services in detached mode
docker compose up --build -d

# Check running status and health probe
docker compose ps

# Access in browser
# http://<YOUR_SERVER_IP>:8000
```

### Method 2: Local Python Execution
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Access the application at: `http://127.0.0.1:8000`

---

## 8. Strategic Roadmap (Phase 6 & Beyond)

1. **User Authentication & Role-Based Access Control (RBAC):**
   - JWT tokens for Client, Advocate/Panel Lawyer, and Organization Admin.
2. **Panel Lawyer Review & Seal Endorsement:**
   - Clients can request formal review by a verified Bangladesh Bar Council lawyer.
   - Lawyer portal to affix digital bar seal and professional approval stamp.
3. **Automated Payment Gateway Integration:**
   - bKash, Nagad, and SSLCommerz payment APIs for pay-per-contract download and monthly subscriptions.
4. **Bangla Speech-to-Text (Voice AI):**
   - Microphone voice dictation directly populating contract clauses and legal queries.
