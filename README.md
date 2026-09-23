# 🎓 CollegeBot — RAG Chatbot with MySQL

A college FAQ chatbot built with **LangChain RAG**, **Streamlit**, **MySQL**, and free AI APIs. Deployed free on **Render**.

## How it works (one diagram, memorize this for the viva)

```
User question
   ↓
Streamlit UI (app.py)
   ↓
rag.py — the RAG pipeline:
   1) RETRIEVE: MySQL `chunks` table — embed the question (sentence-transformers
      on CPU), cosine-rank stored vectors, take the top 3
   2) AUGMENT:  chunks are pasted into the LLM prompt as context
   3) GENERATE: Groq LLM writes the answer from that context
   ↓
database.py — saves the Q&A into MySQL (chat_logs table; JSON fallback)
   ↓
Answer shown to user + 👍/👎 feedback saved to MySQL
```

## Files (what each one does)

| File | What it does | Lines to understand |
|---|---|---|
| `app.py` | The whole UI (chat + admin pages) | Start here |
| `rag.py` | RAG pipeline: retrieve → augment → generate | The brain |
| `ingest.py` | Splits PDFs into chunks and stores them in MySQL `chunks` | Runs when uploading |
| `database.py` | All MySQL work (documents, chat_logs, feedback, **chunks**) | The SQL part |
| `config.py` | Reads secrets from `.env` / Render dashboard | Security |
| `knowledge_base.txt` | Starter facts the bot knows | Demo data |

## Run it on your laptop (5 steps)

```bash
# 1. create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows  (Mac/Linux: source venv/bin/activate)

# 2. install libraries
pip install -r requirements.txt

# 3. make your secrets file: copy .env.example to .env and fill in keys
#    (GROQ_API_KEY is already filled for you)

# 4. teach the bot the starter knowledge
python ingest.py knowledge_base.txt

# 5. run the app
streamlit run app.py
```

Open http://localhost:8501 — chat away. Admin page password is in `.env` (`ADMIN_PASSWORD`).

## Free API keys (1 minute)

- **Groq (LLM):** https://console.groq.com/keys → "Create API Key"
- Embeddings need **no key** — sentence-transformers runs `all-MiniLM-L6-v2` on your machine.

## Deploy on Render (free)

1. Push this folder to a **GitHub repo** (keep `.env` out — `.gitignore` already handles it)
2. Go to https://dashboard.render.com → **New +** → **Web Service** → connect the repo
3. Render reads `render.yaml` automatically. Set these env vars in the dashboard:
   - `GROQ_API_KEY`, `ADMIN_PASSWORD`
   - MySQL keys (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`) — from Aiven
4. Deploy. Your link: `https://collegebot-xxxx.onrender.com`

**Free MySQL that never expires:** https://aiven.io/free-mysql-database → create free MySQL → copy the "Connection information" values into `.env` / Render.

### One warning about free hosting
- App may sleep after idle → open the link a minute before demo to wake it
- Without MySQL configured, vectors + logs live in `local_data.json` on the app disk → re-deploy wipes them; re-run `python ingest.py knowledge_base.txt` (or first-run auto-ingest / Admin upload). With MySQL keys set, all data survives re-deploys.

## Viva cheat sheet (for your friend)

- **What is RAG?** Retrieval Augmented Generation — the bot searches its own notes first, then answers using them. Like an open-book exam.
- **What is an embedding?** A list of numbers representing a sentence's meaning. Similar meaning = similar numbers.
- **Where are vectors stored?** MySQL table `chunks` — each row has the text, source file, and a JSON array of floats (the embedding). Cosine similarity picks the top 3.
- **What is MySQL doing here?** Four tables: `chunks` (knowledge + vectors), `chat_logs`, `documents`, `feedback`. Admin page shows them all as tables.
- **Why LangChain?** It's the glue that connects models, loaders, splitters, and prompts with a few lines of code.
- **Why Groq?** Free API that runs open LLMs very fast.
