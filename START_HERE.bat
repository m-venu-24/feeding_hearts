@echo off
echo ========================================
echo   Feeding Hearts - Project Startup
echo ========================================
echo.

echo Starting services...
echo.

REM Start Django Backend
echo [1/4] Starting Django Backend (Port 8000)...
start "Django Backend" cmd /k "cd backend/django-ai-ml && python manage.py runserver 0.0.0.0:8000"
timeout /t 3 /nobreak >nul

REM Start React App
echo [2/4] Starting React App (Port 5173)...
start "React App" cmd /k "cd frontend/react-app && npm run dev"
timeout /t 2 /nobreak >nul

REM Start Angular Admin
echo [3/4] Starting Angular Admin (Port 4200)...
start "Angular Admin" cmd /k "cd frontend/angular-admin && npm start"
timeout /t 2 /nobreak >nul

REM Start Vue Integration
echo [4/4] Starting Vue Integration (Port 5174)...
start "Vue Integration" cmd /k "cd frontend/vue-integration && npm run dev"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   Services Started!
echo ========================================
echo.
echo Access URLs:
echo   React App:        http://localhost:5173
echo   Angular Admin:    http://localhost:4200
echo   Vue Integration: http://localhost:5174
echo   Django API:       http://localhost:8000/api
echo.
echo Press any key to exit...
pause >nul

