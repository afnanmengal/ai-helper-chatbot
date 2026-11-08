@echo off
setlocal enabledelayedexpansion
title Afnan's AI - Desktop Neural Assistant
cd /d "%~dp0"

echo =======================================================
echo   Launching Afnan's AI (Desktop Neural Interface)
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

:: 2. Find and run Python with PyQt6
set "PYTHON_EXE=C:\Users\hp\miniconda3\envs\ml\python.exe"
if exist "!PYTHON_EXE!" (
    echo [INFO] Launching Afnan's AI Interface...
    "!PYTHON_EXE!" desktop_app.py
    goto :DONE
)

echo [INFO] Direct ML python not found, trying conda...
where conda >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    call conda run -n ml python desktop_app.py
    goto :DONE
)

echo [INFO] Trying system python...
python desktop_app.py

:DONE
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application closed with code %ERRORLEVEL%.
    pause
)
