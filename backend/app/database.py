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
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_contract(title: str, doc_type: str, language: str, data: dict, contract_id: str = None) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    
    if not contract_id:
        contract_id = str(uuid.uuid4())[:8]
        cursor.execute("""
            INSERT INTO contracts (id, title, document_type, language, data_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (contract_id, title, doc_type, language, json.dumps(data, ensure_ascii=False), now, now))
    else:
        cursor.execute("""
            UPDATE contracts
            SET title = ?, document_type = ?, language = ?, data_json = ?, updated_at = ?
            WHERE id = ?
        """, (title, doc_type, language, json.dumps(data, ensure_ascii=False), now, contract_id))
        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO contracts (id, title, document_type, language, data_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (contract_id, title, doc_type, language, json.dumps(data, ensure_ascii=False), now, now))
    
    conn.commit()
    conn.close()
    return contract_id

def list_contracts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, document_type, language, created_at, updated_at FROM contracts ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

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

def update_remote_signature(contract_id: str, signature_data: str, target: str = "party2") -> bool:
    item = get_contract(contract_id)
    if not item:
        return False
    data = item["data"]
    if target == "party1":
        data["party1_signature"] = signature_data
    else:
        data["party2_signature"] = signature_data

    save_contract(item["title"], item["document_type"], item["language"], data, contract_id)
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
