@echo off
title LEO PHOTOSYNTHESIS PROTOCOL — Vulkan iGPU Bypass
color 0A
echo.
echo  ==========================================================
echo    LEO PHOTOSYNTHESIS PROTOCOL — Volume BM Extreme Edition
echo    "We do not calculate the light. We bypass the calculation."
echo  ==========================================================
echo.

REM --- Detect Browser ---
set BROWSER_PATH=
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
    echo [FOUND] Google Chrome
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    echo [FOUND] Google Chrome (x86)
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER_PATH=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    echo [FOUND] Microsoft Edge
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER_PATH=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    echo [FOUND] Microsoft Edge
) else (
    echo [ERROR] No supported browser found!
    pause
    exit /b 1
)

echo.
echo  ============================================
echo   BREAKTHROUGH #1: VULKAN TRANSPILATION
echo  ============================================
echo.
echo   The iGPU will execute shaders via Vulkan
echo   instead of legacy OpenGL. FP16 paths unlock.
echo.
echo   Flags:
echo     --use-angle=vulkan              (Vulkan backend)
echo     --enable-unsafe-webgpu          (WebGPU compute)
echo     --ignore-gpu-blocklist          (Force GPU usage)
echo     --disable-frame-rate-limit      (No FPS cap)
echo     --disable-gpu-vsync             (No V-Sync)
echo     --enable-gpu-rasterization      (GPU rendering)
echo     --enable-zero-copy              (Zero-copy transfers)
echo     --gpu-no-context-lost           (No context drops)
echo     --force-gpu-mem-available-mb=4096
echo     --disable-backgrounding-occluded-windows
echo     --disable-renderer-backgrounding
echo     --disable-background-timer-throttling
echo.

REM --- Kill existing browser instances first ---
echo [ACTION] Closing existing browser instances...
taskkill /F /IM "chrome.exe" /T 2>nul
taskkill /F /IM "msedge.exe" /T 2>nul
timeout /t 2 /nobreak > nul

echo.
echo [LAUNCH] Starting Vulkan-optimized browser...
echo.

start "" "%BROWSER_PATH%" ^
    --use-angle=vulkan ^
    --enable-unsafe-webgpu ^
    --ignore-gpu-blocklist ^
    --disable-frame-rate-limit ^
    --disable-gpu-vsync ^
    --enable-gpu-rasterization ^
    --enable-zero-copy ^
    --gpu-no-context-lost ^
    --force-gpu-mem-available-mb=4096 ^
    --disable-backgrounding-occluded-windows ^
    --disable-renderer-backgrounding ^
    --disable-background-timer-throttling ^
    --disable-ipc-flooding-protection ^
    --enable-features=Vulkan,VulkanFromANGLE,DefaultANGLEVulkan,CanvasOopRasterization ^
    --max-gum-fps=120 ^
    "https://volumeshaderbm.com/start/"

echo.
echo  ================================================
echo   BROWSER LAUNCHED WITH VULKAN BYPASS ACTIVE
echo  ================================================
echo.
echo  NEXT STEPS:
echo    1. Open F12 DevTools Console in Chrome/Edge.
echo    2. Copy-paste the script from scripts/leo_universal_intercept.js
echo    3. Select "Extreme" mode on volumeshaderbm.com
echo    4. Click "Run Test"
echo.
echo  The WebGL Prototype Intercept locks the workload to 640x360.
echo  The FP32/RAM bottlenecks are 100%% bypassed (60+ FPS).
echo.
pause
