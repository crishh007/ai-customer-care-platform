# ASSIGNED TO: AI-1 (coordination) + BE-2 (API wiring)
# AI processing service

import os
import sys
import logging
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv

# Ensure the sibling folders are in the Python search path
current_dir = os.path.dirname(os.path.abspath(__file__))
rag_dir = os.path.abspath(os.path.join(current_dir, "../../../rag-engine"))
monitoring_dir = os.path.abspath(os.path.join(current_dir, "../../../monitoring"))

if rag_dir not in sys.path:
    sys.path.insert(0, rag_dir)
if monitoring_dir not in sys.path:
    sys.path.insert(0, monitoring_dir)

# Import schemas and services
from app.models.chat import ChatResponse
try:
    from retrieval import retrieve
except ImportError:
    # Fallback if imported from another context
    def retrieve(query: str, top_k: int = 3) -> list[str]:
        return []

try:
    from langsmith_setup import log_interaction
except ImportError:
    def log_interaction(query: str, response: str, metadata: dict = None):
        pass

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize LLM client (LangChain preferred)
_llm = None

# 1. Prefer Groq Chat LLM
if os.getenv("GROQ_API_KEY"):
    try:
        from langchain_groq import ChatGroq
        _llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
        logger.info("LangChain ChatGroq LLM initialised (model: %s)", os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    except Exception as e:
        logger.warning("Failed to initialise ChatGroq: %s. Trying OpenAI.", e)

# 2. Try OpenAI Chat LLM
if _llm is None and os.getenv("OPENAI_API_KEY"):
    try:
        from langchain_openai import ChatOpenAI
        _llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        logger.info("LangChain ChatOpenAI LLM initialised (model: gpt-4)")
    except Exception as e:
        logger.warning("Failed to initialise ChatOpenAI: %s. Using fallback.", e)

# Define prompts and agent guidelines
SYSTEM_PROMPT = """You are an AI-powered customer support assistant for a modern customer care platform.

Your personality:
- Professional
- Friendly
- Helpful
- Calm
- Respectful

Your responsibilities:
- Help users politely and professionally.
- Answer customer questions clearly and accurately.
- Keep responses short and easy to understand.
- Maintain a positive customer-support tone.
- Ask follow-up questions if user requests are unclear.
- Handle frustrated users calmly and respectfully.

Behavior Rules:
- Never use rude or offensive language.
- Never provide fake or misleading information.
- Never argue with users.
- Never generate harmful content.
- Politely admit when information is unavailable.

Response Style:
- Human-like
- Supportive
- Concise
- Customer-focused
"""

AGENT_GUIDELINES = {
    "greeting_agent": "Greet users warmly and professionally. Maintain a friendly customer-support tone.",
    "payment_agent": "For payment-related issues:\n- Be polite and reassuring\n- Ask for transaction details if needed\n- Guide users carefully through troubleshooting\n\nExample:\n\"Please confirm whether the payment amount was deducted from your account.\"",
    "technical_agent": "For technical issues:\n- Explain solutions step-by-step\n- Keep instructions simple\n- Avoid complicated technical jargon\n- Ask follow-up questions if needed\n\nExample:\n\"Please restart the application and try again. If the issue continues, let me know the error message.\"",
    "account_agent": "For account-related issues:\n- Help users with login and password recovery\n- Explain account steps clearly\n- Maintain secure and professional communication\n\nExample:\n\"You can reset your password using the 'Forgot Password' option on the login page.\"",
    "escalation_agent": "If the customer is angry or the issue cannot be resolved:\n- Stay calm and respectful\n- Apologize professionally\n- Show empathy\n- Focus on solving the issue\n- Avoid arguments\n- Politely recommend contacting human support\n- Avoid misleading solutions\n- Remain professional and empathetic\n\nExample:\n\"I’m sorry for the inconvenience. Our support team will assist you further with this issue.\"",
    "fallback_agent": "If information is unavailable:\n- Politely admit uncertainty\n- Avoid fake answers\n- Suggest contacting support if required\n\nExample:\n\"I’m sorry, but I don’t currently have that information. Please contact our support team for further assistance.\""
}

def detect_intent(message: str) -> str:
    """Helper to detect intent using regex whole-word matching."""
    import re
    msg = message.lower()
    
    # Define keywords
    angry_kws = ["angry", "bad", "worst", "terrible", "hate", "disappointed", "frustrated", "rubbish", "crap", "stupid"]
    payment_kws = ["pay", "payment", "card", "billing", "invoice", "charge", "price", "cost", "subscription", "upgrade", "plan", "visa", "mastercard", "amex"]
    account_kws = ["password", "reset", "login", "register", "email", "account", "signup", "sign in"]
    technical_kws = ["bug", "error", "crash", "crashing", "slow", "broken", "issue", "technical", "help", "work", "load"]
    greeting_kws = ["hi", "hello", "hey", "greet", "greetings", "good morning", "good afternoon"]

    # Helper function to check whole-word matching
    def has_kw(kws):
        return any(re.search(r'\b' + re.escape(kw) + r'\b', msg) for kw in kws)

    # Prioritize specific intents first to avoid general greeting override
    if has_kw(angry_kws):
        return "angry"
    if has_kw(payment_kws):
        return "payment"
    if has_kw(account_kws):
        return "account"
    if has_kw(technical_kws):
        return "technical"
    if has_kw(greeting_kws):
        return "greeting"
        
    return "general"


def analyze_sentiment(message: str, intent: str) -> str:
    """Helper to classify sentiment."""
    if intent == "angry":
        return "negative"
    
    msg = message.lower()
    if any(w in msg for w in ["good", "great", "awesome", "excellent", "love", "thanks", "thank you", "perfect"]):
        return "positive"
        
    if any(w in msg for w in ["bad", "worst", "terrible", "hate", "disappointed", "slow", "broken", "angry"]):
        return "negative"
        
    return "neutral"

def select_agent(intent: str) -> tuple[str, str]:
    """Helper to select agent name and load specific prompt guidelines."""
    if intent == "payment":
        return "payment_agent", AGENT_GUIDELINES["payment_agent"]
    elif intent == "account":
        return "account_agent", AGENT_GUIDELINES["account_agent"]
    elif intent == "technical":
        return "technical_agent", AGENT_GUIDELINES["technical_agent"]
    elif intent == "angry":
        return "escalation_agent", AGENT_GUIDELINES["escalation_agent"]
    elif intent == "greeting":
        return "support_agent", AGENT_GUIDELINES["greeting_agent"]
    else:
        return "support_agent", AGENT_GUIDELINES["fallback_agent"]

def _build_fallback_response(message: str, context_chunks: list[str], agent_name: str) -> str:
    """Rule-based fallback when no LLM is configured."""
    if agent_name == "support_agent" and not context_chunks:
        return "Hello! How can I assist you today?"
        
    if agent_name == "escalation_agent":
        return "I’m sorry for the inconvenience. Our support team has been notified and will assist you further with this issue."
        
    if agent_name == "account_agent":
        return "You can reset your password using the 'Forgot Password' option on the login page or update your account details under Settings."
        
    if agent_name == "payment_agent":
        return "We accept Visa, MasterCard, American Express, UPI, and Net Banking. Please confirm whether the payment amount was deducted from your account."
        
    if context_chunks:
        best_match = context_chunks[0]
        return (
            f"According to our knowledge base: \"{best_match}\"\n\n"
            f"If you have additional questions or need more help regarding your query, "
            f"our customer care team is standing by!"
        )
        
    return (
        f"Thank you for contacting customer care. We received your query. "
        f"We couldn't find a direct policy matching your query in our database. "
        f"Please feel free to clarify your question or contact our support team."
    )

async def process_query(user_id: str, message: str, session_id: str = None) -> ChatResponse:
    """
    Main AI Service Pipeline:
    1. Detect intent
    2. Analyze sentiment
    3. Retrieve context from RAG engine
    4. Select appropriate agent
    5. Call LLM (OpenAI GPT-4 or Groq fallback)
    6. Score confidence
    7. Return response
    """
    try:
        # Step 1: Detect intent
        intent = detect_intent(message)
        
        # Step 2: Analyze sentiment
        sentiment = analyze_sentiment(message, intent)
        
        # Step 3: Retrieve context from RAG engine
        context_chunks = []
        if intent not in ["greeting"]:
            context_chunks = retrieve(message, top_k=3)
            
        # Step 4: Agent selection
        agent_used, agent_guideline = select_agent(intent)
        
        # Step 5: Call LLM or use fallback
        reply_text = ""
        confidence_score = 1.0
        
        if _llm is not None:
            try:
                from langchain_core.prompts import ChatPromptTemplate
                
                context_text = "\n\n".join(context_chunks) if context_chunks else "No relevant context found."
                
                # Combine system prompt, agent guidelines, and context
                full_system_prompt = (
                    f"{SYSTEM_PROMPT}\n\n"
                    f"--- CURRENT AGENT INSTRUCTIONS: {agent_used.upper()} ---\n"
                    f"{agent_guideline}\n\n"
                    f"--- KNOWLEDGE BASE CONTEXT ---\n"
                    f"{context_text}\n---"
                )
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", full_system_prompt),
                    ("human", "{question}")
                ])
                
                chain = prompt | _llm
                result = await chain.ainvoke({"question": message})
                reply_text = result.content
            except Exception as e:
                logger.error("LLM generation failed: %s — falling back.", e)
                reply_text = _build_fallback_response(message, context_chunks, agent_used)
        else:
            reply_text = _build_fallback_response(message, context_chunks, agent_used)
            
        # Step 6: Score confidence
        if agent_used == "escalation_agent":
            confidence_score = 0.5
        elif intent not in ["greeting"] and not context_chunks:
            confidence_score = 0.6
        else:
            confidence_score = 0.95
            
        # Log manual interaction to LangSmith
        log_interaction(
            query=message,
            response=reply_text,
            metadata={
                "user_id": user_id,
                "session_id": session_id,
                "intent": intent,
                "sentiment": sentiment,
                "agent_used": agent_used,
                "confidence_score": confidence_score,
                "context_chunks_count": len(context_chunks)
            }
        )
        
        # Step 7: Return structured response
        return ChatResponse(
            reply=reply_text,
            sentiment=sentiment,
            confidence_score=confidence_score,
            agent_used=agent_used
        )
        
    except Exception as e:
        logger.error("Error in process_query pipeline: %s", e)
        return ChatResponse(
            reply="I'm sorry, an internal error occurred while processing your request. Please try again later.",
            sentiment="neutral",
            confidence_score=0.0,
            agent_used="support_agent"
        )
