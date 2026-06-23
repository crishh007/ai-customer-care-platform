# ASSIGNED TO: BE-2
# Chat API routes
# Endpoints to implement:
#   POST /api/chat/query    → Process user message through AI pipeline
#   GET  /api/chat/history  → Get conversation history for a user/session

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.chat import ChatQuery, ChatResponse
from app.services.ai_service import process_query

router = APIRouter()

@router.post("/query", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def query(request: ChatQuery):
    """
    Process user message through AI pipeline.
    Calls ai_service.process_query() and returns ChatResponse.
    """
    try:
        response = await process_query(
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )

# TODO: Implement history endpoint
@router.get("/history")
async def get_history():
    # Fetch conversation history by user_id or session_id
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="History endpoint not implemented yet."
    )
