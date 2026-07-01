"""
voice_router.py
---------------
FastAPI router for the Voice AI module.

Endpoints
---------
POST /api/voice/transcribe  — Audio file → transcript
POST /api/voice/speak       — Text → WAV audio file
POST /api/voice/chat        — Audio file → transcript + AI reply + WAV audio
"""

import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse

from speech_to_text import transcribe_audio, SUPPORTED_FORMATS
from text_to_speech import synthesize_speech
from groq_service import generate_ai_response, get_model_info

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/api/voice", tags=["Voice AI"])

# ---------------------------------------------------------------------------
# Directory paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


def _save_upload(upload: UploadFile) -> Path:
    """
    Save an UploadFile to the uploads/ directory with a unique name.
    Returns the saved file path.
    """
    suffix = Path(upload.filename or "audio.wav").suffix.lower() or ".wav"
    dest = UPLOADS_DIR / f"{uuid.uuid4().hex}{suffix}"
    with dest.open("wb") as fh:
        shutil.copyfileobj(upload.file, fh)

    # Size guard after saving (streaming-safe)
    if dest.stat().st_size > MAX_UPLOAD_BYTES:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file must be ≤ 25 MB.",
        )
    return dest


def _validate_audio_extension(upload: UploadFile) -> None:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file type '{suffix}'. "
                f"Accepted: {', '.join(sorted(SUPPORTED_FORMATS))}"
            ),
        )


# ---------------------------------------------------------------------------
# Endpoint 1 — Transcribe
# ---------------------------------------------------------------------------

@router.post(
    "/transcribe",
    summary="Speech-to-Text",
    description=(
        "Upload an audio file (mp3, wav, webm, m4a, ogg, flac) and receive "
        "the transcribed text, detected language, and word-level segments."
    ),
    response_description="Transcription result",
)
async def transcribe_endpoint(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
):
    """
    **Workflow:** Upload audio → Faster-Whisper STT → JSON transcript.
    """
    _validate_audio_extension(audio)
    saved_path = _save_upload(audio)

    try:
        result = transcribe_audio(str(saved_path))
    finally:
        saved_path.unlink(missing_ok=True)  # clean up temp upload

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result["error"],
        )

    return JSONResponse(
        content={
            "status": "success",
            "transcription": result["transcription"],
            "language": result["language"],
            "language_probability": result["language_probability"],
            "segments": result["segments"],
        }
    )


# ---------------------------------------------------------------------------
# Endpoint 2 — Speak (Text-to-Speech)
# ---------------------------------------------------------------------------

@router.post(
    "/speak",
    summary="Text-to-Speech",
    description=(
        "Send plain text and receive a downloadable WAV audio file "
        "synthesized offline with pyttsx3."
    ),
    response_class=FileResponse,
    response_description="WAV audio file",
)
async def speak_endpoint(
    text: str = Form(..., description="Text to convert to speech", max_length=5000),
    rate: int = Form(175, description="Speech rate in words per minute (50–300)", ge=50, le=300),
    volume: float = Form(1.0, description="Volume level 0.0–1.0", ge=0.0, le=1.0),
):
    """
    **Workflow:** Receive text → pyttsx3 TTS → Return WAV file as download.
    """
    result = synthesize_speech(text, rate=rate, volume=volume)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result["error"],
        )

    audio_path = Path(result["audio_path"])
    if not audio_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="TTS file was reported as created but is missing.",
        )

    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav",
        filename=result["filename"],
        headers={"X-Text-Length": str(result["text_length"])},
    )


# ---------------------------------------------------------------------------
# Endpoint 3 — Full Voice Chat Pipeline
# ---------------------------------------------------------------------------

@router.post(
    "/chat",
    summary="Full Voice Chat Pipeline",
    description=(
        "Complete end-to-end pipeline: upload audio → STT → Groq AI → TTS. "
        "Returns the transcript, AI response text, and a link to download the "
        "synthesized audio reply."
    ),
    response_description="Full pipeline result including audio download URL",
)
async def voice_chat_endpoint(
    audio: UploadFile = File(..., description="User's voice input (mp3/wav/webm/…)"),
    conversation_history: Optional[str] = Form(
        None,
        description=(
            "Optional JSON array of prior turns for multi-turn conversations. "
            'Example: [{"role":"user","content":"Hi"},{"role":"assistant","content":"Hello!"}]'
        ),
    ),
):
    """
    **Workflow:**
    1. Receive audio upload  
    2. Faster-Whisper → transcript  
    3. Groq Llama → AI reply  
    4. pyttsx3 → WAV audio of the reply  
    5. Return all three artefacts in a single JSON response  
    """
    import json

    _validate_audio_extension(audio)
    saved_path = _save_upload(audio)

    # ── Step 1: Speech → Text ───────────────────────────────────────────────
    try:
        stt_result = transcribe_audio(str(saved_path))
    finally:
        saved_path.unlink(missing_ok=True)

    if not stt_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"STT failed: {stt_result['error']}",
        )

    transcript = stt_result["transcription"]
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No speech detected in the audio file.",
        )

    # ── Step 2: Parse optional conversation history ─────────────────────────
    history: list[dict] = []
    if conversation_history:
        try:
            history = json.loads(conversation_history)
            if not isinstance(history, list):
                history = []
        except (json.JSONDecodeError, ValueError):
            history = []

    # ── Step 3: Text → Groq AI ──────────────────────────────────────────────
    ai_result = generate_ai_response(transcript, conversation_history=history)

    if not ai_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI generation failed: {ai_result['error']}",
        )

    ai_text = ai_result["response"]

    # ── Step 4: AI text → Speech ────────────────────────────────────────────
    tts_result = synthesize_speech(ai_text)

    if not tts_result["success"]:
        # Soft failure — return transcript + AI text but flag TTS issue
        logger.warning("TTS failed: %s", tts_result["error"])
        return JSONResponse(
            content={
                "status": "partial_success",
                "transcription": transcript,
                "language": stt_result.get("language", ""),
                "ai_response": ai_text,
                "audio_filename": None,
                "audio_url": None,
                "model_used": ai_result.get("model", ""),
                "token_usage": ai_result.get("usage", {}),
                "tts_error": tts_result["error"],
            }
        )

    audio_filename = tts_result["filename"]
    audio_url = f"/api/voice/audio/{audio_filename}"

    return JSONResponse(
        content={
            "status": "success",
            "transcription": transcript,
            "language": stt_result.get("language", ""),
            "language_probability": stt_result.get("language_probability", 0.0),
            "ai_response": ai_text,
            "audio_filename": audio_filename,
            "audio_url": audio_url,
            "model_used": ai_result.get("model", ""),
            "token_usage": ai_result.get("usage", {}),
        }
    )


# ---------------------------------------------------------------------------
# Endpoint 4 — Serve generated audio files
# ---------------------------------------------------------------------------

@router.get(
    "/audio/{filename}",
    summary="Download synthesized audio",
    description="Retrieve a previously synthesized WAV file by filename.",
    response_class=FileResponse,
)
async def get_audio_file(filename: str):
    """Serve WAV files from the outputs/ directory."""
    # Security: prevent path traversal
    safe_name = Path(filename).name
    audio_path = OUTPUTS_DIR / safe_name

    if not audio_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file '{safe_name}' not found.",
        )

    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav",
        filename=safe_name,
    )


# ---------------------------------------------------------------------------
# Endpoint 5 — Health / Info
# ---------------------------------------------------------------------------

@router.get(
    "/info",
    summary="Module info",
    description="Returns configuration info and health status of the Voice AI module.",
)
async def info_endpoint():
    """Returns model config and supported formats."""
    model_info = get_model_info()
    return {
        "status": "ok",
        "module": "Voice AI",
        "stt_engine": "Faster-Whisper (base)",
        "tts_engine": "pyttsx3 (offline)",
        "llm_model": model_info["model"],
        "supported_audio_formats": sorted(SUPPORTED_FORMATS),
        "groq_api_key_configured": model_info["api_key_set"],
        "max_upload_size_mb": MAX_UPLOAD_BYTES // (1024 * 1024),
    }
