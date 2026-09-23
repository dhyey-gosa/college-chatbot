"""
config.py — keeps ALL settings in ONE place.

We read values from a .env file (local) or Render's dashboard (online).
This way our secret keys are never written inside the code itself.
"""
import os
from dotenv import load_dotenv

# This line reads the .env file and loads the values into os.environ
load_dotenv()

# ---------- API KEYS ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")      # for the LLM (answers)
# Embeddings run LOCALLY via sentence-transformers — no Google/API key needed.

# ---------- MYSQL DATABASE ----------
# If DB_HOST is empty, the app runs in "local mode" and skips MySQL.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", ""),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", ""),
}

# Where the vector database (Chroma) saves its files
CHROMA_DIR = "chroma_db"

# The model we use (all free)
LLM_MODEL = "openai/gpt-oss-120b"            # Groq's free model (available on this key)
EMBED_MODEL = "all-MiniLM-L6-v2"             # local sentence-transformers model (~80MB, downloads once)

# Admin password for the Admin page (set in .env)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "college123")
