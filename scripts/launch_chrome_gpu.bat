@echo off
title LEO Benchmark Mode — GPU Optimized Chrome Launch
echo.
echo =============================================
echo   LEO BENCHMARK MODE — Phase 3: GPU Browser
echo =============================================
echo.

REM --- Detect Chrome or Edge ---
set BROWSER_PATH=
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
    echo [INFO] Using Google Chrome
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set "BROWSER_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    echo [INFO] Using Google Chrome (x86)
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER_PATH=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    echo [INFO] Using Microsoft Edge
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    set "BROWSER_PATH=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    echo [INFO] Using Microsoft Edge
) else (
    echo [ERROR] No supported browser found!
    pause
    exit /b 1
)

echo.
echo [INFO] Launching browser with GPU-optimized flags...
echo.
echo   Flags Applied:
echo     --enable-gpu-rasterization       (Force GPU rendering pipeline)
echo     --enable-zero-copy               (Zero-copy GPU memory transfers)
echo     --use-angle=d3d11                (Direct3D 11 — native Intel path)
echo     --enable-features=Vulkan         (Vulkan backend for Intel)
echo     --disable-frame-rate-limit       (Remove browser FPS cap)
echo     --disable-gpu-vsync              (Disable V-Sync for max FPS)
echo     --gpu-no-context-lost            (Prevent GPU context drops)
echo     --force-gpu-mem-available-mb=4096 (Advertise 4GB GPU mem)
echo     --disable-backgrounding-occluded-windows (Keep GPU active)
echo     --disable-renderer-backgrounding  (Full GPU power to tab)
echo     --max-gum-fps=120                (Allow up to 120 FPS)
echo.

start "" "%BROWSER_PATH%" ^
    --enable-gpu-rasterization ^
    --enable-zero-copy ^
    --use-angle=d3d11 ^
    --enable-features=Vulkan,CanvasOopRasterization ^
    --disable-frame-rate-limit ^
    --disable-gpu-vsync ^
    --gpu-no-context-lost ^
    --force-gpu-mem-available-mb=4096 ^
    --disable-backgrounding-occluded-windows ^
    --disable-renderer-backgrounding ^
    --disable-background-timer-throttling ^
    --disable-ipc-flooding-protection ^
    --enable-webgl2-compute-context ^
    --enable-unsafe-webgpu ^
    --max-gum-fps=120 ^
    "https://volumeshaderbm.com/start/"

echo.
echo [SUCCESS] Browser launched with GPU optimizations!
echo [INFO] Run the Volume Shader Benchmark in Extreme mode.
echo.
pause
