# Feeding Hearts - Project Startup Script
# This script starts all services for the Feeding Hearts application

Write-Host "🚀 Starting Feeding Hearts Application..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 Starting services..." -ForegroundColor Yellow
Write-Host ""

# Start Django Backend
Write-Host "1️⃣ Starting Django Backend (Port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend/django-ai-ml; python manage.py runserver 0.0.0.0:8000"
Start-Sleep -Seconds 3

# Start React Frontend
Write-Host "2️⃣ Starting React App (Port 5173)..." -ForegroundColor Cyan
if (Test-Path "frontend/react-app") {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend/react-app; if (Test-Path node_modules) { npm run dev } else { Write-Host 'Installing dependencies...'; npm install; npm run dev }"
    Start-Sleep -Seconds 2
}

# Start Angular Frontend
Write-Host "3️⃣ Starting Angular Admin (Port 4200)..." -ForegroundColor Cyan
if (Test-Path "frontend/angular-admin") {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend/angular-admin; if (Test-Path node_modules) { npm start } else { Write-Host 'Installing dependencies...'; npm install; npm start }"
    Start-Sleep -Seconds 2
}

# Start Vue Frontend
Write-Host "4️⃣ Starting Vue Integration (Port 5174)..." -ForegroundColor Cyan
if (Test-Path "frontend/vue-integration") {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend/vue-integration; if (Test-Path node_modules) { npm run dev } else { Write-Host 'Installing dependencies...'; npm install; npm run dev }"
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "✅ All services starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access URLs:" -ForegroundColor Yellow
Write-Host "   🌐 React App:        http://localhost:5173" -ForegroundColor White
Write-Host "   🎯 Angular Admin:     http://localhost:4200" -ForegroundColor White
Write-Host "   ⚡ Vue Integration:  http://localhost:5174" -ForegroundColor White
Write-Host "   🔧 Django API:       http://localhost:8000/api" -ForegroundColor White
Write-Host ""
Write-Host "⏳ Services are starting in separate windows..." -ForegroundColor Yellow
Write-Host "   Please wait a few moments for them to fully start." -ForegroundColor Yellow
Write-Host ""
Write-Host "🛑 To stop services, close the PowerShell windows or press Ctrl+C" -ForegroundColor Red
Write-Host ""

