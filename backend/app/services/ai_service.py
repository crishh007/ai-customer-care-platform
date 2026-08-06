# ASSIGNED TO: AI-1 (coordination) + BE-2 (API wiring)
# AI processing service — wires SupervisorAgent into the API pipeline

import os
import sys
import logging
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv

# Ensure sibling folders are in the Python search path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
agents_dir = os.path.abspath(os.path.join(current_dir, "../../.."))
rag_dir = os.path.abspath(os.path.join(current_dir, "../../../rag-engine"))
monitoring_dir = os.path.abspath(os.path.join(current_dir, "../../../monitoring"))

for d in [project_root, agents_dir, rag_dir, monitoring_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

# Import schemas
from app.models.chat import ChatResponse

# Import RAG retrieval (graceful fallback)
try:
    from retrieval import retrieve
except ImportError:
    def retrieve(query: str, top_k: int = 3) -> list[str]:
        return []

# Import LangSmith logging (graceful fallback)
try:
    from langsmith_setup import log_interaction
except ImportError:
    def log_interaction(query: str, response: str, metadata: dict = None):
        pass

# Import SupervisorAgent
try:
    from agents.supervisor_agent import SupervisorAgent
    _supervisor = SupervisorAgent()
    logging.getLogger(__name__).info("SupervisorAgent initialized successfully")
except Exception as e:
    _supervisor = None
    logging.getLogger(__name__).warning("SupervisorAgent failed to initialize: %s", e)

load_dotenv()

logger = logging.getLogger(__name__)


async def process_query(user_id: str, message: str, session_id: str = None) -> ChatResponse:
    """
    Main AI Service Pipeline (powered by SupervisorAgent):

    1. Retrieve RAG context from ChromaDB
    2. Route through SupervisorAgent:
       a. Input safety check
       b. Sentiment analysis
       c. Intent detection
       d. Agent selection & execution (LLM call)
       e. Response validation & re-routing
       f. Confidence scoring
       g. Output safety check
    3. Log to LangSmith
    4. Return ChatResponse
    """
    try:
        # ── Step 1: Retrieve RAG context ────────────────────────────────
        context_chunks = []
        try:
            context_chunks = retrieve(message, top_k=3)
        except Exception as e:
            logger.warning("RAG retrieval failed: %s", e)

        # ── Step 2: Route through SupervisorAgent ───────────────────────
        if _supervisor is not None:
            context = {
                "rag_chunks": context_chunks,
                "user_id": user_id,
                "session_id": session_id,
            }

            result = await _supervisor.route(message, context)

            reply = result["reply"]
            sentiment = result["sentiment"]
            confidence_score = result["confidence_score"]
            agent_used = result["agent_used"]
            metadata = result.get("metadata", {})

        else:
            # Fallback: if SupervisorAgent failed to init, use basic response
            logger.warning("SupervisorAgent not available — using basic fallback")
            reply = _basic_fallback(message, context_chunks)
            sentiment = "neutral"
            confidence_score = 0.50
            agent_used = "support_agent"
            metadata = {"fallback": True}

        # ── Step 3: Log to LangSmith ────────────────────────────────────
        log_interaction(
            query=message,
            response=reply,
            metadata={
                "user_id": user_id,
                "session_id": session_id,
                "sentiment": sentiment,
                "agent_used": agent_used,
                "confidence_score": confidence_score,
                "context_chunks_count": len(context_chunks),
                **metadata,
            }
        )

        # ── Step 4: Return structured response ──────────────────────────
        return ChatResponse(
            reply=reply,
            sentiment=sentiment,
            confidence_score=confidence_score,
            agent_used=agent_used,
        )

    except Exception as e:
        logger.error("Error in process_query pipeline: %s", e, exc_info=True)
        return ChatResponse(
            reply="I'm sorry, an internal error occurred while processing your request. Please try again later.",
            sentiment="neutral",
            confidence_score=0.0,
            agent_used="support_agent",
        )


def _basic_fallback(message: str, context_chunks: list) -> str:
    """Simple rule-based fallback when SupervisorAgent is unavailable."""
    if context_chunks:
        return (
            f"Based on our knowledge base: \"{context_chunks[0]}\"\n\n"
            f"If you need more help, our support team is standing by!"
        )
    return (
        "Thank you for contacting customer care. "
        "We received your query and a support agent will assist you shortly. "
        "Please feel free to provide more details about your question."
    )
