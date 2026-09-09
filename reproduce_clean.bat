@echo off
REM ============================================================================
REM reproduce_clean.bat - One-Command Clean Replication for HYPER-CCO
REM ============================================================================
echo [HYPER-CCO] Initiating Clean Replication Pipeline...
python reproduce_clean.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Replication pipeline failed with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
echo [SUCCESS] HYPER-CCO Replication Succeeded.
