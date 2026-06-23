# ASSIGNED TO: AI-1
# LangSmith Monitoring Setup
# Purpose: Track all LLM calls, agent runs, RAG queries for debugging

import os
import logging

logger = logging.getLogger(__name__)

def initialize_monitoring():
    """Configure LangSmith environment variables for automatic tracing."""
    langchain_tracing = os.getenv("LANGCHAIN_TRACING_V2", "false")
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")

    if langchain_tracing.lower() == "true" and langsmith_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
        os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "ai-customer-care")
        logger.info("LangSmith tracing ENABLED for project '%s'", os.environ["LANGSMITH_PROJECT"])
        print(f"LangSmith monitoring initialized for project '{os.environ['LANGSMITH_PROJECT']}'")
    else:
        os.environ.pop("LANGCHAIN_TRACING_V2", None)
        logger.info("LangSmith tracing DISABLED (missing LANGSMITH_API_KEY or LANGCHAIN_TRACING_V2 != true)")
        print("LangSmith monitoring disabled")

def log_interaction(query: str, response: str, metadata: dict = None):
    """Log a manual interaction/query to LangSmith for tracking."""
    logger.info("LangSmith interaction logged: Query='%s', Response='%s', Metadata=%s", query, response, metadata)
