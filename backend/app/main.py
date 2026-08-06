# ASSIGNED TO: BE-1 (App setup) + BE-2 (Router wiring)
# FastAPI application entry point

import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure sibling folders like monitoring are in the path for importing
current_dir = os.path.dirname(os.path.abspath(__file__))
monitoring_dir = os.path.abspath(os.path.join(current_dir, "../../monitoring"))
if monitoring_dir not in sys.path:
    sys.path.insert(0, monitoring_dir)

try:
    from langsmith_setup import initialize_monitoring
except ImportError:
    def initialize_monitoring():
        pass

from app.api import chat  # Import our chat router

app = FastAPI(title="AI Customer Care API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Initialize LangSmith monitoring at app startup
    initialize_monitoring()

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
from app.api import auth
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])  # BE-2
from app.api import tickets
app.include_router(tickets.router, prefix="/api/tickets", tags=["tickets"])  # BE-2
from app.api import analytics
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])  # BE-2
from app.api import crm
app.include_router(crm.router, prefix="/api/crm", tags=["CRM"])  # BE-2

@app.get("/")
async def root():
    return {"message": "AI Customer Care API is running"}
