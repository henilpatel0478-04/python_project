@echo off
title Snack Attack! - Launcher
cd /d "%~dp0"

echo ========================================================
echo           Launching Snack Attack! Arcade Game
echo ========================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python main.py
    goto end
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py main.py
    goto end
)

echo [ERROR] Python was not found in your system PATH!
echo Please ensure Python is installed and added to PATH.
pause

:end
