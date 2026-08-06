# ASSIGNED TO: AI-2 (structure) + AI-1 (LLM integration)
# Base Agent class - all agents inherit from this
# Provides: shared LLM access, prompt building, RAG context integration

import os
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)

# ── Shared LLM Instance (singleton across all agents) ──────────────────────
_shared_llm = None
_llm_initialized = False


def get_shared_llm():
    """Lazy-initialize and return the shared LLM instance."""
    global _shared_llm, _llm_initialized

    if _llm_initialized:
        return _shared_llm

    _llm_initialized = True

    # 1. Try Groq (fast + free tier)
    if os.getenv("GROQ_API_KEY"):
        try:
            from langchain_groq import ChatGroq
            _shared_llm = ChatGroq(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                temperature=0.3,
                api_key=os.getenv("GROQ_API_KEY")
            )
            logger.info("Shared LLM: ChatGroq initialized (model: %s)",
                        os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
            return _shared_llm
        except Exception as e:
            logger.warning("ChatGroq init failed: %s. Trying OpenAI.", e)

    # 2. Try OpenAI
    if os.getenv("OPENAI_API_KEY"):
        try:
            from langchain_openai import ChatOpenAI
            _shared_llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.3,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            logger.info("Shared LLM: ChatOpenAI initialized (model: gpt-4)")
            return _shared_llm
        except Exception as e:
            logger.warning("ChatOpenAI init failed: %s. No LLM available.", e)

    logger.warning("No LLM configured — agents will use rule-based fallbacks.")
    return None


class BaseAgent(ABC):
    """
    Base class for all AI agents.

    Every agent gets:
    - A name for logging/tracking
    - Access to the shared LLM
    - A system prompt template
    - Helper methods to build prompts and call the LLM
    """

    def __init__(self, name: str, system_prompt: str = ""):
        self.name = name
        self.system_prompt = system_prompt

    @abstractmethod
    async def handle(self, query: str, context: dict) -> dict:
        """
        Process a user query and return a response dict.

        Args:
            query: The user's message
            context: Dict with keys like 'rag_chunks', 'sentiment', 'intent',
                     'session_id', 'user_id', 'chat_history'

        Returns:
            dict with keys: 'reply', 'confidence', 'metadata'
        """
        pass

    def log(self, message: str):
        logger.info("[%s] %s", self.name, message)

    def get_llm(self):
        """Get the shared LLM instance."""
        return get_shared_llm()

    def build_context_text(self, rag_chunks: list) -> str:
        """Format RAG chunks into a context string for the prompt."""
        if not rag_chunks:
            return "No relevant knowledge base documents found."
        return "\n\n".join(f"[Document {i+1}]: {chunk}" for i, chunk in enumerate(rag_chunks))

    async def call_llm(self, query: str, context: dict, extra_instructions: str = "") -> str:
        """
        Build a full prompt and call the LLM.

        Returns the LLM response text, or None if LLM is unavailable.
        """
        llm = self.get_llm()
        if llm is None:
            return None

        try:
            from langchain_core.prompts import ChatPromptTemplate

            rag_chunks = context.get("rag_chunks", [])
            context_text = self.build_context_text(rag_chunks)

            full_system = (
                f"{self.system_prompt}\n\n"
                f"--- AGENT-SPECIFIC INSTRUCTIONS ---\n"
                f"{extra_instructions}\n\n"
                f"--- KNOWLEDGE BASE CONTEXT ---\n"
                f"{context_text}\n"
                f"---"
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system", full_system),
                ("human", "{question}")
            ])

            chain = prompt | llm
            result = await chain.ainvoke({"question": query})
            self.log(f"LLM call successful ({len(result.content)} chars)")
            return result.content

        except Exception as e:
            self.log(f"LLM call failed: {e}")
            return None
