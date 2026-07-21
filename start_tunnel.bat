@echo off
:: ================================================================
::  LEO AI — Public Tunnel Launcher
::  Exposes http://localhost:8005 via Cloudflare Tunnel (free)
::  so the Lovable cloud preview can reach your local backend.
:: ================================================================
echo.
echo ================================================================
echo  LEO AI — Public Backend Tunnel
echo ================================================================
echo.
echo This script creates a secure public HTTPS URL for your local
echo LEO backend (http://localhost:8005) using Cloudflare Tunnel.
echo.
echo The public URL will look like:
echo   https://xxxx-xxxx-xxxx.trycloudflare.com
echo.
echo Copy that URL into your Lovable app Settings panel and Save.
echo Then the "Cannot reach LEO backend" banner will clear.
echo.
echo ================================================================
echo.

:: Check if cloudflared is available
where cloudflared >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] cloudflared not found. Downloading now...
    echo.
    :: Download the Windows binary directly from Cloudflare
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    if %errorlevel% neq 0 (
        echo [ERROR] Could not download cloudflared.
        echo.
        echo Please download it manually from:
        echo   https://github.com/cloudflare/cloudflared/releases/latest
        echo Then re-run this script.
        pause
        exit /b 1
    )
    echo [OK] cloudflared downloaded.
    set CLOUDFLARED="%~dp0cloudflared.exe"
) else (
    set CLOUDFLARED=cloudflared
)

echo Starting Cloudflare Tunnel for http://localhost:8005...
echo.
echo ================================================================
echo  COPY THE PUBLIC URL BELOW INTO LOVABLE SETTINGS
echo ================================================================
echo.

%CLOUDFLARED% tunnel --url http://localhost:8005

echo.
pause
