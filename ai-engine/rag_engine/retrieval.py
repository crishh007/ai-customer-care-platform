import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend", "chroma_db")

class RAGRetriever:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        env = os.getenv("NODE_ENV", "development")
        
        if env == "production":
            try:
                from langchain_pinecone import PineconeVectorStore
                index_name = os.getenv("PINECONE_INDEX", "ai-customer-care")
                self.db = PineconeVectorStore(index_name=index_name, embedding=self.embeddings)
                self.retriever = self.db.as_retriever(search_kwargs={"k": 3})
            except ImportError:
                print("Pinecone not found, falling back to Chroma.")
                self._init_chroma()
        else:
            self._init_chroma()

    def _init_chroma(self):
        if not os.path.exists(CHROMA_DB_DIR):
            print(f"Warning: ChromaDB directory {CHROMA_DB_DIR} not found. RAG may return empty results.")
        self.db = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=self.embeddings)
        self.retriever = self.db.as_retriever(search_kwargs={"k": 3})

    def retrieve_context(self, query: str) -> str:
        """
        Retrieves relevant documents for the given query and formats them as a context string.
        """
        docs = self.retriever.invoke(query)
        if not docs:
            return ""
        
        # Combine the page content of the retrieved documents
        context_parts = [f"[{i+1}] {doc.page_content}" for i, doc in enumerate(docs)]
        return "\n\n".join(context_parts)

# Singleton instance for easy import
rag_retriever = None

def get_rag_retriever() -> RAGRetriever:
    global rag_retriever
    if rag_retriever is None:
        rag_retriever = RAGRetriever()
    return rag_retriever
