#!/bin/bash
# Quick start script for frontend (Linux/Mac)
echo "Starting frontend..."
cd frontend
npm install
cp .env.example .env.local
npm run dev
