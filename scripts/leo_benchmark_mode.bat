@echo off
title LEO BENCHMARK MODE — Full System Optimization
color 0A
echo.
echo  =============================================
echo    LEO QUANTUM — BENCHMARK MODE ACTIVATOR
echo    "Bypassing the Silicon Limit"
echo  =============================================
echo.
echo  This script will:
echo    [1] Optimize system memory (free ~3-5 GB RAM)
echo    [2] Apply Intel iGPU turbo settings
echo    [3] Set power plan to High Performance
echo    [4] Start LEO backend with minimal footprint
echo    [5] Launch GPU-optimized browser with benchmark
echo.
echo  Press any key to begin the breakthrough...
pause > nul

REM --- Phase 1+2: Run PowerShell optimizer (Admin elevation) ---
echo.
echo [STEP 1/4] Running system optimizer...
powershell -ExecutionPolicy Bypass -File "%~dp0optimize_igpu.ps1"

REM --- Phase 3: Stop existing dev servers to free resources ---
echo.
echo [STEP 2/4] Stopping existing heavy processes...
taskkill /F /IM "node.exe" /T 2>nul
echo   -> Node.js processes stopped (freeing CPU+RAM for GPU)

REM --- Phase 4: Start LEO backend with minimal workers ---
echo.
echo [STEP 3/4] Starting LEO backend (minimal mode)...
cd /d "%~dp0.."
start /MIN "LEO Backend" cmd /c "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8005 --workers 1 --limit-concurrency 10"
echo   -> Backend started with 1 worker (minimal RAM footprint)

REM --- Wait for backend to initialize ---
timeout /t 3 /nobreak > nul

REM --- Phase 5: Launch GPU-optimized browser ---
echo.
echo [STEP 4/4] Launching GPU-optimized browser...
call "%~dp0launch_chrome_gpu.bat"

echo.
echo  =============================================
echo    BENCHMARK MODE ACTIVE
echo  =============================================
echo.
echo  Your system is now optimized for maximum
echo  iGPU performance. Run the Volume Shader BM
echo  in Extreme mode and monitor Task Manager.
echo.
echo  To restore normal mode, restart your computer.
echo.
pause
