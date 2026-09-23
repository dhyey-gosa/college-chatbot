"""
ingest.py — teaches the bot new knowledge (writes into MySQL `chunks`).

Pipeline:
  1) LOAD   — read PDF/TXT
  2) SPLIT  — cut into ~800 char pieces (100 overlap)
  3) EMBED  — sentence-transformers -> list of 384 numbers
  4) STORE  — INSERT into MySQL chunks table (or local_data.json)

Run:  python ingest.py knowledge_base.txt
"""
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from database import add_chunks
from rag import embed_text


def ingest_pdf(path):
    """
    Load a file -> split -> embed -> save into MySQL chunks table.
    Returns how many chunks were added.
    """
    # 1) LOAD
    if path.lower().endswith(".pdf"):
        raw_docs = PyPDFLoader(path).load()
    else:
        raw_docs = TextLoader(path, encoding="utf-8").load()

    # 2) SPLIT
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )
    pieces = splitter.split_documents(raw_docs)

    # 3) EMBED + 4) STORE
    items = []
    for doc in pieces:
        text = doc.page_content or ""
        if not text.strip():
            continue
        source = (doc.metadata or {}).get("source") or path.split("/")[-1].split("\\")[-1]
        items.append({
            "content": text,
            "source": source,
            "embedding": embed_text(text),
        })

    return add_chunks(items)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        n = ingest_pdf(sys.argv[1])
        print(f"[OK] Ingested {n} chunks from {sys.argv[1]}")
    else:
        print("Usage: python ingest.py yourfile.pdf")
