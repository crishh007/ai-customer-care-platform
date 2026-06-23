# Quick start script for frontend (Windows PowerShell)
Write-Host "Starting frontend..."
Set-Location frontend
npm install
Copy-Item .env.example .env.local
npm run dev
