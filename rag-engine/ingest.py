# ASSIGNED TO: AI-4 (implemented to support AI-1 integration)
# Knowledge Base Ingestion Script
# Purpose: Load documents → Chunk → Embed → Store in vector DB

import os
import sys
from dotenv import load_dotenv

# Allow importing from current directory when running this script directly
sys.path.insert(0, os.path.dirname(__file__))

from retrieval import get_chroma_client, get_collection

# Load environment variables
load_dotenv()
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/.env")))

def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Splits text into overlapping chunks using paragraph boundaries."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if current_chunk and len(current_chunk) + len(para) + 2 > chunk_size:
            chunks.append(current_chunk.strip())
            current_chunk = current_chunk[-overlap:] + "\n\n" + para if overlap > 0 else para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def ingest_documents() -> int:
    """Loads knowledge base .txt files, chunks them, and upserts them to ChromaDB."""
    print("=============================================")
    print("      Starting Document Ingestion Pipeline    ")
    print("=============================================")

    doc_dir = os.getenv("DOCUMENT_DIR") or "../knowledge-base"
    if not os.path.isabs(doc_dir):
        # Resolve relative to the backend/ directory (where the .env resides)
        doc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend", doc_dir))
        
    collection_name = os.getenv("CHROMA_COLLECTION_NAME", "customer_care_docs")

    if not os.path.exists(doc_dir):
        print(f"[Error] Document directory '{doc_dir}' does not exist.")
        return 0

    # Reset collection for a clean ingest
    try:
        client = get_chroma_client()
        collections = [c.name for c in client.list_collections()]
        if collection_name in collections:
            print(f"Resetting existing collection '{collection_name}'...")
            client.delete_collection(collection_name)
    except Exception as e:
        print(f"[Warning] Failed to reset collection: {e}")

    collection = get_collection()

    files = [f for f in os.listdir(doc_dir) if f.endswith(".txt")]
    if not files:
        print(f"[Warning] No text (.txt) files found in directory: '{doc_dir}'")
        return 0

    print(f"Discovered {len(files)} files to ingest.")
    total_chunks = 0

    for filename in files:
        filepath = os.path.join(doc_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()

            chunks = split_text_into_chunks(raw_text)
            if not chunks:
                continue

            ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{"source": filename} for _ in range(len(chunks))]

            collection.upsert(
                ids=ids,
                documents=chunks,
                metadatas=metadatas
            )
            total_chunks += len(chunks)
            print(f"[✓] Successfully ingested {len(chunks)} chunks from '{filename}'")
        except Exception as e:
            print(f"[Error] Failed to ingest '{filename}': {e}")

    print("=============================================")
    print(f"  Ingestion Complete! Total chunks: {total_chunks}   ")
    print("=============================================")
    return total_chunks

if __name__ == "__main__":
    ingest_documents()
