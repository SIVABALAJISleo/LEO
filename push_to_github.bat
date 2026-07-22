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
echo Staging submodule updates...
cd /d "%~dp0core_ai\colibri_engine"
git add -A
git commit -m "update(colibri): sync engine modifications"
cd /d "%~dp0"

echo.
echo Staging TestSprite test scripts and onboarding tools...
git add -A
git commit -m "feat(testsprite): add backend test files and onboard automation script"

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
