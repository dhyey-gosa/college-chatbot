"""
rag.py — the BRAIN of the chatbot. This is the RAG pipeline.

RAG = Retrieval Augmented Generation. In plain words:

  1. RETRIEVE : search our knowledge base for the 3 most relevant chunks
  2. AUGMENT  : paste those chunks into the LLM's prompt as context
  3. GENERATE : the LLM answers using that context (so it doesn't make stuff up)

If the LLM is a student writing an open-book exam, the retrieved chunks
are the book pages. That's the whole idea.
"""
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from config import (CHROMA_DIR, EMBED_MODEL, GROQ_API_KEY, LLM_MODEL)

# ---------- The two AI models ----------
# LLM: Groq API (needs GROQ_API_KEY)
# Embeddings: sentence-transformers runs LOCALLY — no API key, no Google.
# Both built lazily so a missing key shows a clear error instead of a crash.
_llm = None
_embeddings = None


def _require(key_value, name, where):
    if not key_value or key_value.startswith("paste_"):
        raise RuntimeError(
            f"{name} is missing. Add it to .env (or the Render dashboard) — get it from {where}"
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
        # First call downloads the model (~80MB) into ~/.cache/huggingface — one time only.
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


# ---------- The system prompt (personality + rules for the bot) ----------
SYSTEM_PROMPT = """You are CollegeBot, a helpful assistant for college students.
Answer ONLY using the context below. If the answer is not in the context,
say politely: "I don't have that in my knowledge base yet."
Keep answers short and friendly (max 5 sentences).

CONTEXT:
{context}
"""


def load_vectorstore():
    """Open the Chroma vector database stored in the chroma_db folder."""
    return Chroma(persist_directory=CHROMA_DIR, embedding_function=_get_embeddings())


def ask(question):
    """
    The full RAG flow for ONE question.
    Returns (answer_text, sources_text, seconds_taken).
    """
    import time
    start = time.time()

    db = load_vectorstore()

    # STEP 1: RETRIEVE — find the 3 most similar chunks from the knowledge base
    # (Chroma compares the question's embedding with every chunk's embedding)
    if db._collection.count() == 0:   # knowledge base is empty
        return ("My knowledge base is empty. Please upload a PDF on the Admin page.",
                "", 0)
    docs = db.similarity_search(question, k=3)

    # STEP 2: AUGMENT — glue the retrieved chunks into one text block
    context = "\n\n".join(d.page_content for d in docs)
    sources = ", ".join(sorted({d.metadata.get("source", "?") for d in docs}))

    # STEP 3: GENERATE — the LLM answers using only our context
    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(context=context)),
        HumanMessage(content=question),
    ]
    answer = _get_llm().invoke(messages).content

    return answer, sources, round(time.time() - start, 2)
