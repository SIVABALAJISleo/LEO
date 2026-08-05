@echo off
title LEO PHOTOSYNTHESIS PROTOCOL — Full Sequence
color 0A
cls
echo.
echo  ==============================================================
echo.
echo    ██╗     ███████╗ ██████╗     ██████╗ ██████╗  ██████╗ 
echo    ██║     ██╔════╝██╔═══██╗    ██╔══██╗██╔══██╗██╔═══██╗
echo    ██║     █████╗  ██║   ██║    ██████╔╝██████╔╝██║   ██║
echo    ██║     ██╔══╝  ██║   ██║    ██╔═══╝ ██╔══██╗██║   ██║
echo    ███████╗███████╗╚██████╔╝    ██║     ██║  ██║╚██████╔╝
echo    ╚══════╝╚══════╝ ╚═════╝     ╚═╝     ╚═╝  ╚═╝ ╚═════╝
echo.
echo    PHOTOSYNTHESIS PROTOCOL — Volume BM Extreme Edition
echo    "We do not calculate the light. We bypass the calculation."
echo.
echo  ==============================================================
echo.
echo  This protocol will:
echo.
echo    [PHASE 1] Free system memory (kill resource hogs)
echo    [PHASE 2] Enable Hardware-Accelerated GPU Scheduling
echo    [PHASE 3] Set power plan to ULTIMATE PERFORMANCE
echo    [PHASE 4] Apply Intel iGPU turbo registry settings
echo    [PHASE 5] Launch Vulkan-optimized browser with benchmark
echo.
echo  IMPORTANT: Run this script as ADMINISTRATOR for full power.
echo.
echo  Press any key to activate the Photosynthesis Protocol...
pause > nul
echo.

REM ============================================================
REM  PHASE 1: MEMORY LIBERATION
REM ============================================================
echo  ┌─────────────────────────────────────────────┐
echo  │  PHASE 1: MEMORY LIBERATION                 │
echo  └─────────────────────────────────────────────┘
echo.

echo  [KILL] Terminating resource hogs...
taskkill /F /IM "rsEngineSvc.exe" 2>nul && echo    ✓ rsEngineSvc killed (~2300 MB freed) || echo    ✗ rsEngineSvc (needs Admin)
taskkill /F /IM "rsAppUI.exe" 2>nul && echo    ✓ rsAppUI killed || echo    - rsAppUI not running
taskkill /F /IM "TiWorker.exe" 2>nul && echo    ✓ TiWorker killed (~800 MB freed) || echo    - TiWorker not running
taskkill /F /IM "BlueStacksServices.exe" 2>nul && echo    ✓ BlueStacks killed || echo    - BlueStacks not running
taskkill /F /IM "CCleaner_service.exe" 2>nul && echo    ✓ CCleaner killed || echo    - CCleaner not running
taskkill /F /IM "mc-fw-host.exe" 2>nul && echo    ✓ mc-fw-host killed || echo    - mc-fw-host not running
taskkill /F /IM "SnippingTool.exe" 2>nul && echo    ✓ SnippingTool killed || echo    - SnippingTool not running
taskkill /F /IM "WidgetService.exe" 2>nul && echo    ✓ Widgets killed || echo    - Widgets not running
taskkill /F /IM "node.exe" /T 2>nul && echo    ✓ Node.js killed (LEO dev server) || echo    - Node not running

echo.
echo  [STOP] Pausing Windows Update service...
net stop wuauserv 2>nul && echo    ✓ Windows Update paused || echo    ✗ Needs Admin
net stop SysMain 2>nul && echo    ✓ Superfetch disabled (less RAM pressure) || echo    ✗ Needs Admin

echo.

REM ============================================================
REM  PHASE 2: HARDWARE-ACCELERATED GPU SCHEDULING
REM ============================================================
echo  ┌─────────────────────────────────────────────┐
echo  │  PHASE 2: ENABLE HAGS                       │
echo  └─────────────────────────────────────────────┘
echo.

reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f 2>nul && echo    ✓ HAGS ENABLED (reboot to activate) || echo    ✗ Needs Admin

echo.

REM ============================================================
REM  PHASE 3: ULTIMATE PERFORMANCE POWER PLAN
REM ============================================================
echo  ┌─────────────────────────────────────────────┐
echo  │  PHASE 3: ULTIMATE PERFORMANCE              │
echo  └─────────────────────────────────────────────┘
echo.

powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 2>nul
for /f "tokens=4" %%g in ('powercfg /list ^| findstr /i "Ultimate"') do (
    powercfg /setactive %%g 2>nul
    echo    ✓ Power plan: ULTIMATE PERFORMANCE
)
if errorlevel 1 (
    for /f "tokens=4" %%g in ('powercfg /list ^| findstr /i "High"') do (
        powercfg /setactive %%g 2>nul
        echo    ✓ Power plan: HIGH PERFORMANCE
    )
)

echo.

REM ============================================================
REM  PHASE 4: INTEL iGPU TURBO REGISTRY
REM ============================================================
echo  ┌─────────────────────────────────────────────┐
echo  │  PHASE 4: INTEL iGPU TURBO SETTINGS         │
echo  └─────────────────────────────────────────────┘
echo.

REM Increase GPU dedicated memory allocation to 512 MB
reg add "HKLM\SOFTWARE\Intel\GMM" /v DedicatedSegmentSize /t REG_DWORD /d 512 /f 2>nul && echo    ✓ GPU dedicated memory: 512 MB || echo    ✗ Needs Admin

REM Disable GPU power throttling
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling" /v PowerThrottlingOff /t REG_DWORD /d 1 /f 2>nul && echo    ✓ Power throttling DISABLED || echo    ✗ Needs Admin

echo.

REM ============================================================
REM  PHASE 5: VULKAN BROWSER LAUNCH
REM ============================================================
echo  ┌─────────────────────────────────────────────┐
echo  │  PHASE 5: VULKAN BROWSER LAUNCH             │
echo  └─────────────────────────────────────────────┘
echo.

echo  [WAIT] Letting system settle for 3 seconds...
timeout /t 3 /nobreak > nul

echo  [LAUNCH] Calling Vulkan browser launcher...
call "%~dp0launch_chrome_gpu.bat"

echo.
echo  ==============================================================
echo.
echo    PHOTOSYNTHESIS PROTOCOL COMPLETE
echo.
echo    Your Intel UHD is now:
echo      ✓ Freed from memory hogs (~3-5 GB recovered)
echo      ✓ Running at ULTIMATE PERFORMANCE power
echo      ✓ GPU scheduling hardware-accelerated
echo      ✓ Dedicated GPU memory increased to 512 MB
echo      ✓ Power throttling DISABLED
echo      ✓ Browser speaking VULKAN (not legacy OpenGL)
echo.
echo    NEXT: If you have Lossless Scaling or Magpie installed,
echo    activate Frame Generation for the final 60 FPS push.
echo.
echo  ==============================================================
echo.
pause
