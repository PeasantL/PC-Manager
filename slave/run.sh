#!/bin/bash

# Define the virtual environment directory
VENV_DIR=".venv"

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv $VENV_DIR
    echo "Virtual environment created."
else
    echo "Virtual environment found."
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Check for requirements.txt and install dependencies if it exists
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping installation."
fi

# Run the FastAPI server on port 7082
echo "Starting FastAPI server on port 7081..."
uvicorn server:app --host 0.0.0.0 --port 7082

# Deactivate the virtual environment after stopping the server
deactivate
