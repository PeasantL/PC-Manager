#!/bin/bash

#Check if the activate script exists
if [ -f "./.venv/bin/activate" ]; then
    source "./.venv/bin/activate"
else
    echo "Virtual environment does not exist. Creating virtual environment"
    python3 -m venv .venv
    source "./.venv/bin/activate"
fi

echo "Checking Dependancies"
pip install -r requirements.txt
echo "Running Server"

if [ "$1" == "--dev" ]; then
    export APP_MODE=dev
    # Run Uvicorn with hot reload and more CORS options for development
    uvicorn app:app --reload --host 0.0.0.0 --port 8001 
else
    # Run Uvicorn normally without hot reload for production
    sudo .venv/bin/uvicorn app:app --host 0.0.0.0 --port 80

fi
