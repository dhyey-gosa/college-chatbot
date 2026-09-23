"""
database.py — ALL MySQL work happens here.

Four tables:
  documents -> which files we added to the knowledge base
  chat_logs -> every question + answer the bot gave
  feedback  -> thumbs up / down from users
  chunks    -> knowledge-base text + embedding vector (replaces Chroma)

Embeddings are stored as a JSON array of numbers in MySQL.
If MySQL is not configured or fails, everything falls back to
local_data.json so the demo NEVER crashes.
"""
import json
import os
from datetime import datetime

import pymysql

from config import DB_CONFIG

LOCAL_FILE = "local_data.json"

_EMPTY = {"documents": [], "chat_logs": [], "feedback": [], "chunks": []}


def _local_read():
    """Read the local JSON backup file (used only when MySQL is off)."""
    if os.path.exists(LOCAL_FILE):
        with open(LOCAL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    # migrate older files that had no "chunks" key
    for key in _EMPTY:
        data.setdefault(key, [])
    return data


def _local_write(data):
    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _connect():
    """Open a MySQL connection. Returns None if not configured / fails."""
    if not DB_CONFIG["host"]:
        return None
    try:
        return pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            connect_timeout=8,
        )
    except Exception as e:
        print("MySQL not available, using local JSON instead:", e)
        return None


def setup_tables():
    """Create the 4 tables if they don't exist yet. Run once at startup."""
    conn = _connect()
    if conn is None:
        return "MySQL OFF (local JSON mode)"
    sql = """
    CREATE TABLE IF NOT EXISTS documents (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filename   VARCHAR(255),
        chunks     INT,
        added_at   DATETIME
    );
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question   TEXT,
        answer     TEXT,
        sources    TEXT,
        seconds    FLOAT,
        asked_at   DATETIME
    );
    CREATE TABLE IF NOT EXISTS feedback (
        id INT AUTO_INCREMENT PRIMARY KEY,
        chat_id    INT,
        rating     VARCHAR(10),
        given_at   DATETIME
    );
    CREATE TABLE IF NOT EXISTS chunks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        content    TEXT,
        source     VARCHAR(255),
        embedding  LONGTEXT,
        added_at   DATETIME
    );
    """
    try:
        with conn.cursor() as cur:
            for stmt in sql.split(";"):
                if stmt.strip():
                    cur.execute(stmt)
        conn.close()
        return "MySQL connected"
    except Exception as e:
        print("Table setup failed:", e)
        return "MySQL error (local JSON mode)"


# ---------- knowledge-base chunks (vector store in MySQL) ----------

def add_chunks(items):
    """
    items: list of dicts {content, source, embedding: list[float]}
    Returns number of rows inserted.
    """
    if not items:
        return 0
    conn = _connect()
    now = datetime.now()
    if conn is None:
        data = _local_read()
        next_id = (data["chunks"][-1]["id"] + 1) if data["chunks"] else 1
        for it in items:
            data["chunks"].append({
                "id": next_id,
                "content": it["content"],
                "source": it["source"],
                "embedding": it["embedding"],
                "added_at": str(now),
            })
            next_id += 1
        _local_write(data)
        return len(items)
    with conn.cursor() as cur:
        for it in items:
            cur.execute(
                "INSERT INTO chunks (content, source, embedding, added_at)"
                " VALUES (%s,%s,%s,%s)",
                (it["content"], it["source"],
                 json.dumps(it["embedding"]), now),
            )
    conn.close()
    return len(items)


def get_all_chunks():
    """Return every knowledge-base chunk: id, content, source, embedding (list[float])."""
    conn = _connect()
    if conn is None:
        rows = _local_read()["chunks"]
    else:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, content, source, embedding, added_at FROM chunks ORDER BY id"
            )
            rows = cur.fetchall()
        conn.close()
    out = []
    for r in rows:
        emb = r.get("embedding")
        if isinstance(emb, str):
            try:
                emb = json.loads(emb)
            except Exception:
                emb = []
        out.append({
            "id": r.get("id"),
            "content": r.get("content") or "",
            "source": r.get("source") or "?",
            "embedding": emb or [],
            "added_at": r.get("added_at"),
        })
    return out


def count_chunks():
    conn = _connect()
    if conn is None:
        return len(_local_read()["chunks"])
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM chunks")
        n = cur.fetchone()["n"]
    conn.close()
    return n


# ---------- documents / chats / feedback ----------

def log_document(filename, chunks):
    conn = _connect()
    if conn is None:
        data = _local_read()
        next_id = (data["documents"][-1]["id"] + 1) if data["documents"] else 1
        data["documents"].append({
            "id": next_id, "filename": filename, "chunks": chunks,
            "added_at": str(datetime.now()),
        })
        _local_write(data)
        return
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO documents (filename, chunks, added_at) VALUES (%s,%s,%s)",
            (filename, chunks, datetime.now()),
        )
    conn.close()


def log_chat(question, answer, sources, seconds):
    """Save one chat exchange. Returns the new row id (used for feedback)."""
    conn = _connect()
    now = str(datetime.now())
    if conn is None:
        data = _local_read()
        row_id = (data["chat_logs"][-1]["id"] + 1) if data["chat_logs"] else 1
        data["chat_logs"].append({
            "id": row_id, "question": question, "answer": answer,
            "sources": sources, "seconds": seconds, "asked_at": now,
        })
        _local_write(data)
        return row_id
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO chat_logs (question, answer, sources, seconds, asked_at)"
            " VALUES (%s,%s,%s,%s,%s)",
            (question, answer, sources, seconds, datetime.now()),
        )
        cur.execute("SELECT LAST_INSERT_ID() AS id")
        row_id = cur.fetchone()["id"]
    conn.close()
    return row_id


def log_feedback(chat_id, rating):
    conn = _connect()
    if conn is None:
        data = _local_read()
        next_id = (data["feedback"][-1]["id"] + 1) if data["feedback"] else 1
        data["feedback"].append({
            "id": next_id, "chat_id": chat_id, "rating": rating,
            "given_at": str(datetime.now()),
        })
        _local_write(data)
        return
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO feedback (chat_id, rating, given_at) VALUES (%s,%s,%s)",
            (chat_id, rating, datetime.now()),
        )
    conn.close()


def get_chat_logs(limit=50):
    """Newest chat rows (Admin table)."""
    conn = _connect()
    if conn is None:
        rows = list(reversed(_local_read()["chat_logs"]))[:limit]
        return rows
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, question, answer, sources, seconds, asked_at "
            "FROM chat_logs ORDER BY id DESC LIMIT %s",
            (limit,),
        )
        rows = cur.fetchall()
    conn.close()
    return rows


def get_documents(limit=100):
    """Ingested files (Admin table)."""
    conn = _connect()
    if conn is None:
        return list(reversed(_local_read()["documents"]))[:limit]
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, filename, chunks, added_at FROM documents "
            "ORDER BY id DESC LIMIT %s",
            (limit,),
        )
        rows = cur.fetchall()
    conn.close()
    return rows


def get_feedback_logs(limit=100):
    """Feedback joined with the question it belongs to (Admin table)."""
    conn = _connect()
    if conn is None:
        data = _local_read()
        chats = {c["id"]: c for c in data["chat_logs"]}
        rows = []
        for f in reversed(data["feedback"]):
            c = chats.get(f.get("chat_id"), {})
            rows.append({
                "id": f.get("id"),
                "chat_id": f.get("chat_id"),
                "question": c.get("question", ""),
                "rating": f.get("rating"),
                "given_at": f.get("given_at"),
            })
            if len(rows) >= limit:
                break
        return rows
    with conn.cursor() as cur:
        cur.execute(
            "SELECT f.id, f.chat_id, c.question, f.rating, f.given_at "
            "FROM feedback f "
            "LEFT JOIN chat_logs c ON c.id = f.chat_id "
            "ORDER BY f.id DESC LIMIT %s",
            (limit,),
        )
        rows = cur.fetchall()
    conn.close()
    return rows
