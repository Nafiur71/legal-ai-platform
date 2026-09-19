import os
import json
import uuid
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

DB_DIR = os.getenv("DB_DIR", "").strip()
if DB_DIR:
    dir_path = Path(DB_DIR)
    dir_path.mkdir(parents=True, exist_ok=True)
    DB_PATH = dir_path / "legal_contracts.db"
else:
    DB_PATH = Path(__file__).resolve().parent.parent / "legal_contracts.db"
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Check if PostgreSQL is configured via DATABASE_URL
IS_POSTGRES = DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgresql+asyncpg://")

_pg_pool = None

async def get_pg_pool():
    global _pg_pool
    if _pg_pool is None and IS_POSTGRES:
        import asyncpg
        # Convert SQLAlchemy URL to standard asyncpg URL if necessary
        clean_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        _pg_pool = await asyncpg.create_pool(
            clean_url,
            min_size=2,
            max_size=20,
            command_timeout=60
        )
    return _pg_pool

def get_sqlite_conn():
    conn = sqlite3.connect(str(DB_PATH), timeout=10.0)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode and busy timeout for high concurrency
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

async def init_db():
    """Initializes tables for either PostgreSQL or SQLite with owner_id support."""
    if IS_POSTGRES:
        try:
            pool = await get_pg_pool()
            async with pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS contracts (
                        id VARCHAR(64) PRIMARY KEY,
                        owner_id VARCHAR(64) DEFAULT 'default_user',
                        title TEXT NOT NULL,
                        document_type VARCHAR(64) NOT NULL,
                        language VARCHAR(16) DEFAULT 'bn',
                        data_json TEXT NOT NULL,
                        created_at VARCHAR(64) NOT NULL,
                        updated_at VARCHAR(64) NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_contracts_owner ON contracts (owner_id, updated_at DESC);
                """)
                try:
                    await conn.execute("ALTER TABLE contracts ADD COLUMN IF NOT EXISTS owner_id VARCHAR(64) DEFAULT 'default_user';")
                except Exception:
                    pass
            logger.info("PostgreSQL database initialized successfully.")
            return
        except Exception as e:
            logger.error(f"PostgreSQL connection failed, falling back to SQLite: {e}")

    # SQLite initialization
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id TEXT PRIMARY KEY,
            owner_id TEXT DEFAULT 'default_user',
            title TEXT NOT NULL,
            document_type TEXT NOT NULL,
            language TEXT DEFAULT 'bn',
            data_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    try:
        cursor.execute("ALTER TABLE contracts ADD COLUMN owner_id TEXT DEFAULT 'default_user';")
    except Exception:
        pass
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contracts_owner ON contracts (owner_id, updated_at DESC);")
    conn.commit()
    conn.close()
    logger.info("SQLite database initialized in WAL mode with owner_id support.")

# Synchronous initialization on module import for local safety
try:
    conn = get_sqlite_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id TEXT PRIMARY KEY,
            owner_id TEXT DEFAULT 'default_user',
            title TEXT NOT NULL,
            document_type TEXT NOT NULL,
            language TEXT DEFAULT 'bn',
            data_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    try:
        conn.execute("ALTER TABLE contracts ADD COLUMN owner_id TEXT DEFAULT 'default_user';")
    except Exception:
        pass
    conn.execute("CREATE INDEX IF NOT EXISTS idx_contracts_owner ON contracts (owner_id, updated_at DESC);")
    conn.commit()
    conn.close()
except Exception as e:
    logger.warning(f"Sync SQLite init error: {e}")

async def save_contract(title: str, doc_type: str, language: str, data: dict, contract_id: str = None, owner_id: str = "default_user") -> str:
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    data_str = json.dumps(data, ensure_ascii=False)
    owner_id = owner_id or "default_user"

    if IS_POSTGRES:
        try:
            pool = await get_pg_pool()
            async with pool.acquire() as conn:
                if not contract_id:
                    contract_id = str(uuid.uuid4())[:8]
                    await conn.execute("""
                        INSERT INTO contracts (id, owner_id, title, document_type, language, data_json, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """, contract_id, owner_id, title, doc_type, language, data_str, now, now)
                else:
                    await conn.execute("""
                        UPDATE contracts
                        SET title = $1, document_type = $2, language = $3, data_json = $4, updated_at = $5
                        WHERE id = $6 AND (owner_id = $7 OR owner_id = 'default_user')
                    """, title, doc_type, language, data_str, now, contract_id, owner_id)
            return contract_id
        except Exception as e:
            logger.warning(f"Postgres save failed, falling back to SQLite: {e}")

    # High-concurrency async SQLite
    import aiosqlite
    async with aiosqlite.connect(str(DB_PATH), timeout=10.0) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA busy_timeout=5000;")
        if not contract_id:
            contract_id = str(uuid.uuid4())[:8]
            await db.execute("""
                INSERT INTO contracts (id, owner_id, title, document_type, language, data_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (contract_id, owner_id, title, doc_type, language, data_str, now, now))
        else:
            await db.execute("""
                UPDATE contracts
                SET title = ?, document_type = ?, language = ?, data_json = ?, updated_at = ?
                WHERE id = ? AND (owner_id = ? OR owner_id = 'default_user')
            """, (title, doc_type, language, data_str, now, contract_id, owner_id))
        await db.commit()
    return contract_id

async def list_contracts(owner_id: Optional[str] = None) -> List[Dict[str, Any]]:
    owner_id = owner_id or "default_user"
    if IS_POSTGRES:
        try:
            pool = await get_pg_pool()
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT id, owner_id, title, document_type, language, created_at, updated_at FROM contracts WHERE owner_id = $1 ORDER BY updated_at DESC",
                    owner_id
                )
                return [dict(r) for r in rows]
        except Exception as e:
            logger.warning(f"Postgres list failed, falling back to SQLite: {e}")

    import aiosqlite
    async with aiosqlite.connect(str(DB_PATH), timeout=10.0) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, owner_id, title, document_type, language, created_at, updated_at FROM contracts WHERE owner_id = ? ORDER BY updated_at DESC",
            (owner_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_contract(contract_id: str, owner_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if IS_POSTGRES:
        try:
            pool = await get_pg_pool()
            async with pool.acquire() as conn:
                if owner_id:
                    row = await conn.fetchrow("SELECT * FROM contracts WHERE id = $1 AND (owner_id = $2 OR owner_id = 'default_user')", contract_id, owner_id)
                else:
                    row = await conn.fetchrow("SELECT * FROM contracts WHERE id = $1", contract_id)
                if row:
                    res = dict(row)
                    res["data"] = json.loads(res["data_json"])
                    return res
                return None
        except Exception as e:
            logger.warning(f"Postgres get failed, falling back to SQLite: {e}")

    import aiosqlite
    async with aiosqlite.connect(str(DB_PATH), timeout=10.0) as db:
        db.row_factory = aiosqlite.Row
        if owner_id:
            query = "SELECT * FROM contracts WHERE id = ? AND (owner_id = ? OR owner_id = 'default_user')"
            params = (contract_id, owner_id)
        else:
            query = "SELECT * FROM contracts WHERE id = ?"
            params = (contract_id,)
        async with db.execute(query, params) as cursor:
            row = await cursor.fetchone()
            if row:
                res = dict(row)
                res["data"] = json.loads(res["data_json"])
                return res
            return None

async def update_remote_signature(contract_id: str, signature_data: str, target: str = "party2") -> bool:
    item = await get_contract(contract_id)
    if not item:
        return False
    data = item["data"]
    if target == "party1":
        data["party1_signature"] = signature_data
    else:
        data["party2_signature"] = signature_data

    await save_contract(item["title"], item["document_type"], item["language"], data, contract_id, owner_id=item.get("owner_id", "default_user"))
    return True

async def delete_contract(contract_id: str, owner_id: Optional[str] = None) -> bool:
    owner_id = owner_id or "default_user"
    if IS_POSTGRES:
        try:
            pool = await get_pg_pool()
            async with pool.acquire() as conn:
                res = await conn.execute(
                    "DELETE FROM contracts WHERE id = $1 AND (owner_id = $2 OR owner_id = 'default_user')",
                    contract_id, owner_id
                )
                return "DELETE 0" not in res
        except Exception as e:
            logger.warning(f"Postgres delete failed, falling back to SQLite: {e}")

    import aiosqlite
    async with aiosqlite.connect(str(DB_PATH), timeout=10.0) as db:
        res = await db.execute(
            "DELETE FROM contracts WHERE id = ? AND (owner_id = ? OR owner_id = 'default_user')",
            (contract_id, owner_id)
        )
        await db.commit()
        return res.rowcount > 0
