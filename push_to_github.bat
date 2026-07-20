@echo off
echo ================================================
echo  HYPER Project - Push to GitHub
echo ================================================
echo.
echo Checking connection to GitHub...
ping -n 1 github.com > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Cannot reach github.com
    echo.
    echo Please check:
    echo  1. Your internet connection is active
    echo  2. No VPN/proxy is blocking port 443
    echo  3. Windows Firewall is not blocking git
    echo.
    echo Press any key to try pushing anyway...
    pause > nul
)

echo.
echo Staging all project changes, Lovable AI v2.0 files, and platform stability updates...
cd /d "%~dp0"
git add -A
git commit -m "feat: complete platform stability tasks (CPU wheels, backend import fixes, .gitignore hygiene, route lazy-loading, & Dependabot security patches)"

echo.
echo Pushing all commits to GitHub...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] All files pushed to GitHub!
) else (
    echo.
    echo [FAILED] Still cannot connect or push. 
    echo Please check your internet connection and credentials, then try again.
)

echo.
pause
