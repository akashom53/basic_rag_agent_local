@echo off
REM Tantor Inc AI Support Bot - CLI Launcher for Windows
REM This script launches the CLI interface

echo Starting Tantor Inc AI Support Bot CLI...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "main.py" (
    echo Error: Please run this script from the cli directory
    echo or navigate to the project root directory
    pause
    exit /b 1
)

REM Run the CLI
echo Launching CLI...
python main.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo CLI exited with an error. Press any key to close...
    pause >nul
)
