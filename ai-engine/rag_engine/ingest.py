import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configuration
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend", "chroma_db")

def ingest_documents():
    """
    Loads FAQ texts, splits them into chunks, and ingests them into ChromaDB.
    """
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        os.makedirs(KNOWLEDGE_BASE_DIR)
        
    faq_path = os.path.join(KNOWLEDGE_BASE_DIR, "faq.txt")
    if not os.path.exists(faq_path):
        # Create a dummy faq file for testing
        with open(faq_path, "w") as f:
            f.write("Q: What is your refund policy?\nA: We offer a 30-day money-back guarantee.\n\n")
            f.write("Q: How long does shipping take?\nA: Standard shipping takes 3-5 business days.\n\n")
            f.write("Q: Can I change my subscription?\nA: Yes, you can upgrade or downgrade at any time from your dashboard.\n")
        print(f"Created sample FAQ file at {faq_path}")

    print("Loading documents...")
    loader = TextLoader(faq_path)
    documents = loader.load()

    print("Splitting documents...")
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separator="\n\n")
    docs = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    env = os.getenv("NODE_ENV", "development")
    if env == "production":
        print("Production environment detected. Ingesting to Pinecone...")
        try:
            from langchain_pinecone import PineconeVectorStore
            import pinecone
            pinecone_api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX", "ai-customer-care")
            
            # This requires 'pinecone-client' and 'langchain-pinecone' to be installed
            PineconeVectorStore.from_documents(docs, embeddings, index_name=index_name)
            print("Pinecone ingestion complete.")
        except ImportError:
            print("Pinecone packages not found. Falling back to ChromaDB.")
            db = Chroma.from_documents(docs, embeddings, persist_directory=CHROMA_DB_DIR)
            db.persist()
    else:
        print(f"Creating embeddings and storing in ChromaDB at {CHROMA_DB_DIR}...")
        db = Chroma.from_documents(docs, embeddings, persist_directory=CHROMA_DB_DIR)
        db.persist()
        print("Ingestion complete.")

if __name__ == "__main__":
    print("Notice: Not using OpenAI embeddings anymore.")
    ingest_documents()
