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
uvicorn app:app --reload --host 0.0.0.0