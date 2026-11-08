@echo off
setlocal enabledelayedexpansion
title Afnan's AI - Web Neural Assistant
cd /d "%~dp0"

echo =======================================================
echo   Launching Afnan's AI (Web Browser Interface)
echo   Hardware Mode: Automatic (GPU Accelerated / CPU Mode)
echo =======================================================

:: 1. Ensure Ollama service is running
curl -s -m 2 http://127.0.0.1:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Initializing neural background engine...
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        start "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
    ) else (
        start "" ollama.exe serve
    )
    ping 127.0.0.1 -n 4 >nul
) else (
    echo [OK] Neural engine is active.
)

:: 2. Find and run Streamlit
set "STREAMLIT_EXE=C:\Users\hp\miniconda3\envs\ml\Scripts\streamlit.exe"
if exist "!STREAMLIT_EXE!" (
    echo [INFO] Opening Web UI at http://localhost:8501...
    "!STREAMLIT_EXE!" run web_app.py
    goto :DONE
)

echo [INFO] Direct Streamlit not found, trying conda...
where conda >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call conda run -n ml streamlit run web_app.py
    goto :DONE
)

echo [INFO] Trying system streamlit...
streamlit run web_app.py

:DONE
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Web app exited with code %ERRORLEVEL%.
    pause
)
