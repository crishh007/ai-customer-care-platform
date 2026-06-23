#!/bin/bash
# Quick start script for backend (Linux/Mac)
echo "Starting backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
echo "Add your API keys to backend/.env then press Enter"
read
python run.py
