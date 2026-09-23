"""
app.py — the WHOLE USER INTERFACE (built with Streamlit).

Two pages (sidebar radio):
  Chat  -> students ask questions (RAG via MySQL chunks table)
  Admin -> upload PDFs + see documents / chat_logs / feedback as TABLES
"""
import streamlit as st
import os

from config import ADMIN_PASSWORD
from rag import ask
from database import (
    log_chat,
    log_feedback,
    log_document,
    get_chat_logs,
    get_documents,
    get_feedback_logs,
    count_chunks,
    setup_tables,
)

st.set_page_config(page_title="CollegeBot", page_icon="🎓", layout="wide")

db_status = setup_tables()

# Fresh deploy: empty knowledge base -> load starter facts once
try:
    if count_chunks() == 0 and os.path.exists("knowledge_base.txt"):
        from ingest import ingest_pdf
        with st.spinner("Loading knowledge base (first run only)..."):
            ingest_pdf("knowledge_base.txt")
except Exception:
    pass

with st.sidebar:
    st.title("🎓 CollegeBot")
    st.caption("RAG chatbot • LangChain • MySQL vector store")
    st.text(f"Database: {db_status}")
    st.text(f"Chunks in DB: {count_chunks()}")
    page = st.radio("Go to", ["💬 Chat", "🔐 Admin"])
    st.caption("Made with LangChain + Groq + sentence-transformers + MySQL")


def _as_table(rows, columns):
    """Turn list-of-dicts into a clean dataframe-friendly list of dicts."""
    if not rows:
        return []
    out = []
    for r in rows:
        out.append({c: r.get(c, "") for c in columns})
    return out


# ============================================================
# PAGE 1: CHAT
# ============================================================
if page == "💬 Chat":

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("💬 Ask CollegeBot")
    st.caption("Ask anything about the college — admissions, fees, timings, rules...")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["text"])

    user_q = st.chat_input("Type your question here...")
    if user_q:
        st.session_state.messages.append({"role": "user", "text": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)

        with st.chat_message("assistant"):
            with st.spinner("Searching the knowledge base..."):
                try:
                    answer, sources, secs = ask(user_q)
                except RuntimeError as e:
                    answer, sources, secs = f"⚠️ {e}", "", 0
                except Exception as e:
                    answer, sources, secs = f"⚠️ Something went wrong: {e}", "", 0
            st.markdown(answer)
            st.caption(f"⏱ {secs}s • sources: {sources or 'none'}")

        st.session_state.messages.append({"role": "assistant", "text": answer})
        row_id = log_chat(user_q, answer, sources, secs)
        st.session_state.last_id = row_id

        c1, c2 = st.columns(2)
        if c1.button("👍 Helpful"):
            log_feedback(row_id, "up")
            st.success("Thanks for the feedback!")
        if c2.button("👎 Not helpful"):
            log_feedback(row_id, "down")
            st.info("Got it — we'll improve!")

# ============================================================
# PAGE 2: ADMIN (password protected) — data shown as TABLES
# ============================================================
elif page == "🔐 Admin":

    st.title("🔐 Admin Panel")

    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False

    if not st.session_state.admin_ok:
        pw = st.text_input("Enter admin password", type="password")
        if st.button("Login"):
            if pw == ADMIN_PASSWORD:
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Wrong password")
        st.stop()

    st.success("Logged in as admin")

    # ---------- A) Upload a PDF into the knowledge base ----------
    st.header("📄 Add a document to the knowledge base")
    uploaded = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded and st.button("Ingest into MySQL chunks table"):
        with st.spinner("Reading, splitting and embedding the document..."):
            os.makedirs("uploads", exist_ok=True)
            path = os.path.join("uploads", uploaded.name)
            with open(path, "wb") as f:
                f.write(uploaded.getbuffer())

            from ingest import ingest_pdf
            n = ingest_pdf(path)
            log_document(uploaded.name, n)
            st.success(f"Done! Added {n} chunks from {uploaded.name}")

    # ---------- B) KB status metrics ----------
    st.header("🧠 Knowledge base status")
    m1, m2, m3 = st.columns(3)
    m1.metric("Chunks in MySQL/JSON", count_chunks())
    m2.metric("Documents ingested", len(get_documents(1000)))
    m3.metric("Chats logged", len(get_chat_logs(1000)))

    # ---------- C) All admin data as TABLES (tabs) ----------
    st.header("📊 Admin data (tables)")
    tab_chats, tab_docs, tab_fb, tab_chunks = st.tabs(
        ["💬 Chat logs", "📄 Documents", "👍 Feedback", "🧩 Chunks (vector store)"]
    )

    with tab_chats:
        rows = get_chat_logs(50)
        cols = ["id", "question", "answer", "sources", "seconds", "asked_at"]
        st.dataframe(
            _as_table(rows, cols),
            use_container_width=True,
            height=320,
            column_config={
                "id": "ID",
                "question": "Question",
                "answer": "Answer",
                "sources": "Sources",
                "seconds": st.column_config.NumberColumn("Sec", format="%.2f"),
                "asked_at": "Asked at",
            },
        )
        if not rows:
            st.info("No chats yet. Ask something on the Chat page.")

    with tab_docs:
        rows = get_documents(100)
        cols = ["id", "filename", "chunks", "added_at"]
        st.dataframe(
            _as_table(rows, cols),
            use_container_width=True,
            height=280,
            column_config={
                "id": "ID",
                "filename": "Filename",
                "chunks": st.column_config.NumberColumn("Chunks"),
                "added_at": "Added at",
            },
        )
        if not rows:
            st.info("No documents ingested yet.")

    with tab_fb:
        rows = get_feedback_logs(100)
        cols = ["id", "chat_id", "question", "rating", "given_at"]
        # normalize rating for display
        for r in rows:
            if r.get("rating") == "up":
                r["rating"] = "👍 up"
            elif r.get("rating") == "down":
                r["rating"] = "👎 down"
        st.dataframe(
            _as_table(rows, cols),
            use_container_width=True,
            height=280,
            column_config={
                "id": "ID",
                "chat_id": "Chat ID",
                "question": "Question",
                "rating": "Rating",
                "given_at": "Given at",
            },
        )
        if not rows:
            st.info("No feedback yet. Use the thumbs buttons on the Chat page.")

    with tab_chunks:
        from database import get_all_chunks
        chunk_rows = get_all_chunks()
        # show preview table without dumping full 384-float vectors
        preview = []
        for c in chunk_rows:
            preview.append({
                "id": c.get("id"),
                "source": c.get("source"),
                "chars": len(c.get("content") or ""),
                "dim": len(c.get("embedding") or []),
                "preview": (c.get("content") or "")[:120],
                "added_at": c.get("added_at"),
            })
        st.dataframe(
            preview,
            use_container_width=True,
            height=320,
            column_config={
                "id": "ID",
                "source": "Source file",
                "chars": "Chars",
                "dim": "Embedding dim",
                "preview": "Text preview",
                "added_at": "Added at",
            },
        )
        if not chunk_rows:
            st.info("No chunks yet. Upload a PDF or wait for first-run auto-ingest.")
        else:
            st.caption(
                "Full embedding vectors live in the MySQL `chunks` table "
                "(column `embedding`, JSON array of floats)."
            )
