# Quick start script for backend (Windows PowerShell)
Write-Host "Starting backend..."
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
Write-Host "Add your API keys to backend/.env then press Enter"
pause
python run.py
