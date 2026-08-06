# ASSIGNED TO: BE-2
# Chat API routes
# Endpoints to implement:
#   POST /api/chat/query    → Process user message through AI pipeline
#   GET  /api/chat/history  → Get conversation history for a user/session

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import FileResponse
from app.models.chat import ChatQuery, ChatResponse
from app.services.ai_service import process_query
import json
import os
import sys
import tempfile
from groq import AsyncGroq
from gtts import gTTS

# Initialize Groq client for Whisper STT
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

# Try importing the AI agents (handling path if needed)
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "ai-engine"))
try:
    from agents.supervisor_agent import SupervisorAgent
    supervisor = SupervisorAgent()
except ImportError:
    supervisor = None

router = APIRouter()

@router.post("/voice")
async def voice_query(audio: UploadFile = File(...)):
    """
    Process voice query: 
    1. STT (Groq Whisper)
    2. Agent Pipeline
    3. TTS (gTTS)
    """
    try:
        # Save uploaded audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            temp_audio.write(await audio.read())
            temp_audio_path = temp_audio.name

        # 1. Speech to Text via Groq
        with open(temp_audio_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=(temp_audio_path, audio_file.read())
            )
        user_text = transcription.text
        os.unlink(temp_audio_path)

        # 2. Process via Supervisor
        ai_response_text = f"I heard you say: '{user_text}'."
        if supervisor:
            try:
                result = await supervisor.route(user_text, {})
                ai_response_text = result.get("reply", ai_response_text)
            except AttributeError:
                # Fallback if using old supervisor mock
                routing = await supervisor.process(user_text)
                ai_response_text = f"I heard you say: '{user_text}'. I am routing your request to {routing}."

        # 3. Text to Speech via gTTS (Free local TTS)
        speech_file_path = os.path.join(tempfile.gettempdir(), f"response_{os.urandom(4).hex()}.mp3")
        tts = gTTS(text=ai_response_text, lang='en')
        tts.save(speech_file_path)

        # Sanitize strings to prevent HTTP header errors with newlines
        safe_user_text = user_text.replace('\n', ' ').replace('\r', '')
        safe_ai_response = ai_response_text.replace('\n', ' ').replace('\r', '')

        return FileResponse(
            path=speech_file_path, 
            media_type="audio/mpeg", 
            filename="response.mp3",
            headers={"X-Transcription": safe_user_text, "X-AI-Response": safe_ai_response}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def query(request: ChatQuery):
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

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Send processing message
            await websocket.send_text(json.dumps({"role": "system", "text": "Analyzing query..."}))
            
            # Use real supervisor if available, else mock
            if supervisor:
                try:
                    if hasattr(supervisor, "route"):
                        result = await supervisor.route(data, {})
                        reply = result.get("reply", "")
                        routing = result.get("agent_used", "SUPPORT").upper()
                        sentiment = result.get("sentiment", "neutral")
                    else:
                        routing = await supervisor.process(data)
                        reply = f"I understand. Let me transfer you to the correct department. {routing}"
                        sentiment = "neutral"
                        
                    # Phase 3: Trigger Webhook on Escalation
                    if "ESCALATION" in routing:
                        from app.services.webhook_service import WebhookService
                        await WebhookService.send_slack_alert(
                            message=f"Critical Escalation! User said: {data}",
                            channel="#urgent-escalations"
                        )
                        
                    await websocket.send_text(json.dumps({
                        "role": "ai", 
                        "text": reply,
                        "sentiment": sentiment
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({"role": "ai", "text": f"Error: {str(e)}"}))
            else:
                await websocket.send_text(json.dumps({"role": "ai", "text": "This is a mock AI response via WebSocket."}))
    except WebSocketDisconnect:
        print("Client disconnected")

@router.get("/history")
async def get_history():
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="History endpoint not implemented yet."
    )
