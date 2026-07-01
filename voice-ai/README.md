# 🎙️ Voice AI Module (AI-5)

> **AI-Powered Intelligent Customer Care Platform**  
> Module: AI-5 — Voice AI  
> Stack: FastAPI · Faster-Whisper · Groq API · pyttsx3 · Python 3.11+

---

## 📦 Tech Stack (100 % Free — Zero OpenAI)

| Layer | Technology | Cost |
|-------|-----------|------|
| Web Framework | FastAPI + Uvicorn | Free |
| Speech-to-Text | Faster-Whisper (base model) | Free / Offline |
| LLM / AI Chat | Groq API — Llama 3.3 70B | Free tier |
| Text-to-Speech | pyttsx3 | Free / Offline |
| Config | python-dotenv | Free |

---

## 📁 Project Structure

```
voice-ai/
├── app.py                   ← FastAPI application entry point
├── speech_to_text.py        ← STT module (Faster-Whisper)
├── text_to_speech.py        ← TTS module (pyttsx3)
├── voice_router.py          ← API endpoints
├── groq_service.py          ← Groq LLM integration
├── requirements.txt         ← Python dependencies
├── .env.example             ← Environment variable template
├── .gitignore
├── Dockerfile
├── README.md
├── uploads/                 ← Temp storage for uploaded audio
├── outputs/                 ← Generated WAV audio files
└── tests/
    ├── __init__.py
    ├── test_stt.py          ← Speech-to-Text tests
    ├── test_tts.py          ← Text-to-Speech tests
    ├── test_chat.py         ← Groq AI chat tests
    └── sample_audio/
        └── README.md        ← How to add test audio files
```

---

## 🚀 Quick Start

### Step 1 — Get a Free Groq API Key

1. Go to **https://console.groq.com**
2. Sign up / log in (free, no credit card)
3. Click **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_…`)

### Step 2 — Configure Environment

```bash
# In the voice-ai/ directory:
cp .env.example .env
```

Open `.env` and set your key:

```env
GROQ_API_KEY=gsk_your_actual_key_here
```

### Step 3 — Create Virtual Environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 4 — Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Linux/WSL only:** pyttsx3 requires espeak  
> ```bash
> sudo apt-get install espeak espeak-ng libespeak-ng1 ffmpeg
> ```

### Step 5 — Run the Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

You'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/` | Root health check |
| GET  | `/health` | Health probe |
| GET  | `/docs` | **Swagger UI** (interactive) |
| GET  | `/redoc` | ReDoc documentation |
| POST | `/api/voice/transcribe` | Audio → text |
| POST | `/api/voice/speak` | Text → WAV audio |
| POST | `/api/voice/chat` | Audio → transcript + AI reply + WAV |
| GET  | `/api/voice/audio/{filename}` | Download generated audio |
| GET  | `/api/voice/info` | Module info & health |

---

## 🧪 Testing

### Run All Tests

```bash
# Unit + validation tests (no API key needed)
pytest tests/ -v -m "not integration"

# All tests including live API calls (needs GROQ_API_KEY)
pytest tests/ -v

# Individual test files
pytest tests/test_stt.py -v
pytest tests/test_tts.py -v
pytest tests/test_chat.py -v
```

### Test with Swagger UI

1. Open **http://localhost:8000/docs**
2. Each endpoint has a **Try it out** button

#### Test `/api/voice/transcribe`
1. Click **POST /api/voice/transcribe** → **Try it out**
2. Upload any `.wav` or `.mp3` file
3. Click **Execute**
4. See the transcript in the response

#### Test `/api/voice/speak`
1. Click **POST /api/voice/speak** → **Try it out**
2. Enter text: `"Hello, I am your AI assistant."`
3. Click **Execute**
4. Click the download link in the response

#### Test `/api/voice/chat` (Full Pipeline)
1. Click **POST /api/voice/chat** → **Try it out**
2. Upload an audio file
3. Click **Execute**
4. Response contains `transcription`, `ai_response`, and `audio_url`

---

## 🐳 Docker

```bash
# Build
docker build -t voice-ai .

# Run
docker run -p 8000:8000 --env-file .env voice-ai

# Open Swagger
open http://localhost:8000/docs
```

---

## 🔧 Configuration Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | — | Your Groq API key |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | LLM model to use |
| `GROQ_SYSTEM_PROMPT` | No | Built-in prompt | Custom AI personality |
| `HOST` | No | `0.0.0.0` | Server bind host |
| `PORT` | No | `8000` | Server port |

---

## 📡 Example API Calls (curl)

### Transcribe Audio
```bash
curl -X POST http://localhost:8000/api/voice/transcribe \
  -F "audio=@/path/to/your/audio.wav"
```

### Text-to-Speech
```bash
curl -X POST http://localhost:8000/api/voice/speak \
  -F "text=Hello, how can I help you today?" \
  -o output.wav
```

### Full Voice Chat Pipeline
```bash
curl -X POST http://localhost:8000/api/voice/chat \
  -F "audio=@/path/to/your/audio.wav" \
  --output response.json
```

---

## 🔊 Adding Sample Audio for Tests

```bash
# Auto-generate using pyttsx3 (run from voice-ai/ directory):
python - <<'EOF'
import pyttsx3
engine = pyttsx3.init()
engine.save_to_file(
    "Hello, this is a test. My order has not arrived yet. Can you help me?",
    "tests/sample_audio/sample.wav"
)
engine.runAndWait()
print("Sample audio created!")
EOF
```

---

## 🐙 Push to GitHub

```bash
# Initialise git (if not already done)
git init
git add .
git commit -m "feat: AI-5 Voice AI Module — complete implementation"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/voice-ai.git
git branch -M main
git push -u origin main
```

---

## 📝 Notes

- **Whisper model** downloads automatically on first run (~75 MB for `base`).
- **pyttsx3 on Linux** needs `espeak` installed via apt.
- **Groq free tier** is generous (~14,400 requests/day as of 2025).
- **No OpenAI** anywhere — this project is 100% free to run.

---

*Built for AI-Powered Intelligent Customer Care Platform — Internship Project*
