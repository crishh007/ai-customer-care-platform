import datetime
import pytest
from unittest.mock import patch, MagicMock

def test_root_endpoint(client):
    """Test that GET / returns the correct status and message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AI Customer Care API is running"}

def test_query_validation_error(client):
    """Test validation errors for invalid input (e.g. missing fields)."""
    # Missing fields
    response = client.post("/api/chat/query", json={})
    assert response.status_code == 422

    # Missing message
    response = client.post("/api/chat/query", json={"user_id": "test_user"})
    assert response.status_code == 422

    # Missing user_id
    response = client.post("/api/chat/query", json={"message": "Hello"})
    assert response.status_code == 422

def test_query_pipeline_fallback(client):
    """Test that query endpoint returns a valid response using fallback when LLM is offline."""
    payload = {
        "user_id": "user_123",
        "message": "Hi, I need help with my account password.",
        "session_id": "session_abc"
    }
    # Temporarily patch _llm to None to force fallback path
    with patch("app.services.ai_service._llm", None):
        response = client.post("/api/chat/query", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "reply" in data
        assert "sentiment" in data
        assert "confidence_score" in data
        assert "agent_used" in data
        
        # Verify values for password reset query routing
        assert data["agent_used"] == "account_agent"
        assert "password" in data["reply"].lower() or "forgot password" in data["reply"].lower()

def test_query_pipeline_with_mocked_llm(client):
    """Test that when LLM is configured, query routes through LLM chain."""
    from unittest.mock import AsyncMock

    mock_ai_message = MagicMock()
    mock_ai_message.content = "This is a mocked LLM response for technical support."

    mock_chain = MagicMock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_ai_message)

    mock_prompt = MagicMock()
    mock_prompt.__or__ = MagicMock(return_value=mock_chain)

    mock_llm = MagicMock()

    with patch("app.services.ai_service._llm", mock_llm), \
         patch("langchain_core.prompts.ChatPromptTemplate.from_messages", return_value=mock_prompt):
        
        payload = {
            "user_id": "user_456",
            "message": "My app keeps crashing.",
            "session_id": "session_def"
        }
        
        response = client.post("/api/chat/query", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["reply"] == "This is a mocked LLM response for technical support."
        assert data["agent_used"] == "technical_agent"
