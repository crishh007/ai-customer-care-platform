# ASSIGNED TO: AI-4 (implemented to support AI-1 integration)
# RAG Retrieval Module
# Purpose: Given a user query, find the top-k most relevant document chunks

import os
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from dotenv import load_dotenv

# Load environment variables relative to current file and backend directory
load_dotenv()
# Also search in backend folder for .env if run from backend folder
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/.env")))

def get_chroma_client():
    """Initialises and returns a persistent ChromaDB client."""
    chroma_host = os.getenv("CHROMA_HOST", None)
    chroma_port = os.getenv("CHROMA_PORT", None)
    chroma_db_dir = os.getenv("CHROMA_DB_DIR") or "chroma_db"
    
    if not os.path.isabs(chroma_db_dir):
        # Resolve relative to the backend/ directory (where the database should live)
        chroma_db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend", chroma_db_dir))

    if chroma_host:
        port = int(chroma_port) if chroma_port else 8000
        return chromadb.HttpClient(host=chroma_host, port=port)
    else:
        os.makedirs(chroma_db_dir, exist_ok=True)
        return chromadb.PersistentClient(path=chroma_db_dir)

def get_collection():
    """Retrieves or creates the target vector collection using DefaultEmbeddingFunction."""
    client = get_chroma_client()
    collection_name = os.getenv("CHROMA_COLLECTION_NAME", "customer_care_docs")
    # DefaultEmbeddingFunction runs sentence-transformers (all-MiniLM-L6-v2) locally
    embedding_function = DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )

def retrieve(query: str, top_k: int = 3) -> list[str]:
    """Embeds the query, runs similarity search, and returns the top_k matching chunks."""
    try:
        collection = get_collection()
        if collection.count() == 0:
            return []
            
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        if results and "documents" in results and results["documents"]:
            return results["documents"][0]
        return []
    except Exception as e:
        print(f"[RAG-Error] Query similarity search failed: {e}")
        return []

def generate_response(query: str, chunks: list) -> dict:
    """Mock answer generator to be overridden/called if direct answering is requested."""
    context = "\n\n".join(chunks) if chunks else "No relevant context found."
    answer = f"Retrieved context: {context}"
    return {
        "answer": answer,
        "confidence": 0.9 if chunks else 0.4,
        "sources": []
    }

if __name__ == "__main__":
    # Test retrieval
    results = retrieve("What is your refund policy?")
    print("Test retrieve results:", results)
