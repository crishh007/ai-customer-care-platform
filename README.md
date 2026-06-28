# 🤖 AI-Powered Intelligent Customer Care Platform

An end-to-end AI customer support platform featuring multi-agent routing, RAG-powered knowledge retrieval, sentiment analysis, and real-time chat — built with FastAPI, LangChain, ChromaDB, and Next.js.

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker-compose)
- [Manual Setup (Without Docker)](#manual-setup-without-docker)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Deployment to Render](#deployment-to-render)
- [CI/CD Pipeline](#cicd-pipeline)
- [LangSmith Monitoring Dashboard](#langsmith-monitoring-dashboard)
- [Project Structure](#project-structure)
- [Team & Branching Strategy](#team--branching-strategy)

---

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────┐
│   Frontend   │────▶│              FastAPI Backend                 │
│  (Next.js)   │◀────│                                              │
└─────────────┘     │  ┌─────────┐  ┌──────────┐  ┌────────────┐  │
                    │  │ Intent   │─▶│ Sentiment │─▶│   Agent    │  │
                    │  │Detection │  │ Analysis  │  │ Selection  │  │
                    │  └─────────┘  └──────────┘  └─────┬──────┘  │
                    │                                     │         │
                    │  ┌──────────────────────────────────┤         │
                    │  │         Agent Router              │         │
                    │  ├──────────┬───────────┬───────────┤         │
                    │  │ Support  │ Technical │ Billing   │         │
                    │  │ Agent    │ Agent     │ Agent     │         │
                    │  ├──────────┼───────────┼───────────┤         │
                    │  │Escalation│ Sentiment │ Greeting  │         │
                    │  │ Agent    │ Agent     │ Agent     │         │
                    │  └──────────┴───────────┴───────────┘         │
                    │                    │                           │
                    │  ┌─────────────────┴──────────────────┐       │
                    │  │    LLM (Groq Llama3 / OpenAI GPT-4) │       │
                    │  └─────────────────┬──────────────────┘       │
                    │                    │                           │
                    └────────────────────┼───────────────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
               ┌────▼─────┐     ┌───────▼──────┐    ┌───────▼──────┐
               │ ChromaDB  │     │   MongoDB     │    │  LangSmith   │
               │ (Vectors) │     │  (Metadata)   │    │ (Monitoring) │
               └───────────┘     └──────────────┘    └──────────────┘
```

---

## Prerequisites

| Tool       | Version  | Purpose                    |
|------------|----------|----------------------------|
| Python     | >= 3.10  | FastAPI backend & AI engine |
| Node.js    | >= 18    | Next.js frontend           |
| Docker     | >= 24.0  | Containerized deployment   |
| Git        | >= 2.30  | Version control            |
| MongoDB    | >= 7.0   | Primary database (or use Docker) |

---

## Quick Start with Docker Compose

The fastest way to get the entire platform running locally:

```bash
# 1. Clone the repository
git clone https://github.com/crishh007/ai-customer-care-platform.git
cd ai-customer-care-platform

# 2. Create your .env file from the template
cp .env.example .env
# Edit .env and add your API keys (OPENAI_API_KEY or GROQ_API_KEY)

# 3. Start all services (FastAPI + ChromaDB + MongoDB)
docker-compose -f deployment/docker-compose.yml up --build

# 4. Verify it's running
# FastAPI:  http://localhost:8000
# API Docs: http://localhost:8000/docs
# ChromaDB: http://localhost:8001
# MongoDB:  localhost:27017
```

**To stop:**
```bash
docker-compose -f deployment/docker-compose.yml down
```

**To reset all data:**
```bash
docker-compose -f deployment/docker-compose.yml down -v
```

---

## Manual Setup (Without Docker)

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Add your API keys
python run.py
# Runs on http://localhost:8000
# Docs at  http://localhost:8000/docs
```

### RAG Engine (Document Ingestion)

```bash
cd rag-engine
pip install -r requirements.txt
cp .env.example .env
python ingest.py                # Load knowledge base into ChromaDB
python retrieval.py             # Test semantic search
```

### Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
# Runs on http://localhost:3000
```

---

## API Endpoints

| Method | Endpoint | Status | Description |
|--------|----------|--------|-------------|
| `GET` | `/` | ✅ Live | Health check |
| `POST` | `/api/chat/query` | ✅ Live | AI chat — full pipeline (intent → sentiment → RAG → agent → LLM) |
| `GET` | `/api/chat/history` | 🔜 TODO | Conversation history |
| `POST` | `/api/auth/register` | 🔜 TODO | User registration |
| `POST` | `/api/auth/login` | 🔜 TODO | JWT authentication |
| `POST` | `/api/tickets/create` | 🔜 TODO | Create support ticket |
| `GET` | `/api/tickets/status` | 🔜 TODO | Ticket status |
| `GET` | `/api/analytics/dashboard` | 🔜 TODO | KPI metrics |
| `GET` | `/api/analytics/sentiment` | 🔜 TODO | Sentiment trends |

### Example — Chat Query

```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "I was charged twice for my subscription",
    "session_id": "session456"
  }'
```

**Response:**
```json
{
  "reply": "I'm sorry about the double charge. Could you please share your transaction ID...",
  "sentiment": "negative",
  "confidence_score": 0.95,
  "agent_used": "payment_agent"
}
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | One of these | OpenAI GPT-4 API key |
| `GROQ_API_KEY` | One of these | Groq (Llama3) API key — **free tier available** |
| `GROQ_MODEL` | No | Default: `llama-3.3-70b-versatile` |
| `MONGO_URI` | For auth/tickets | MongoDB connection string |
| `LANGCHAIN_TRACING_V2` | No | Set `true` to enable LangSmith |
| `LANGSMITH_API_KEY` | For monitoring | LangSmith dashboard API key |
| `JWT_SECRET` | For auth | Secret key for JWT tokens |
| `CHROMA_DB_DIR` | No | Default: `chroma_db` |

> ⚠️ **Never commit `.env` files.** Only `.env.example` with placeholder values.

---

## Deployment to Render

### FastAPI Backend

1. Go to [render.com/new](https://dashboard.render.com/new) → **New Web Service**
2. Connect your GitHub repo: `crishh007/ai-customer-care-platform`
3. Configure:
   - **Name:** `ai-customer-care-api`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in the Render dashboard (see table above)
5. Deploy!

**Or use the Blueprint:** The repo includes a `render.yaml` — go to Render → **New Blueprint Instance** → connect the repo and it auto-configures everything.

### Node.js Frontend (when ready)

1. Same process on Render → **New Web Service**
2. **Root Directory:** `frontend`
3. **Build Command:** `npm install && npm run build`
4. **Start Command:** `npm start`
5. Set `FASTAPI_URL` env var to the live FastAPI Render URL (e.g., `https://ai-customer-care-api.onrender.com`)

---

## CI/CD Pipeline

GitHub Actions automatically runs on every PR to `main` or `develop`:

| Check | Tool | What it does |
|-------|------|--------------|
| Backend tests | `pytest` | Runs all tests in `backend/tests/` |
| Frontend lint | `eslint` | Lints JS/TS files (skips if frontend not ready) |

**Failing checks block the PR from merging** — protecting `main` from broken code.

See: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

---

## LangSmith Monitoring Dashboard

All LLM calls are automatically traced when `LANGCHAIN_TRACING_V2=true`:

1. Sign up at [smith.langchain.com](https://smith.langchain.com)
2. Create an API key
3. Add to your `.env`:
   ```
   LANGCHAIN_TRACING_V2=true
   LANGSMITH_API_KEY=your_key_here
   LANGSMITH_PROJECT=ai-customer-care
   ```
4. View traces at: **smith.langchain.com → Projects → ai-customer-care**

**What's tracked:**
- Every prompt sent to the LLM
- Every response received
- Latency per call
- Token usage & cost
- Agent used & intent detected

---

## Project Structure

```
ai-customer-care-platform/
├── .github/workflows/    → CI/CD pipeline (GitHub Actions)
├── agents/               → Multi-Agent AI (Supervisor, Support, Technical, Billing, Escalation)
├── ai-engine/            → Prompt templates for all customer scenarios
├── analytics/            → Predictive analytics (churn prediction)
├── backend/              → FastAPI backend (API routes, services, models)
│   ├── app/
│   │   ├── api/          → Route handlers (chat, auth, tickets, analytics)
│   │   ├── models/       → Pydantic schemas
│   │   ├── services/     → Business logic (AI pipeline, auth)
│   │   └── middleware/   → Auth middleware
│   ├── tests/            → pytest test suite
│   └── requirements.txt
├── deployment/           → Docker & docker-compose configs
├── frontend/             → Next.js + Tailwind frontend
├── knowledge-base/       → FAQ & policy documents for RAG
├── monitoring/           → LangSmith tracing setup
├── rag-engine/           → ChromaDB ingestion & retrieval
├── scripts/              → Helper scripts (start backend/frontend)
├── voice-ai/             → Voice AI module (STT/TTS)
├── .env.example          → Environment variable template
├── .gitignore            → Comprehensive ignore rules
├── render.yaml           → Render deployment blueprint
└── README.md             → This file
```

---

## Team & Branching Strategy

```
main (protected)  ←  develop (protected)  ←  team branches  ←  feature branches
```

| Branch | Purpose | Who |
|--------|---------|-----|
| `main` | Production-ready releases | PRs only, 1+ approval required |
| `develop` | Integration & testing | Team branches merge here |
| `frontend` | Frontend team work | FE team |
| `backend` | Backend team work | BE team |
| `ai-engine` | AI team work | AI team |
| `devops` | DevOps & infra work | DevOps team |

### Workflow
```bash
git checkout backend                    # Switch to your team branch
git pull origin backend                 # Get latest
git checkout -b feature/be-auth-api     # Create feature branch
# ... make changes, commit, push ...
git push origin feature/be-auth-api
# Open PR: feature/be-auth-api → backend (teammate reviews)
# Then: backend → develop (cross-team integration)
# Finally: develop → main (release)
```

---

## Team Contacts

| Team     | Responsibility                              |
|----------|---------------------------------------------|
| AI       | Multi-agent system, RAG, sentiment, LangSmith |
| Backend  | FastAPI APIs, MongoDB, auth, tickets         |
| Frontend | Next.js UI, chat widget, dashboard           |
| DevOps   | Docker, CI/CD, Render deployment, monitoring |

---

**📄 License:** MIT
