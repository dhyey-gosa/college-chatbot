# 🎓 CollegeBot — RAG Chatbot with MySQL

A college FAQ chatbot built with **LangChain RAG**, **Streamlit**, **MySQL**, and free AI APIs. Deployed free on **Render**.

## How it works (one diagram, memorize this for the viva)

```
User question
   ↓
Streamlit UI (app.py)
   ↓
rag.py — the RAG pipeline:
   1) RETRIEVE: Chroma finds the 3 most similar text chunks (vector search,
      embeddings computed locally by sentence-transformers)
   2) AUGMENT:  chunks are pasted into the LLM prompt as context
   3) GENERATE: Groq's Llama-3.3-70B writes the answer from that context
   ↓
database.py — saves the Q&A into MySQL (chat_logs table)
   ↓
Answer shown to user + 👍/👎 feedback saved to MySQL
```

## Files (what each one does)

| File | What it does | Lines to understand |
|---|---|---|
| `app.py` | The whole UI (chat + admin pages) | Start here |
| `rag.py` | RAG pipeline: retrieve → augment → generate | The brain |
| `ingest.py` | Splits PDFs into chunks and stores them in Chroma | Runs when uploading |
| `database.py` | All MySQL work (3 tables: documents, chat_logs, feedback) | The SQL part |
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

### One warning about Render free tier
- App sleeps after 15 min idle → open the link 5 min before demo to wake it
- Chroma data lives on the app's disk → if you re-deploy, re-run `python ingest.py knowledge_base.txt` (or re-upload via Admin page). Chat logs are safe in MySQL.

## Viva cheat sheet (for your friend)

- **What is RAG?** Retrieval Augmented Generation — the bot searches its own notes first, then answers using them. Like an open-book exam.
- **What is an embedding?** A list of numbers representing a sentence's meaning. Similar meaning = similar numbers.
- **What is Chroma?** A vector database that stores embeddings and finds the most similar ones fast.
- **What is MySQL doing here?** Saving every chat (chat_logs), uploaded files (documents), and user feedback (feedback). Show a live SELECT in the admin page.
- **Why LangChain?** It's the glue that connects models, the vector store, and prompts with a few lines of code.
- **Why Groq?** Free API that runs Llama 3.3 70B very fast.
