#!/bin/bash
# Script to run Sensor Monitor application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to project directory
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
source venv/bin/activate

# Check if required packages are installed
python3 -c "import PyQt6; import pyqtgraph; import serial" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip install -r requirements.txt
fi

# Run the application
echo "Starting Sensor Monitor..."
python3 main.py

# Deactivate virtual environment when done
deactivate
