# AI-Powered Intelligent Customer Care Platform

## Team Setup & Getting Started

### Prerequisites
- Node.js >= 18
- Python >= 3.10
- MongoDB (local or Atlas URI)
- Git

---

## 1. Clone & Setup

```bash
git clone <your-repo-url>
cd ai-customer-care-team
```

---

## 2. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
# Runs on http://localhost:3000
```

---

## 3. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
# Runs on http://localhost:8000
```

---

## 4. RAG Engine Setup

```bash
cd rag-engine
pip install -r requirements.txt
cp .env.example .env
python ingest.py       # Load knowledge base
python retrieval.py    # Test retrieval
```

---

## Project Structure

```
ai-customer-care-team/
├── frontend/          → Next.js + Tailwind (Frontend Team)
├── backend/           → FastAPI (Backend Team)
├── agents/            → Multi-Agent AI (AI Team)
├── rag-engine/        → RAG Pipeline (AI Team)
├── voice-ai/          → Voice AI (AI Team)
├── analytics/         → Predictive Analytics (AI Team)
├── knowledge-base/    → FAQs & Docs (AI Team)
├── deployment/        → Docker & Cloud (DevOps/Backend)
├── monitoring/        → LangSmith & Logs (AI Team)
└── scripts/           → Helper scripts
```

---

## Team Contacts

| Team       | Lead           |
|------------|----------------|
| Frontend   | TBD            |
| Backend    | TBD            |
| AI         | TBD            |
| QA         | TBD            |

