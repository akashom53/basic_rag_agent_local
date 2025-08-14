#!/bin/bash

# Tantor Inc AI Support Bot - CLI Launcher for Unix/Linux/macOS
# This script launches the CLI interface

echo "Starting Tantor Inc AI Support Bot CLI..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        echo "Please install Python 3.8 or higher and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python $REQUIRED_VERSION or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: Please run this script from the cli directory"
    echo "or navigate to the project root directory"
    exit 1
fi

# Make sure the script is executable
chmod +x main.py

# Run the CLI
echo "Launching CLI with $PYTHON_CMD..."
$PYTHON_CMD main.py

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "CLI exited with an error."
    read -p "Press Enter to continue..."
fi
