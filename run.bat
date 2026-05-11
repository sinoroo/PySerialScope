@echo off
REM Script to run Sensor Monitor application on Windows

REM Get the directory where this script is located
setlocal enabledelayedexpansion
set SCRIPT_DIR=%~dp0

REM Change to project directory
cd /d "%SCRIPT_DIR%"

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if required packages are installed
python -c "import PyQt6; import pyqtgraph; import serial" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
)

REM Run the application
echo Starting Sensor Monitor...
python main.py

REM Deactivate virtual environment
deactivate
