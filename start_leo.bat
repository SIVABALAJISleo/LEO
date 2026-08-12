@echo off
echo ===================================================
echo   LEO AI - 3D Photosynthesis Protocol Startup
echo ===================================================

echo [1/2] Starting LEO Backend (Uvicorn API on port 8005)...
start "LEO Backend API" cmd /c "set APP_ENV=development && python -m uvicorn backend.main:app --port 8005 --host 0.0.0.0 --reload"

echo [2/2] Starting LEO Frontend (Vite Dev Server)...
start "LEO Frontend" cmd /c "npm run dev"

echo.
echo Both servers are now running in separate windows!
echo - Frontend: http://localhost:8080/app
echo - Backend: http://127.0.0.1:8005/docs
echo.
echo You can safely close this window. Do not close the two new terminal windows.
pause
