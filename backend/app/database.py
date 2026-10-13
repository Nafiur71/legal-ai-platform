import os
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "legal_contracts.db"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

env_db = os.getenv("DB_PATH")
if env_db:
    DB_PATH = Path(env_db)
elif (DATA_DIR / "legal_contracts.db").exists():
    DB_PATH = DATA_DIR / "legal_contracts.db"
elif DEFAULT_DB.exists():
    DB_PATH = DEFAULT_DB
else:
    DB_PATH = DATA_DIR / "legal_contracts.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH), timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            document_type TEXT NOT NULL,
            language TEXT DEFAULT 'bn',
            data_json TEXT NOT NULL,
            status TEXT DEFAULT 'draft',
            party1_name TEXT DEFAULT '',
            party2_name TEXT DEFAULT '',
            party1_signed_at TEXT DEFAULT '',
            party2_signed_at TEXT DEFAULT '',
            party1_ip TEXT DEFAULT '',
            party2_ip TEXT DEFAULT '',
            sha256_hash TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    # Ensure newly added columns exist in existing databases
    new_cols = [
        ("status", "TEXT DEFAULT 'draft'"),
        ("party1_name", "TEXT DEFAULT ''"),
        ("party2_name", "TEXT DEFAULT ''"),
        ("party1_signed_at", "TEXT DEFAULT ''"),
        ("party2_signed_at", "TEXT DEFAULT ''"),
        ("party1_ip", "TEXT DEFAULT ''"),
        ("party2_ip", "TEXT DEFAULT ''"),
        ("sha256_hash", "TEXT DEFAULT ''")
    ]
    for col_name, col_def in new_cols:
        try:
            cursor.execute(f"ALTER TABLE contracts ADD COLUMN {col_name} {col_def}")
        except Exception:
            pass  # column already exists
    conn.commit()
    conn.close()

def extract_party_names(doc_type: str, data: dict):
    p1 = (
        data.get("landlord_name") or
        data.get("disclosing_party_name") or
        data.get("client_name") or
        data.get("partner1_name") or
        data.get("company_name") or
        data.get("party1_name") or ""
    )
    p2 = (
        data.get("tenant_name") or
        data.get("receiving_party_name") or
        data.get("freelancer_name") or
        data.get("partner2_name") or
        data.get("employee_name") or
        data.get("party2_name") or ""
    )
    return str(p1), str(p2)

def save_contract(title: str, doc_type: str, language: str, data: dict, contract_id: str = None, client_ip: str = "127.0.0.1") -> str:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    p1_name, p2_name = extract_party_names(doc_type, data)
    
    # Check signatures & status
    has_p1 = bool(data.get("party1_signature"))
    has_p2 = bool(data.get("party2_signature"))
    if has_p1 and has_p2:
        status = "completed"
    elif has_p1:
        status = "pending_party2"
    else:
        status = "draft"

    p1_signed_at = now if has_p1 and not data.get("party1_signed_at") else data.get("party1_signed_at", "")
    p2_signed_at = now if has_p2 and not data.get("party2_signed_at") else data.get("party2_signed_at", "")
    data["status"] = status
    if has_p1:
        data["party1_signed_at"] = p1_signed_at
    if has_p2:
        data["party2_signed_at"] = p2_signed_at

    import hashlib
    content_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    sha_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()
    data["sha256_hash"] = sha_hash

    if not contract_id:
        contract_id = str(uuid.uuid4())[:8]
        data["ref_id"] = f"SLA-BD-{contract_id.upper()}"
        cursor.execute("""
            INSERT INTO contracts (
                id, title, document_type, language, data_json, status,
                party1_name, party2_name, party1_signed_at, party2_signed_at,
                party1_ip, party2_ip, sha256_hash, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            contract_id, title, doc_type, language, json.dumps(data, ensure_ascii=False),
            status, p1_name, p2_name, p1_signed_at, p2_signed_at,
            client_ip if has_p1 else "", client_ip if has_p2 else "", sha_hash, now, now
        ))
    else:
        data.setdefault("ref_id", f"SLA-BD-{contract_id.upper()}")
        cursor.execute("""
            UPDATE contracts
            SET title = ?, document_type = ?, language = ?, data_json = ?, status = ?,
                party1_name = ?, party2_name = ?, party1_signed_at = ?, party2_signed_at = ?,
                sha256_hash = ?, updated_at = ?
            WHERE id = ?
        """, (
            title, doc_type, language, json.dumps(data, ensure_ascii=False), status,
            p1_name, p2_name, p1_signed_at, p2_signed_at,
            sha_hash, now, contract_id
        ))
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO contracts (
                    id, title, document_type, language, data_json, status,
                    party1_name, party2_name, party1_signed_at, party2_signed_at,
                    party1_ip, party2_ip, sha256_hash, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contract_id, title, doc_type, language, json.dumps(data, ensure_ascii=False),
                status, p1_name, p2_name, p1_signed_at, p2_signed_at,
                client_ip if has_p1 else "", client_ip if has_p2 else "", sha_hash, now, now
            ))
    
    conn.commit()
    conn.close()
    return contract_id

def list_contracts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, document_type, language, status,
               party1_name, party2_name, party1_signed_at, party2_signed_at,
               created_at, updated_at, data_json
        FROM contracts
        ORDER BY updated_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        item = dict(r)
        try:
            item["data"] = json.loads(item.get("data_json", "{}"))
        except Exception:
            item["data"] = {}
        result.append(item)
    return result

def get_contract(contract_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        res = dict(row)
        res["data"] = json.loads(res["data_json"])
        return res
    return None

def update_remote_signature(contract_id: str, signature_data: str, target: str = "party2", client_ip: str = "127.0.0.1") -> bool:
    item = get_contract(contract_id)
    if not item:
        return False
    data = item["data"]
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    if target == "party1":
        data["party1_signature"] = signature_data
        data["party1_signed_at"] = now
        data["party1_ip"] = client_ip
    else:
        data["party2_signature"] = signature_data
        data["party2_signed_at"] = now
        data["party2_ip"] = client_ip

    save_contract(item["title"], item["document_type"], item["language"], data, contract_id, client_ip)
    return True

def delete_contract(contract_id: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

init_db()
