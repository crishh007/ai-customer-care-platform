"""
app.py
------
FastAPI application entry point for the AI-Powered Voice AI Module (AI-5).

Tech Stack (100% free, no OpenAI):
  STT  : Faster-Whisper
  LLM  : Groq API  (llama-3.3-70b-versatile)
  TTS  : pyttsx3 (offline)
  Web  : FastAPI + Uvicorn
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from voice_router import router as voice_router

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Directory setup
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
(BASE_DIR / "uploads").mkdir(exist_ok=True)
(BASE_DIR / "outputs").mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI-Powered Intelligent Customer Care — Voice AI Module",
    description=(
        "## Voice AI Module (AI-5)\n\n"
        "End-to-end voice pipeline using **100% free technologies**:\n\n"
        "| Component | Technology |\n"
        "|-----------|------------|\n"
        "| Speech-to-Text | Faster-Whisper (offline) |\n"
        "| AI Chat | Groq API — Llama 3.3 70B |\n"
        "| Text-to-Speech | pyttsx3 (offline) |\n\n"
        "### Quick-start\n"
        "1. Set `GROQ_API_KEY` in `.env`\n"
        "2. `uvicorn app:app --reload`\n"
        "3. Open `/docs` (Swagger UI)\n\n"
        "### Endpoints\n"
        "| Method | Path | Description |\n"
        "|--------|------|-------------|\n"
        "| POST | `/api/voice/transcribe` | Audio → text |\n"
        "| POST | `/api/voice/speak` | Text → WAV audio |\n"
        "| POST | `/api/voice/chat` | Audio → text + AI → WAV |\n"
        "| GET  | `/api/voice/audio/{filename}` | Download audio file |\n"
        "| GET  | `/api/voice/info` | Module health info |\n"
    ),
    version="1.0.0",
    contact={
        "name": "AI-5 Voice Module",
        "url": "https://github.com/your-username/voice-ai",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS — allow all origins during development
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Mount static file serving for the outputs/ folder (audio downloads)
# ---------------------------------------------------------------------------
app.mount(
    "/outputs",
    StaticFiles(directory=str(BASE_DIR / "outputs")),
    name="outputs",
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(voice_router)


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["Root"], summary="Root health check")
async def root():
    return {
        "message": "Voice AI Module is running 🎙️",
        "docs": "/docs",
        "redoc": "/redoc",
        "info": "/api/voice/info",
    }


@app.get("/health", tags=["Root"], summary="Health probe")
async def health():
    return {"status": "healthy"}


# ---------------------------------------------------------------------------
# Dev server entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level="info",
    )
