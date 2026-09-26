@echo off
title FIREGUARD AI - Industrial Fire Command Center (SIH26162)
echo ====================================================================
echo Starting FIREGUARD AI Full-Stack Platform...
echo ====================================================================

REM Check if Python is in path, or fallback to detected Anaconda/Python 3.12
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python run.py
    goto end
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py run.py
    goto end
)

if exist "C:\Users\mmoha\Downloads\dhee4\python.exe" (
    "C:\Users\mmoha\Downloads\dhee4\python.exe" run.py
    goto end
)

echo [ERROR] Python runtime not found. Please ensure Python is installed and in PATH.
pause

:end
