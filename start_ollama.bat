@echo off
title Ollama RTX 5060 Server
cd /d "%~dp0"

echo =======================================================
echo   Starting Ollama Engine for NVIDIA GeForce RTX 5060
echo =======================================================

if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
) else (
    ollama.exe serve
)

pause
