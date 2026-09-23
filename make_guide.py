# Generates CollegeBot_Code_Guide.pdf — full code walkthrough + viva Q&A
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

OUT = r"D:\college worjk\college-chatbot\CollegeBot_Code_Guide.pdf"

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="CoverTitle", fontName="Helvetica-Bold", fontSize=26,
    leading=32, alignment=TA_CENTER, textColor=colors.HexColor("#1a1a2e"),
    spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="CoverSub", fontName="Helvetica", fontSize=13,
    leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#333333"),
    spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="H1x", fontName="Helvetica-Bold", fontSize=16, leading=20,
    textColor=colors.HexColor("#0d47a1"), spaceBefore=14, spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="H2x", fontName="Helvetica-Bold", fontSize=13, leading=17,
    textColor=colors.HexColor("#1565c0"), spaceBefore=12, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="H3x", fontName="Helvetica-Bold", fontSize=11, leading=15,
    textColor=colors.HexColor("#333"), spaceBefore=8, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="Bodyx", fontName="Helvetica", fontSize=10.5, leading=15,
    alignment=TA_JUSTIFY, spaceAfter=6, textColor=colors.HexColor("#222"),
))
styles.add(ParagraphStyle(
    name="Bulletx", fontName="Helvetica", fontSize=10.5, leading=15,
    leftIndent=14, bulletIndent=4, spaceAfter=3, textColor=colors.HexColor("#222"),
))
styles.add(ParagraphStyle(
    name="CodeBlock", fontName="Courier", fontSize=8.5, leading=11.5,
    backColor=colors.HexColor("#f4f4f4"), borderPadding=6,
    leftIndent=0, rightIndent=0, spaceBefore=4, spaceAfter=8,
    textColor=colors.HexColor("#111"),
))
styles.add(ParagraphStyle(
    name="Callout", fontName="Helvetica", fontSize=10.5, leading=15,
    backColor=colors.HexColor("#e8f5e9"), borderPadding=8,
    spaceBefore=6, spaceAfter=10, textColor=colors.HexColor("#1b5e20"),
    alignment=TA_LEFT,
))
styles.add(ParagraphStyle(
    name="Warn", fontName="Helvetica", fontSize=10.5, leading=15,
    backColor=colors.HexColor("#fff3e0"), borderPadding=8,
    spaceBefore=6, spaceAfter=10, textColor=colors.HexColor("#e65100"),
))
styles.add(ParagraphStyle(
    name="QA", fontName="Helvetica", fontSize=10.5, leading=15,
    spaceAfter=4, textColor=colors.HexColor("#111"),
))
styles.add(ParagraphStyle(
    name="Q", fontName="Helvetica-Bold", fontSize=11, leading=15,
    spaceBefore=8, spaceAfter=3, textColor=colors.HexColor("#0d47a1"),
))
styles.add(ParagraphStyle(
    name="FooterC", fontName="Helvetica", fontSize=8, alignment=TA_CENTER,
    textColor=colors.grey,
))
styles.add(ParagraphStyle(
    name="Tbl", fontName="Helvetica", fontSize=9.5, leading=13,
))
styles.add(ParagraphStyle(
    name="TblH", fontName="Helvetica-Bold", fontSize=9.5, leading=13,
    textColor=colors.white,
))


# Helvetica/WinAnsi-safe replacements (emoji & arrows break PDF glyphs)
_GLYPH_MAP = {
    "🎓": "[College]",
    "💬": "[Chat]",
    "🔐": "[Admin]",
    "👍": "[Yes]",
    "👎": "[No]",
    "📄": "[PDF]",
    "🧠": "[KB]",
    "🗄️": "[DB]",
    "🗄": "[DB]",
    "❓": "[Q]",
    "⏱": "[Time]",
    "✅": "[OK]",
    "→": "->",
    "←": "<-",
    "↑": "^",
    "↓": "v",
    "—": "-",
    "–": "-",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "…": "...",
    "×": "x",
    "₹": "Rs.",
    "•": "-",
}


def sanitize(text: str) -> str:
    for k, v in _GLYPH_MAP.items():
        text = text.replace(k, v)
    # strip any remaining non-latin1 chars that WinAnsi cannot draw
    return "".join(ch if ord(ch) < 256 else "?" for ch in text)


def P(text, style="Bodyx"):
    return Paragraph(sanitize(text), styles[style])


def B(text):
    return Paragraph(sanitize(text), styles["Bulletx"], bulletText="-")


def code(src: str):
    src = sanitize(src)
    lines = []
    for line in src.splitlines():
        if len(line) > 95:
            line = line[:92] + "..."
        lines.append(line)
    return Preformatted("\n".join(lines), styles["CodeBlock"])


def qa(q, a):
    return [
        Paragraph("Q: " + sanitize(escape(q)), styles["Q"]),
        Paragraph("<b>A:</b> " + sanitize(escape(a)), styles["QA"]),
        Spacer(1, 4),
    ]


def section_table(headers, rows):
    data = [[Paragraph(sanitize(h), styles["TblH"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(sanitize(c), styles["Tbl"]) for c in row])
    t = Table(data, colWidths=[3.2 * cm, 13.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fafafa")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#bbb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#ffffff"), colors.HexColor("#f0f4f8")]),
    ]))
    return t


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#0d47a1"))
    canvas.setLineWidth(1.2)
    canvas.line(1.8 * cm, A4[1] - 1.2 * cm, A4[0] - 1.8 * cm, A4[1] - 1.2 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(1.8 * cm, A4[1] - 1.0 * cm, "CollegeBot - Complete Code Guide & Viva Q&A")
    canvas.drawRightString(A4[0] - 1.8 * cm, A4[1] - 1.0 * cm, "RAG Chatbot Presentation Pack")
    canvas.line(1.8 * cm, 1.2 * cm, A4[0] - 1.8 * cm, 1.2 * cm)
    canvas.drawString(1.8 * cm, 0.8 * cm, "Streamlit + LangChain + Groq + MySQL vector store")
    canvas.drawRightString(A4[0] - 1.8 * cm, 0.8 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build():
    doc = BaseDocTemplate(
        OUT, pagesize=A4,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
        title="CollegeBot Code Guide",
        author="CollegeBot Team",
        subject="Code walkthrough and viva Q&A for CollegeBot RAG chatbot",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="all", frames=frame, onPage=on_page)])

    S = []

    # ========== COVER ==========
    S.append(Spacer(1, 2.5 * cm))
    S.append(P("CollegeBot", "CoverTitle"))
    S.append(P("Complete Code Guide &amp; Viva Q&amp;A", "CoverTitle"))
    S.append(Spacer(1, 0.4 * cm))
    S.append(P("A beginner-friendly walkthrough of every file in the project", "CoverSub"))
    S.append(P("RAG Chatbot for College FAQ — built with Python", "CoverSub"))
    S.append(Spacer(1, 1.2 * cm))
    S.append(P(
        "Live app: https://chatbot-mem.streamlit.app/<br/>"
        "GitHub: https://github.com/dhyey-gosa/college-chatbot",
        "CoverSub",
    ))
    S.append(Spacer(1, 1.5 * cm))
    S.append(P(
        "<b>How to use this guide:</b> Read Part 1 to understand the big picture. "
        "Part 2 explains each file line-by-line in plain English. "
        "Part 3 is a glossary of every technical term. "
        "Part 4 is the Q&amp;A bank for when ma'am asks questions. "
        "Part 5 is the live demo script — follow it click-by-click during the presentation.",
        "Callout",
    ))
    S.append(PageBreak())

    # ========== PART 1 ==========
    S.append(P("Part 1 — What We Built (The Big Picture)", "H1x"))
    S.append(P(
        "CollegeBot is a website chatbot that answers questions about a college "
        "(fees, library timings, hostel rules, admission dates, etc.). "
        "Unlike a normal chatbot that only knows what it was trained on, "
        "CollegeBot first <b>searches its own notes</b> (a knowledge base of college facts), "
        "then writes an answer <b>using only those notes</b>. This technique is called "
        "<b>RAG — Retrieval Augmented Generation</b>.",
        "Bodyx",
    ))

    S.append(P("1.1 One-sentence summary for ma'am", "H2x"))
    S.append(P(
        "\"CollegeBot is a Retrieval-Augmented Generation chatbot: it retrieves the most "
        "relevant chunks from a college knowledge base stored in MySQL (table `chunks`), "
        "then generates an answer with a large language model (via the Groq API), "
        "and logs every Q&amp;A into MySQL with a Streamlit web UI.\"",
        "Callout",
    ))

    S.append(P("1.2 How a question flows through the system", "H2x"))
    S.append(code(
"""User types a question in the browser
        |
        v
[app.py]  Streamlit UI receives the text box input
        |
        v
[rag.py]  --- RETRIEVE ---
          Embed the question into numbers, cosine-rank MySQL `chunks`,
          grab the top 3 most similar text rows
        |
        v
[rag.py]  --- AUGMENT ---
          Paste those 3 chunks into a prompt as CONTEXT
        |
        v
[rag.py]  --- GENERATE ---
          Send prompt to Groq LLM (openai/gpt-oss-120b),
          get back a plain-English answer
        |
        v
[database.py] Save question, answer, sources, time
              into MySQL chat_logs table (or local JSON)
        |
        v
[app.py]  Show answer on screen + thumbs up/down buttons"""
    ))

    S.append(P("1.3 Tech stack (what each tool does)", "H2x"))
    S.append(section_table(
        ["Tool", "Role in this project"],
        [
            ["Python 3.11", "The programming language everything is written in."],
            ["Streamlit", "Turns Python into a web UI (chat page + admin page) with almost no HTML/CSS."],
            ["LangChain", "Glue library that connects LLMs, prompts, and vector databases."],
            ["Groq API", "Free/fast cloud service that runs the LLM and returns answers."],
            ["MySQL (4 tables)", "chunks (vectors + text), chat_logs, documents, feedback. JSON file fallback if MySQL is off."],
            ["sentence-transformers", "Local model (all-MiniLM-L6-v2) that converts text into embedding vectors."],
            ["pymysql", "Python driver that talks to MySQL."],
            ["PyPDF / TextLoader", "Reads PDF and TXT files so we can ingest their content."],
            ["python-dotenv", "Loads secret keys from a .env file into environment variables."],
            ["GitHub", "Hosts the source code; Streamlit Cloud pulls from it to deploy."],
            ["Streamlit Community Cloud", "Free hosting that runs streamlit run app.py and gives a public URL."],
        ],
    ))

    S.append(P("1.4 Project file map", "H2x"))
    S.append(section_table(
        ["File", "Plain-English job"],
        [
            ["app.py", "The whole website: Chat page and password-protected Admin page (tables)."],
            ["rag.py", "The brain. Does retrieve (MySQL cosine search), augment, generate."],
            ["ingest.py", "Reads a file, splits it into chunks, embeds them, stores in MySQL chunks table."],
            ["database.py", "All MySQL code: documents, chat_logs, feedback, chunks. Falls back to local_data.json."],
            ["config.py", "Loads secrets (.env / Streamlit secrets) and model names in one place."],
            ["knowledge_base.txt", "Starter facts about Sunrise College (fees, library, hostel, etc.)."],
            ["requirements.txt", "Exact list of Python packages to install (pip install -r requirements.txt)."],
            ["render.yaml", "Optional Render.com deploy config (we actually used Streamlit Cloud)."],
            [".env / .env.example", "Secret keys file. Real .env is NEVER pushed to GitHub."],
            [".gitignore", "Tells git which files to ignore (.env, venv, caches...)."],
            ["local_data.json", "Created at runtime when MySQL is OFF — same 4 collections as the tables."],
        ],
    ))

    S.append(PageBreak())

    # ========== PART 2: FILE BY FILE ==========
    S.append(P("Part 2 — File-by-File Code Walkthrough", "H1x"))
    S.append(P(
        "Read this part top to bottom before the demo. Every important block of code "
        "is shown with a plain-English explanation of what it means.",
        "Bodyx",
    ))

    # --- config.py ---
    S.append(P("2.1 config.py — Settings &amp; Secrets (52 lines)", "H2x"))
    S.append(P(
        "<b>What it does:</b> Reads all secret keys and settings from one place so keys "
        "are never hard-coded inside app logic. Locally it reads a .env file; on Streamlit "
        "Cloud it reads App Settings → Secrets. Same code works in both places.",
        "Bodyx",
    ))
    S.append(P("Key code:", "H3x"))
    S.append(code(
"""import os
from dotenv import load_dotenv
load_dotenv()   # reads .env file into environment variables

def _secret(name: str, default: str = "") -> str:
    val = os.getenv(name, "")          # 1) try environment variable
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and name in st.secrets:
            return str(st.secrets[name])  # 2) else try Streamlit secrets
    except Exception:
        pass
    return default

    GROQ_API_KEY = _secret("GROQ_API_KEY")     # key for the LLM
LLM_MODEL    = "openai/gpt-oss-120b"       # which Groq model to use
EMBED_MODEL  = "all-MiniLM-L6-v2"          # local embedding model
ADMIN_PASSWORD = _secret("ADMIN_PASSWORD", "college123")"""
    ))
    S.append(B("<b>load_dotenv()</b> — loads key=value pairs from the hidden .env file into the process environment."))
    S.append(B("<b>_secret(name)</b> — tries env var first, then Streamlit secrets, then a default. Dual-source lookup so local + cloud both work."))
    S.append(B("<b>GROQ_API_KEY</b> — the password that lets our app call Groq's free LLM API. Never commit the real key."))
    S.append(B("<b>LLM_MODEL</b> — which Groq model to call. We use openai/gpt-oss-120b (available on our key)."))
    S.append(B("<b>EMBED_MODEL</b> — name of the sentence-transformers model. It runs on our CPU, no API key needed."))
    S.append(B("<b>ADMIN_PASSWORD</b> — gate for the Admin page. Default demo value is college123."))
    S.append(B("<b>DB_CONFIG</b> — MySQL connection details. Empty DB_HOST means local JSON mode (no MySQL)."))

    # --- rag.py ---
    S.append(P("2.2 rag.py — The RAG Brain (MySQL vector search)", "H2x"))
    S.append(P(
        "<b>What it does:</b> Implements the full Retrieval Augmented Generation pipeline. "
        "Retrieval reads the MySQL <b>chunks</b> table (or local_data.json), computes cosine "
        "similarity against the question embedding, and keeps the top 3. "
        "If the LLM is a student writing an <i>open-book</i> exam, those 3 rows are the book pages.",
        "Bodyx",
    ))
    S.append(P("Core idea in code:", "H3x"))
    S.append(code(
"""def retrieve(question, k=3):
    rows = get_all_chunks()          # FROM chunks  (MySQL or JSON)
    q_vec = embed_text(question)     # sentence-transformers, 384 floats
    scored = [(_cosine(q_vec, r["embedding"]), r) for r in rows]
    scored.sort(reverse=True)        # highest similarity first
    return top k rows

def ask(question):
    hits = retrieve(question, k=3)                    # 1) RETRIEVE
    context = "\\n\\n".join(h["content"] for h in hits)  # 2) AUGMENT
    messages = [SystemMessage(SYSTEM_PROMPT.format(context=context)),
                HumanMessage(question)]
    answer = _get_llm().invoke(messages).content      # 3) GENERATE
    return answer, sources, elapsed_seconds"""
    ))
    S.append(P("The system prompt (personality + rules):", "H3x"))
    S.append(code(
"""You are CollegeBot, a helpful assistant for college students.
Answer ONLY using the context below. If the answer is not in the context,
say politely: "I don't have that in my knowledge base yet."
Keep answers short and friendly (max 5 sentences).

CONTEXT:
{context}"""
    ))
    S.append(B("<b>get_all_chunks()</b> — loads every row from MySQL table `chunks` (or local JSON); embedding is a JSON array of floats."))
    S.append(B("<b>_cosine(a, b)</b> — similarity score between question vector and each chunk vector; we sort descending and keep top 3."))
    S.append(B("<b>k=3</b> — we only pass 3 chunks to the LLM. Fewer chunks = faster + cheaper + less noise."))
    S.append(B("<b>SYSTEM_PROMPT</b> — the LLM's job description. Critical line: <i>Answer ONLY using the context</i> — this is what stops hallucination."))
    S.append(B("<b>HumanMessage / SystemMessage</b> — LangChain's way of building the chat messages sent to Groq."))
    S.append(B("<b>_get_llm() / _get_embeddings()</b> — lazy singletons: models are created once on first use, not at import time."))
    S.append(B("<b>temperature=0.2</b> — low creativity so answers stay factual and consistent."))
    S.append(B("<b>embed_text()</b> — runs sentence-transformers on CPU and returns a normalized 384-float vector."))
    S.append(B("<b>Return value</b> — a tuple (answer_text, sources_text, seconds_taken) so the UI can show timing + source file."))

    # --- ingest.py ---
    S.append(P("2.3 ingest.py — Teaching the Bot New Knowledge", "H2x"))
    S.append(P(
        "<b>What it does:</b> Turns a raw PDF/TXT into searchable vector rows in MySQL. "
        "This is the <i>indexing</i> step of RAG — done once when we add a document, "
        "not on every chat message.",
        "Bodyx",
    ))
    S.append(code(
"""def ingest_pdf(path):
    # 1) LOAD — read raw text
    if path.lower().endswith(".pdf"):
        raw_docs = PyPDFLoader(path).load()
    else:
        raw_docs = TextLoader(path, encoding="utf-8").load()

    # 2) SPLIT — ~800 char chunks, 100 char overlap
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=100)
    pieces = splitter.split_documents(raw_docs)

    # 3) EMBED each piece  4) STORE into MySQL `chunks`
    items = [{"content": d.page_content,
              "source": d.metadata["source"],
              "embedding": embed_text(d.page_content)} for d in pieces]
    return add_chunks(items)   # INSERT into chunks table"""
    ))
    S.append(B("<b>LOAD</b> — PyPDFLoader extracts text page-by-page from a PDF; TextLoader reads a plain .txt file."))
    S.append(B("<b>SPLIT (chunking)</b> — models work better on small pieces. 800 characters is about one short paragraph/section."))
    S.append(B("<b>chunk_overlap=100</b> — consecutive chunks share 100 characters so a sentence cut in half is not lost."))
    S.append(B("<b>embed_text()</b> — each chunk becomes a 384-float vector via all-MiniLM-L6-v2 (local CPU)."))
    S.append(B("<b>add_chunks()</b> — database.py INSERTs content + source + JSON embedding into MySQL `chunks` (or appends to local_data.json)."))
    S.append(B("<b>CLI mode</b> — <font face='Courier'>python ingest.py knowledge_base.txt</font> works from the terminal for batch loading."))
    S.append(P(
        "Analogy: ingest.py is like filing each page of a textbook into a MySQL cabinet "
        "with a numeric fingerprint (embedding) so retrieval can find the right page later.",
        "Callout",
    ))

    # --- database.py ---
    S.append(P("2.4 database.py — MySQL (4 tables) + JSON Fallback", "H2x"))
    S.append(P(
        "<b>What it does:</b> Every database operation lives here. Four tables: "
        "<b>chunks</b> (knowledge text + embedding vector — replaces Chroma), "
        "<b>documents</b> (what we ingested), <b>chat_logs</b> (every Q&amp;A), "
        "<b>feedback</b> (thumbs up/down). If MySQL is not configured or fails, "
        "everything writes to local_data.json so the demo never crashes.",
        "Bodyx",
    ))
    S.append(code(
"""CREATE TABLE chunks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content   TEXT,          -- the raw text chunk
    source    VARCHAR(255),  -- which file it came from
    embedding LONGTEXT,      -- JSON array of 384 floats
    added_at  DATETIME
);

def add_chunks(items):
    # MySQL: INSERT content, source, JSON.stringify(embedding)
    # fallback: append dicts into local_data.json["chunks"]

def get_all_chunks():
    # SELECT ... FROM chunks  ->  list of dicts with embedding as list[float]

def log_chat(...):
    # INSERT INTO chat_logs ...; return LAST_INSERT_ID()"""
    ))
    S.append(B("<b>chunks table</b> — the vector store itself. embedding column holds a JSON array like [0.02, -0.11, ...]."))
    S.append(B("<b>add_chunks / get_all_chunks / count_chunks</b> — write and read the knowledge base for RAG."))
    S.append(B("<b>_connect()</b> — returns a pymysql connection or None. None means \"use local JSON instead\"."))
    S.append(B("<b>setup_tables()</b> — CREATE TABLE IF NOT EXISTS for all 4 tables; run once at startup from app.py."))
    S.append(B("<b>DictCursor</b> — makes each row a Python dict so we can do row['question'] instead of row[0]."))
    S.append(B("<b>log_chat()</b> — INSERT one conversation, return its id (used later to attach feedback)."))
    S.append(B("<b>LAST_INSERT_ID()</b> — MySQL function that returns the auto-increment id of the row we just inserted."))
    S.append(B("<b>Parameterized queries (%s)</b> — user text is never pasted into SQL strings, which prevents SQL injection."))
    S.append(B("<b>get_chat_logs / get_documents / get_feedback_logs</b> — SELECT helpers that feed the Admin tables (feedback LEFT JOINs the question)."))
    S.append(B("<b>local_data.json fallback</b> — same 4 keys as the tables so the app works with MySQL off."))

    # --- app.py ---
    S.append(P("2.5 app.py — The Whole User Interface", "H2x"))
    S.append(P(
        "<b>What it does:</b> Builds the website with Streamlit. Sidebar has a radio button "
        "to switch between two pages: Chat (students) and Admin (password-protected upload "
        "+ all data shown as tabular dataframes).",
        "Bodyx",
    ))
    S.append(P("Page setup + sidebar:", "H3x"))
    S.append(code(
"""import streamlit as st
st.set_page_config(page_title="CollegeBot", page_icon="🎓", layout="wide")

db_status = setup_tables()   # create MySQL tables once, show status

with st.sidebar:
    st.title("🎓 CollegeBot")
    st.text(f"Database: {db_status}")
    page = st.radio("Go to", ["💬 Chat", "🔐 Admin"])"""
    ))
    S.append(P("Chat page — the main loop:", "H3x"))
    S.append(code(
"""if page == "💬 Chat":
    if "messages" not in st.session_state:
        st.session_state.messages = []      # memory between reruns

    for m in st.session_state.messages:     # redraw old messages
        with st.chat_message(m["role"]):
            st.markdown(m["text"])

    user_q = st.chat_input("Type your question here…")
    if user_q:
        st.session_state.messages.append({"role": "user", "text": user_q})
        answer, sources, secs = ask(user_q)   # <-- calls rag.py
        st.session_state.messages.append(
            {"role": "assistant", "text": answer})
        log_chat(user_q, answer, sources, secs)  # <-- saves to MySQL
        # then show thumbs up / thumbs down buttons"""
    ))
    S.append(B("<b>st.session_state</b> — Streamlit's memory. Streamlit re-runs the whole script on every click; session_state keeps chat history alive."))
    S.append(B("<b>st.chat_message / st.chat_input</b> — built-in chat bubbles and the bottom text box."))
    S.append(B("<b>ask(user_q)</b> — one call into rag.py returns (answer, sources, seconds)."))
    S.append(B("<b>try/except around ask()</b> — if the API key is missing or Groq errors, we show a warning instead of a red crash screen."))
    S.append(B("<b>log_chat + log_feedback</b> — persistence layer (MySQL or JSON)."))
    S.append(P("Admin page (password gate):", "H3x"))
    S.append(code(
"""if not st.session_state.admin_ok:
    pw = st.text_input("Enter admin password", type="password")
    if st.button("Login"):
        if pw == ADMIN_PASSWORD:
            st.session_state.admin_ok = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()   # nothing below runs until login succeeds"""
    ))
    S.append(B("<b>type=\"password\"</b> — masks the input as dots."))
    S.append(B("<b>st.stop()</b> — hard stop: the rest of the Admin page is invisible until the password is correct."))
    S.append(B("<b>File uploader</b> — saves the uploaded PDF to uploads/, calls ingest_pdf(), then log_document()."))
    S.append(B("<b>Auto-ingest at startup</b> — if count_chunks()==0 and knowledge_base.txt exists, load it once (fresh cloud deploys)."))
    S.append(P("Admin data as TABLES (the part ma'am will like):", "H3x"))
    S.append(code(
"""tab_chats, tab_docs, tab_fb, tab_chunks = st.tabs(
    ["Chat logs", "Documents", "Feedback", "Chunks"])

st.dataframe(rows, use_container_width=True)  # proper table UI
# Feedback tab: LEFT JOIN feedback with chat_logs to show the question
# Chunks tab: id, source, chars, embedding dim, text preview
# (full 384-float vectors stay in MySQL, not dumped into the UI)"""
    ))
    S.append(B("<b>st.tabs</b> — four sections on one Admin page without scrolling forever."))
    S.append(B("<b>st.dataframe</b> — sortable, scrollable table (not expanders). Columns: ID, question, answer, sources, seconds, timestamp."))
    S.append(B("<b>Metrics row</b> — chunks in DB, documents ingested, chats logged."))
    S.append(B("<b>Feedback join</b> — get_feedback_logs() LEFT JOINs so each rating shows which question it was for."))

    # --- knowledge base ---
    S.append(P("2.6 knowledge_base.txt — The Demo Data (39 lines)", "H2x"))
    S.append(P(
        "Plain text file with facts about a fictional <b>Sunrise College of Engineering</b>: "
        "admissions, fees (tuition 85,000 / hostel 45,000), library (8 AM–8 PM), hostel rules, "
        "exams (75% attendance), and contact info. This is the only knowledge the bot has "
        "until an admin uploads more PDFs. Every answer cites this file as its source.",
        "Bodyx",
    ))

    # --- requirements ---
    S.append(P("2.7 requirements.txt — Exact Dependencies (19 lines)", "H2x"))
    S.append(code(
"""--extra-index-url https://download.pytorch.org/whl/cpu
torch==2.14.0+cpu          # CPU-only torch (smaller, free-tier friendly)

streamlit==1.40.0          # web UI
langchain==0.3.7           # RAG framework
langchain-core==0.3.27     # must match langchain version (compat)
langchain-groq==0.2.1      # Groq LLM wrapper
sentence-transformers==3.3.1   # local embeddings
langchain-huggingface==0.1.2   # HF embeddings integration
pypdf==5.1.0               # PDF reader
pymysql==1.1.1             # MySQL driver (vector store + logs)
python-dotenv==1.0.1       # loads .env
gunicorn==23.0.0           # production WSGI server (Render)"""
    ))
    S.append(B("Pinned versions (=) so the same code runs on our laptop and on the cloud."))
    S.append(B("CPU torch avoids downloading the huge CUDA/GPU build — free hosts only have CPU."))
    S.append(B("No chromadb — vectors live in MySQL `chunks` (JSON fallback)."))
    S.append(B("langchain-core must be compatible with langchain; a mismatch is the #1 install failure."))

    # --- gitignore / env ---
    S.append(P("2.8 .env, .env.example, .gitignore — Secret Safety", "H2x"))
    S.append(P(
        "<b>.env</b> holds the real GROQ key and admin password. <b>.env.example</b> is a "
        "safe template with placeholders, committed to GitHub so others know what to fill in. "
        "<b>.gitignore</b> excludes .env, venv/, __pycache__/, local_data.json, and uploads/ "
        "so secrets and junk never hit the repo. Vectors are not committed — they live in "
        "MySQL (or local_data.json) and are rebuilt by ingest / first-run auto-ingest.",
        "Bodyx",
    ))

    S.append(PageBreak())

    # ========== PART 3: GLOSSARY ==========
    S.append(P("Part 3 — Glossary (Every Technical Term, Plain English)", "H1x"))
    terms = [
        ("RAG (Retrieval Augmented Generation)",
         "Search your own documents first, then let the LLM write an answer using those documents as open-book notes. Reduces hallucination."),
        ("LLM (Large Language Model)",
         "A big neural network trained to predict text (ChatGPT-style). Here we call one through Groq's API instead of hosting it ourselves."),
        ("Embedding",
         "A list of numbers (vector) that represents the meaning of a sentence. Similar meaning = nearby points in that number space. Our model outputs 384 numbers per chunk."),
        ("Vector store (MySQL chunks)",
         "Table `chunks` holds text + source + embedding (JSON array of floats). Retrieval loads rows and ranks them by cosine similarity in Python."),
        ("Similarity search",
         "Given a query vector, score every stored vector by cosine similarity and return the top k. We use k=3."),
        ("Chunking",
         "Splitting a long document into ~800-character pieces so retrieval is precise and embeddings stay meaningful."),
        ("Prompt / System prompt",
         "The text sent to the LLM. System prompt sets rules (answer only from context); Human message is the user's question."),
        ("Temperature",
         "How creative/random the LLM is. 0 = very factual, 1 = wild. We use 0.2 for a student-helper tone."),
        ("Hallucination",
         "When an LLM invents confident-sounding facts. Our guard: 'Answer ONLY using the context' + refuse if missing."),
        ("Streamlit rerun model",
         "Every interaction re-executes app.py from top to bottom. st.session_state is how we keep state between reruns."),
        ("session_state",
         "A dict owned by Streamlit for the current browser session — holds chat history and admin login flag."),
        ("Lazy initialization",
         "Create heavy objects (models) only when first needed. Our _get_llm() / _get_embeddings() use this pattern."),
        ("Environment variable / secrets",
         "Key-value settings outside the source code. Read via os.getenv or st.secrets so keys are not committed to git."),
        ("SQL injection",
         "Attack where user text becomes executable SQL. Prevented by parameterized queries with %s placeholders."),
        ("MySQL tables",
         "documents = files ingested; chat_logs = every Q&A; feedback = thumbs up/down linked by chat_id."),
        ("JSON fallback",
         "If MySQL is off, data goes to local_data.json with the same structure so the app still works offline."),
        ("PyPDFLoader",
         "LangChain loader that extracts text from each page of a PDF into Document objects."),
        ("RecursiveCharacterTextSplitter",
         "Splits text by characters first, then tries paragraph/newline boundaries so cuts land on natural breaks."),
        ("Groq",
         "Free API platform that serves open models at very high speed. We authenticate with GROQ_API_KEY."),
        ("Deployment",
         "Putting the app on a public server. We pushed to GitHub and Streamlit Community Cloud runs streamlit run app.py for us."),
        (".gitignore",
         "List of paths git must never track (secrets, virtualenvs, caches)."),
        ("Virtual environment (venv)",
         "A private Python install folder for this project so packages don't clash with other projects."),
    ]
    for name, defn in terms:
        S.append(Paragraph(sanitize(f"<b>{escape(name)}</b> - {escape(defn)}"), styles["Bulletx"], bulletText="-"))

    S.append(PageBreak())

    # ========== PART 4: Q&A ==========
    S.append(P("Part 4 — Viva / Presentation Q&amp;A Bank", "H1x"))
    S.append(P(
        "These are the questions ma'am is most likely to ask. Answers are written so you can "
        "read them almost verbatim. Practice the bolded ones first.",
        "Bodyx",
    ))

    S.append(P("Concept questions", "H2x"))
    for q, a in [
        ("What is RAG and why did you use it instead of fine-tuning?",
         "RAG means Retrieval Augmented Generation. Instead of retraining the model, we fetch the 3 most relevant chunks from our college knowledge base and paste them into the prompt as context. The LLM then answers from that context. It is cheaper than fine-tuning, updates instantly when we change the notes, and lets us show the source of every answer."),
        ("Explain the three steps of your RAG pipeline.",
         "1) RETRIEVE: embed the user question, load MySQL `chunks`, cosine-rank, keep top 3. 2) AUGMENT: join those three chunks into one context string and place it inside a system prompt. 3) GENERATE: send the prompt to the Groq LLM and return its answer, the source filenames, and the time taken."),
        ("What is an embedding? Which model do you use?",
         "An embedding is a fixed-length list of numbers that encodes meaning so similar sentences sit close together in vector space. We use the sentence-transformers model all-MiniLM-L6-v2, which runs locally on CPU and produces 384-dimensional vectors. It needs no API key."),
        ("Why local embeddings instead of an API like OpenAI or Gemini embeddings?",
         "Local embeddings are free, work offline, keep data on our machine, and avoid a second API key. The model is only about 80MB and downloads once to the Hugging Face cache."),
        ("What is Chroma / where did it go?",
         "We originally used Chroma as the vector DB. Now vectors live in the MySQL table `chunks` (content, source, embedding as JSON). Cosine similarity is computed in Python after loading rows. If MySQL is off, local_data.json stores the same structure."),
        ("Why k=3 for retrieval? What happens if k is larger or smaller?",
         "k=3 gives enough context for a short factual answer without flooding the prompt. Smaller k may miss the fact; larger k costs more tokens, can add noise, and may confuse the model. It is a tunable hyperparameter."),
        ("How is the vector stored in MySQL?",
         "The chunks.embedding column is LONGTEXT holding a JSON array of 384 floats produced by all-MiniLM-L6-v2. On query we parse the JSON, compute cosine similarity with the question embedding, and take the top 3 rows."),
        ("How do you prevent the chatbot from hallucinating?",
         "The system prompt says Answer ONLY using the context and to reply 'I don't have that in my knowledge base yet' if the answer is missing. Temperature is low (0.2). We also display the sources under each answer so users can verify."),
        ("What is the role of LangChain in this project?",
         "LangChain is the orchestration framework. It provides document loaders, text splitters, chat message types, and the ChatGroq client so we can wire retrieval and generation with a few lines instead of writing everything from scratch."),
        ("What is Groq and which model are you calling?",
         "Groq is a free high-speed API for open LLMs. We call model openai/gpt-oss-120b with temperature 0.2 through the langchain-groq ChatGroq class, authenticated by GROQ_API_KEY."),
        ("How does Streamlit work under the hood?",
         "Streamlit reruns the entire Python script whenever the user interacts (types, clicks). st.session_state preserves data between reruns — that is how our chat history and admin login survive."),
    ]:
        S.extend(qa(q, a))

    S.append(P("Database questions", "H2x"))
    for q, a in [
        ("What tables are in your MySQL database?",
         "Four tables: chunks (knowledge text + JSON embedding vector), documents (filename, chunks, added_at), chat_logs (question, answer, sources, seconds, asked_at), and feedback (chat_id, rating, given_at) linked to a chat row."),
        ("Show how you insert a chat into MySQL.",
         "log_chat() uses a parameterized INSERT: INSERT INTO chat_logs (question, answer, sources, seconds, asked_at) VALUES (%s,%s,%s,%s,%s), then SELECT LAST_INSERT_ID() to get the new row id for feedback."),
        ("What if MySQL is down during the demo?",
         "database.py detects a failed or missing connection and falls back to local_data.json with the same data shape. The sidebar shows 'MySQL OFF (local JSON mode)' instead of crashing."),
        ("How do you avoid SQL injection?",
         "Every query uses pymysql placeholders (%s) with values passed separately. User text is never concatenated into the SQL string."),
        ("What is the use of feedback table?",
         "It stores which chat got a thumbs up or down (chat_id + rating). Over time this shows which answers were helpful and can drive improvements."),
        ("How would you show live chat logs to ma'am?",
         "Open the Admin page, enter the password, and open the Chat logs tab — a sortable dataframe with ID, question, answer, sources, seconds, and timestamp. Under the hood it is SELECT ... ORDER BY id DESC LIMIT 50."),
    ]:
        S.extend(qa(q, a))

    S.append(P("Architecture &amp; deployment questions", "H2x"))
    for q, a in [
        ("Walk me through what happens when a user asks a question.",
         "app.py captures the chat_input string, appends it to session_state, calls rag.py ask(). ask() loads all chunks from MySQL, embeds the question, cosine-ranks, builds the system+human messages with the top 3, invokes Groq, and returns answer/sources/seconds. app.py renders the bubble, logs the row in database.py, and shows feedback buttons."),
        ("Where is the knowledge base loaded from? What if it is empty?",
         "From the MySQL chunks table (or local_data.json if MySQL is off). On startup, if count_chunks() is 0 and knowledge_base.txt exists, app.py auto-ingests it once. On the Admin page you can upload any PDF, which is chunked and inserted the same way."),
        ("How is the project deployed?",
         "Source is on GitHub (dhyey-gosa/college-chatbot). Streamlit Community Cloud connects to that repo, installs requirements.txt, and runs streamlit run app.py. Secrets (GROQ_API_KEY, ADMIN_PASSWORD) are pasted into the app's Secrets settings as TOML. Live URL: https://chatbot-mem.streamlit.app/."),
        ("Why didn't you hard-code the API key in the source?",
         "Hard-coding keys in git leaks them to anyone with repo access. We use .env locally (gitignored) and Streamlit secrets in the cloud. config.py reads env first, then st.secrets."),
        ("What is in requirements.txt and why pin versions?",
         "It is the exact dependency list for pip install -r requirements.txt. Pinning (=) prevents 'works on my machine' bugs — Streamlit Cloud must install the same versions we tested."),
        ("Explain chunk_size=800 and chunk_overlap=100.",
         "Each piece of text stored is about 800 characters. Adjacent pieces share 100 characters so a sentence split across a boundary still appears fully in at least one chunk, improving recall."),
        ("How would you scale this to 10,000 documents?",
         "Add an ANN index path (or move vectors to a dedicated vector DB / MySQL 9 VECTOR type), index chunks by department metadata, use hybrid keyword+vector search, batch embeddings, and put the Groq call behind a queue. Also switch MySQL to a managed instance with connection pooling."),
        ("What are the limitations of your current system?",
         "Only top-3 chunks are used so multi-hop questions may be incomplete; answers are limited to the knowledge base (no web search); feedback is stored but not yet used for training; free hosting can sleep when idle; embeddings are English-focused."),
        ("How do you evaluate answer quality?",
         "Manual spot-checks against knowledge_base.txt, response time shown under each answer (e.g. 0.68s), source attribution for verifiability, and 👍/👎 feedback counts in the feedback table. A future step is an automated faithfulness score (does every claim appear in the retrieved chunks?)."),
        ("Is this secure?",
         "Secrets stay out of git; Admin page uses a password gate; SQL uses parameterized queries; HTTPS is provided by the host. For production we would add proper auth (SSO), rate limiting, and server-side session expiry — the current gate is demo-grade."),
    ]:
        S.extend(qa(q, a))

    S.append(P("Code-specific questions (they may open a file)", "H2x"))
    for q, a in [
        ("What does lazy loading mean in rag.py?",
         "_llm and _embeddings start as None. _get_llm() and _get_embeddings() create the real objects only on the first call and reuse them after. Benefits: app starts faster, and a missing API key raises a clear RuntimeError instead of crashing at import time."),
        ("Why store embeddings as JSON in MySQL instead of a separate vector DB?",
         "For a college demo the corpus is tiny (a few dozen chunks). Loading rows and computing cosine in Python is simple, uses one database we already need for chat logs, and shows ma'am real SQL tables on the Admin page — no extra infrastructure."),
        ("What does st.stop() do on the Admin page?",
         "It halts the rest of the script for this rerun. Used after the password form so the upload UI and chat logs never render for a logged-out user."),
        ("Why try/except around ask() in app.py?",
         "So a missing key or API outage shows a friendly warning bubble instead of a full-page Streamlit exception. Keeps the demo alive when something external fails."),
        ("Why is .env not committed while demo data can be rebuilt?",
         ".env holds the live API key and must never be public. Knowledge-base vectors are not secret — we rebuild them with python ingest.py knowledge_base.txt or first-run auto-ingest. Chat history persists in MySQL when DB_* is configured."),
    ]:
        S.extend(qa(q, a))

    S.append(PageBreak())

    # ========== PART 5: DEMO SCRIPT ==========
    S.append(P("Part 5 — Live Demo Script (Follow This Click-by-Click)", "H1x"))
    S.append(P(
        "Open https://chatbot-mem.streamlit.app/ in a browser <b>before</b> the class "
        "(first load can take ~30s while the app wakes up). Keep this tab ready.",
        "Warn",
    ))

    S.append(P("Opening line (30 seconds)", "H2x"))
    S.append(P(
        "\"This is CollegeBot, a RAG-based chatbot for college FAQs. Instead of blindly "
        "trusting an LLM, it first retrieves the three most relevant lines from our "
        "knowledge base, then generates an answer from them, shows the source file, "
        "and logs everything into a database.\"",
        "Callout",
    ))

    S.append(P("Demo steps", "H2x"))
    steps = [
        "Point at the sidebar: app name, Database status (MySQL OFF / connected), and the Chat/Admin switch.",
        "Ask: <b>What are the college fees?</b> — wait for the answer (usually under 1 second).",
        "Highlight: correct figures (85,000 / 45,000), the <b>sources: knowledge_base.txt</b> line, and the response time.",
        "Click <b>👍 Helpful</b> — explain this writes a row into the feedback table (or JSON fallback).",
        "Ask a second question from a different section, e.g. <b>What are the library timings?</b>",
        "Ask an out-of-scope question, e.g. <b>What is the stock price of Reliance?</b> — bot should refuse: not in knowledge base. This proves the hallucination guard.",
        "Switch to <b>🔐 Admin</b>, password <b>college123</b>.",
        "Show the four Admin tabs as tables: Chat logs, Documents, Feedback, Chunks (st.dataframe).",
        "(Optional) Upload a small PDF and re-check the chunk count increases.",
        "Close with the architecture line from Part 1.2 and invite questions from Part 4.",
    ]
    for i, s in enumerate(steps, 1):
        S.append(Paragraph(sanitize(f"<b>Step {i}.</b> {s}"), styles["Bulletx"], bulletText=">"))

    S.append(P("Backup if the live site is slow", "H2x"))
    S.append(code(
"""# run locally on the laptop
cd college-chatbot
venv\\Scripts\\activate
streamlit run app.py
# open http://localhost:8501"""
    ))
    S.append(P(
        "Local run uses the same code and the same knowledge base. Have the terminal "
        "pre-started as a fallback.",
        "Bodyx",
    ))

    S.append(P("Likely last-minute questions (one-line answers)", "H2x"))
    for q, a in [
        ("Is this using ChatGPT?", "No. It calls a Groq-hosted open model (gpt-oss-120b) through an API, grounded by our RAG pipeline."),
        ("Is the data going to Google/OpenAI?",
         "Retrieval is fully local/MySQL: embeddings via sentence-transformers on our machine, ranking in Python/SQL. Only the final prompt (context + question) is sent to Groq to generate text."),
        ("Can anyone become admin?", "Only if they know ADMIN_PASSWORD. It is a demo gate; production would use real auth."),
        ("What happens if you add a new PDF?", "Admin upload -> ingest.py chunks and embeds it -> new rows appear in the MySQL chunks table -> the next question can retrieve from that PDF. Source name shows under the answer."),
        ("Why is everything in one MySQL database?", "One system for both operational data (chat_logs, documents, feedback) and the vector store (chunks). Admin page shows all four as tables; JSON file is only the offline fallback."),
        ("What is the accuracy?", "Within the knowledge base, answers match the source facts exactly (verified live: fee question returned 85,000 / 45,000 / 15 Aug 2026). Outside the KB it refuses instead of guessing."),
    ]:
        S.extend(qa(q, a))

    S.append(Spacer(1, 12))
    S.append(P(
        "End of guide. Source code: GitHub dhyey-gosa/college-chatbot. "
        "Live app: https://chatbot-mem.streamlit.app/. "
        "Admin password is in .env / Streamlit secrets (default demo: college123).",
        "Callout",
    ))

    doc.build(S)
    print("Wrote", OUT)


if __name__ == "__main__":
    build()
