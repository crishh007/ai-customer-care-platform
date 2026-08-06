# Rig.care - AI Customer Care Platform

Rig.care is an autonomous, on-device AI support platform designed to handle customer tickets, track telemetry in real-time, and route queries using local and cloud SLM/LLM models. 

## Features
- **Support AI**: An intelligent chat agent with voice-to-text (Whisper) capabilities.
- **Escalations Queue**: A CRM integration for prioritizing and assigning tickets.
- **Telemetry Dashboard**: Real-time insights into active channels, CSAT scores, and predictive churn.
- **Multi-session Chat History**: Stateful chat history saved automatically.

## Tech Stack
- **Frontend**: Next.js 14, Tailwind CSS, Lucide React, Recharts.
- **Backend**: FastAPI, Python 3.9, LangChain, LangGraph.
- **Database**: MongoDB (via Motor and mongomock for local testing).
- **AI Models**: Groq (Llama-3-70b, Whisper-large-v3).

## Prerequisites
Before running the application, you must configure the environment variables for the backend.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create or edit the `.env` file and ensure the following keys are set:
   ```env
   # Mandatory for AI Inference & Voice processing
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   
   # Optional: LangSmith Tracing
   LANGCHAIN_TRACING_V2=true
   LANGSMITH_API_KEY=your_langsmith_key
   LANGSMITH_PROJECT=ai-customer-care
   ```
   *Note: If you do not have a Groq API Key, you can get one for free at [console.groq.com](https://console.groq.com).*

## Running the Application Locally (No Docker Required)

This project has been configured to use an in-memory mock database (`mongomock`) if a local MongoDB instance is not detected, meaning you do not need Docker to run it locally.

### 1. Start the Backend
Open a terminal and run the following commands:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Start the Frontend
Open a **second** terminal and run the following commands:
```bash
cd frontend
npm install
npm run dev
```

### 3. Open the App
Navigate to [http://localhost:3000](http://localhost:3000) in your browser. 
Because you are using an in-memory database, you will need to click **Sign Up** to create an account the first time you boot the server. If you restart the backend, the database will be wiped and you will need to sign up again.
