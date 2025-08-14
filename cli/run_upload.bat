@echo off
REM Tantor Inc AI Support Bot - Document Upload Tool for Windows
REM This script launches the document upload interface

echo Starting Tantor Inc AI Support Bot - Document Upload Tool...
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
if not exist "upload.py" (
    echo Error: Please run this script from the cli directory
    echo or navigate to the project root directory
    pause
    exit /b 1
)

REM Check for command line arguments
if "%1"=="" (
    echo Launching interactive upload tool...
    python upload.py
) else (
    echo Uploading with arguments: %*
    python upload.py %*
)

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Upload tool exited with an error. Press any key to close...
    pause >nul
)
