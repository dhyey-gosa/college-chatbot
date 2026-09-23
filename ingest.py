"""
ingest.py — teaches the bot new knowledge.

"Chunking" explained simply:
  A PDF can be 50 pages. AI models can't search raw pages well, so we
  1) split the text into small pieces ("chunks" of ~800 characters)
  2) convert each chunk into a list of numbers called an "embedding"
     (similar meanings -> similar numbers)
  3) store those embeddings inside the Chroma vector database

Later, when a user asks something, we embed THEIR question the same way
and Chroma finds the chunks with the most similar numbers. That is the
"Retrieval" in RAG.

Run from terminal:  python ingest.py knowledge_base.txt
"""
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag import load_vectorstore


def ingest_pdf(path):
    """
    Load a PDF -> split into chunks -> embed -> save into Chroma.
    Returns how many chunks were added.
    """
    # 1) LOAD — read the raw text from the file
    if path.lower().endswith(".pdf"):
        raw_docs = PyPDFLoader(path).load()
    else:  # .txt works too
        raw_docs = TextLoader(path, encoding="utf-8").load()

    # 2) SPLIT — cut into ~800-character chunks with 100 overlap
    #    (overlap keeps sentences that span two chunks intact)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )
    chunks = splitter.split_documents(raw_docs)

    # 3) STORE — Chroma embeds each chunk (via our Gemini embeddings)
    #    and saves them in the chroma_db folder
    db = load_vectorstore()
    db.add_documents(chunks)

    return len(chunks)


# Allows: python ingest.py somefile.pdf
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        n = ingest_pdf(sys.argv[1])
        print(f"[OK] Ingested {n} chunks from {sys.argv[1]}")
    else:
        print("Usage: python ingest.py yourfile.pdf")
