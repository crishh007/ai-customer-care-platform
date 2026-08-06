FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (required for some Python packages like pyaudio/gtts)
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/app ./app
COPY backend/main.py .

# Copy AI Engine (since backend depends on it)
COPY ai-engine /ai-engine

ENV PYTHONPATH=/app:/ai-engine

EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
