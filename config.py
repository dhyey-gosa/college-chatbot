"""
config.py — keeps ALL settings in ONE place.

Reads secrets from, in order:
  1. environment variables (.env locally, host dashboard in the cloud)
  2. Streamlit secrets (share.streamlit.io → App settings → Secrets)
This way secret keys are never written inside the code itself.
"""
import os
from dotenv import load_dotenv

# This line reads the .env file and loads the values into os.environ
load_dotenv()


def _secret(name: str, default: str = "") -> str:
    """Read a setting from env vars, then fall back to Streamlit secrets."""
    val = os.getenv(name, "")
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return default


# ---------- API KEYS ----------
GROQ_API_KEY = _secret("GROQ_API_KEY")          # for the LLM (answers)
# Embeddings run LOCALLY via sentence-transformers — no Google/API key needed.

# ---------- MYSQL DATABASE ----------
# If DB_HOST is empty, the app runs in "local mode" and skips MySQL.
DB_CONFIG = {
    "host": _secret("DB_HOST"),
    "port": int(_secret("DB_PORT", "3306") or "3306"),
    "user": _secret("DB_USER"),
    "password": _secret("DB_PASSWORD"),
    "database": _secret("DB_NAME"),
}

# Where the vector database (Chroma) saves its files
CHROMA_DIR = "chroma_db"

# The model we use (all free)
LLM_MODEL = "openai/gpt-oss-120b"            # Groq's free model (available on this key)
EMBED_MODEL = "all-MiniLM-L6-v2"             # local sentence-transformers model (~80MB, downloads once)

# Admin password for the Admin page (set in .env / host secrets)
ADMIN_PASSWORD = _secret("ADMIN_PASSWORD", "college123")
