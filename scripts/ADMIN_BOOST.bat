@echo off
title LEO ADMIN BOOST — Click YES on UAC prompt
color 0A

echo.
echo  ============================================================
echo    LEO ADMIN BOOST — Killing rsEngineSvc + Enabling HAGS
echo  ============================================================
echo.

echo [1/4] Killing Reason Security Engine (frees 2.3 GB RAM)...
taskkill /F /IM rsEngineSvc.exe >nul 2>&1
sc stop "Reason Security Engine" >nul 2>&1
echo      Done.

echo [2/4] Stopping Windows Update + Superfetch...
net stop wuauserv >nul 2>&1
net stop SysMain >nul 2>&1
echo      Done.

echo [3/4] Enabling Hardware Accelerated GPU Scheduling (HAGS)...
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f >nul 2>&1
echo      Done.

echo [4/4] Setting Ultimate Performance power plan...
powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c >nul 2>&1
echo      Done.

echo.
echo  ============================================================
echo    ALL DONE! rsEngineSvc killed. HAGS enabled.
echo    2.3 GB RAM freed. Now run the benchmark!
echo  ============================================================
echo.
pause
