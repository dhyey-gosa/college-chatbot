"""
database.py — ALL MySQL work happens here.

Three tables:
  documents -> which files we added to the knowledge base
  chat_logs -> every question + answer the bot gave (real INSERTs you can show ma'am)
  feedback  -> thumbs up / down from users

IMPORTANT (easy mode): if MySQL is not configured or fails to connect,
we fall back to a local JSON file so the app NEVER crashes during your demo.
"""
import json
import os
from datetime import datetime

import pymysql

from config import DB_CONFIG

# Local backup file used when MySQL is not available
LOCAL_FILE = "local_data.json"


def _local_read():
    """Read the local JSON backup file (used only when MySQL is off)."""
    if os.path.exists(LOCAL_FILE):
        with open(LOCAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"documents": [], "chat_logs": [], "feedback": []}


def _local_write(data):
    """Save data to the local JSON backup file."""
    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _connect():
    """Open a MySQL connection. Returns None if not configured / fails."""
    if not DB_CONFIG["host"]:          # no host given -> local mode
        return None
    try:
        return pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            cursorclass=pymysql.cursors.DictCursor,  # rows come back as dicts
            autocommit=True,
            connect_timeout=8,
        )
    except Exception as e:
        print("MySQL not available, using local JSON instead:", e)
        return None


def setup_tables():
    """Create the 3 tables if they don't exist yet. Run once at startup."""
    conn = _connect()
    if conn is None:
        return "MySQL OFF (local mode)"
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
    """
    try:
        with conn.cursor() as cur:
            for stmt in sql.split(";"):
                if stmt.strip():
                    cur.execute(stmt)
        conn.close()
        return "MySQL connected ✓"
    except Exception as e:
        print("Table setup failed:", e)
        return "MySQL error (local mode)"


def log_document(filename, chunks):
    """Save a record that a file was ingested into the vector store."""
    conn = _connect()
    if conn is None:
        data = _local_read()
        data["documents"].append({"filename": filename, "chunks": chunks,
                                  "added_at": str(datetime.now())})
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
        row_id = len(data["chat_logs"]) + 1
        data["chat_logs"].append({"id": row_id, "question": question,
                                  "answer": answer, "sources": sources,
                                  "seconds": seconds, "asked_at": now})
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
    """Save thumbs up / down for a given chat row."""
    conn = _connect()
    if conn is None:
        data = _local_read()
        data["feedback"].append({"chat_id": chat_id, "rating": rating,
                                 "given_at": str(datetime.now())})
        _local_write(data)
        return
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO feedback (chat_id, rating, given_at) VALUES (%s,%s,%s)",
            (chat_id, rating, datetime.now()),
        )
    conn.close()


def get_chat_logs(limit=50):
    """Read the newest chat rows (shown on the Admin page)."""
    conn = _connect()
    if conn is None:
        data = _local_read()
        return list(reversed(data["chat_logs"]))[:limit]
    with conn.cursor() as cur:
        cur.execute(
            "SELECT question, answer, sources, seconds, asked_at "
            "FROM chat_logs ORDER BY id DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
    conn.close()
    return rows
