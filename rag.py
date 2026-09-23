"""
rag.py — the BRAIN of the chatbot (RAG pipeline).

RAG = Retrieval Augmented Generation:
  1. RETRIEVE : embed the question, cosine-rank all chunks stored in MySQL
                (or local JSON), take the top 3
  2. AUGMENT  : paste those chunks into the LLM prompt as context
  3. GENERATE : the LLM answers using only that context

Vector store is MySQL table `chunks` (embedding = JSON list of floats).
No Chroma. sentence-transformers still runs locally to produce embeddings.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from config import EMBED_MODEL, GROQ_API_KEY, LLM_MODEL
from database import count_chunks, get_all_chunks

_llm = None
_embeddings = None


def _require(key_value, name, where):
    if not key_value or key_value.startswith("paste_"):
        raise RuntimeError(
            f"{name} is missing. Add it to .env (or host secrets) — get it from {where}"
        )
    return key_value


def _get_llm():
    global _llm
    if _llm is None:
        _require(GROQ_API_KEY, "GROQ_API_KEY", "https://console.groq.com/keys")
        _llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY, temperature=0.2)
    return _llm


def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


SYSTEM_PROMPT = """You are CollegeBot, a helpful assistant for college students.
Answer ONLY using the context below. If the answer is not in the context,
say politely: "I don't have that in my knowledge base yet."
Keep answers short and friendly (max 5 sentences).

CONTEXT:
{context}
"""


def embed_text(text: str):
    """Turn one string into a normalized embedding vector (list of floats)."""
    return list(_get_embeddings().embed_query(text))


def _cosine(a, b):
    """Cosine similarity between two equal-length vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / ((na ** 0.5) * (nb ** 0.5))


def retrieve(question: str, k: int = 3):
    """
    Top-k chunks from MySQL/JSON by cosine similarity.
    Returns list of dicts: {content, source, score}.
    """
    rows = get_all_chunks()
    if not rows:
        return []
    q_vec = embed_text(question)
    scored = []
    for r in rows:
        s = _cosine(q_vec, r.get("embedding") or [])
        scored.append((s, r))
    scored.sort(key=lambda t: t[0], reverse=True)
    out = []
    for s, r in scored[:k]:
        out.append({
            "content": r.get("content") or "",
            "source": r.get("source") or "?",
            "score": round(s, 4),
        })
    return out


def ask(question):
    """
    Full RAG flow for ONE question.
    Returns (answer_text, sources_text, seconds_taken).
    """
    import time
    start = time.time()

    # STEP 1: RETRIEVE from MySQL `chunks` (or local JSON)
    if count_chunks() == 0:
        return (
            "My knowledge base is empty. Please upload a PDF on the Admin page.",
            "",
            0,
        )
    hits = retrieve(question, k=3)

    # STEP 2: AUGMENT — glue retrieved chunks into one context block
    context = "\n\n".join(h["content"] for h in hits)
    sources = ", ".join(sorted({h["source"] for h in hits}))

    # STEP 3: GENERATE — LLM answers using only our context
    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(context=context)),
        HumanMessage(content=question),
    ]
    answer = _get_llm().invoke(messages).content

    return answer, sources, round(time.time() - start, 2)
