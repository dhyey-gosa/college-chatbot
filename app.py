"""
app.py — the WHOLE USER INTERFACE (built with Streamlit).

Streamlit turns simple Python into a website. One command runs it:
    streamlit run app.py

You get TWO pages in one app (switch in the sidebar):
  💬 Chat  -> students ask questions
  🔐 Admin -> upload PDFs into the knowledge base + see MySQL chat logs
"""
import streamlit as st
import os

from config import ADMIN_PASSWORD
from rag import ask, load_vectorstore
from database import log_chat, log_feedback, log_document, get_chat_logs, setup_tables

# ---------- Basic page setup ----------
st.set_page_config(page_title="CollegeBot", page_icon="🎓", layout="wide")

# ---------- Run table setup once, show DB status in sidebar ----------
db_status = setup_tables()

with st.sidebar:
    st.title("🎓 CollegeBot")
    st.caption("RAG chatbot • LangChain • MySQL")
    st.text(f"Database: {db_status}")
    page = st.radio("Go to", ["💬 Chat", "🔐 Admin"])
    st.caption("Made with LangChain + Groq + sentence-transformers + Chroma + MySQL")


# ============================================================
# PAGE 1: CHAT
# ============================================================
if page == "💬 Chat":

    # st.session_state = Streamlit's memory between clicks.
    # We store the chat history there so old messages stay on screen.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("💬 Ask CollegeBot")
    st.caption("Ask anything about the college — admissions, fees, timings, rules…")

    # Draw all past messages
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["text"])

    # chat_input shows a text box at the bottom; value arrives when user presses Enter
    user_q = st.chat_input("Type your question here…")
    if user_q:

        # 1) show the user's question
        st.session_state.messages.append({"role": "user", "text": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)

        # 2) get the answer from the RAG pipeline (rag.py)
        with st.chat_message("assistant"):
            with st.spinner("Searching the knowledge base…"):
                try:
                    answer, sources, secs = ask(user_q)
                except RuntimeError as e:
                    answer, sources, secs = f"⚠️ {e}", "", 0
                except Exception as e:
                    answer, sources, secs = f"⚠️ Something went wrong: {e}", "", 0
            st.markdown(answer)
            st.caption(f"⏱ {secs}s • sources: {sources or 'none'}")

        # 3) remember it + save one row into MySQL (chat_logs table)
        st.session_state.messages.append({"role": "assistant", "text": answer})
        row_id = log_chat(user_q, answer, sources, secs)
        st.session_state.last_id = row_id

        # 4) thumbs up / down feedback (saved into MySQL too)
        c1, c2 = st.columns(2)
        if c1.button("👍 Helpful"):
            log_feedback(row_id, "up")
            st.success("Thanks for the feedback!")
        if c2.button("👎 Not helpful"):
            log_feedback(row_id, "down")
            st.info("Got it — we'll improve!")

# ============================================================
# PAGE 2: ADMIN  (password protected)
# ============================================================
elif page == "🔐 Admin":

    st.title("🔐 Admin Panel")

    # Simple password gate
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
        st.stop()   # stop here = nothing below is shown until login

    st.success("Logged in as admin")

    # ---------- A) Upload a PDF into the knowledge base ----------
    st.header("📄 Add a PDF to the knowledge base")
    uploaded = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded and st.button("Ingest into vector database"):
        with st.spinner("Reading, splitting and embedding the PDF…"):
            # save the upload temporarily
            os.makedirs("uploads", exist_ok=True)
            path = os.path.join("uploads", uploaded.name)
            with open(path, "wb") as f:
                f.write(uploaded.getbuffer())

            # import here so the page loads fast
            from ingest import ingest_pdf
            n = ingest_pdf(path)

            log_document(uploaded.name, n)     # record it in MySQL
            st.success(f"Done! Added {n} chunks from {uploaded.name}")

    # ---------- B) Show what the vector store contains ----------
    st.header("🧠 Knowledge base status")
    try:
        count = load_vectorstore()._collection.count()
        st.metric("Chunks stored in Chroma", count)
    except Exception:
        st.metric("Chunks stored in Chroma", 0)

    # ---------- C) Show MySQL chat logs ----------
    st.header("🗄️ Last 20 chats (from MySQL)")
    rows = get_chat_logs(20)
    if not rows:
        st.caption("No chats yet. Ask something on the Chat page!")
    for r in rows:
        with st.expander(f"❓ {r['question']}"):
            st.markdown(r["answer"])
            st.caption(f"sources: {r['sources']} • {r['seconds']}s • at {r['asked_at']}")
