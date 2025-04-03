#!/bin/bash

# Check if the activate script exists
if [ -f "./.venv/bin/activate" ]; then
    source "./.venv/bin/activate"
else
    echo "Virtual environment does not exist. Creating virtual environment"
    python3 -m venv .venv
    source "./.venv/bin/activate"
fi

echo "Checking Dependencies"
pip install -r requirements.txt

# Check for the --dev flag
if [[ "$1" == "--dev" ]]; then
    echo "Running Server in Development Mode"
    export DEV_MODE=true
    uvicorn app:app --host 0.0.0.0 --port 7081 --reload
else
    echo "Running Server in Production Mode"
    export DEV_MODE=false
    uvicorn app:app --host 0.0.0.0 --port 808
fi
