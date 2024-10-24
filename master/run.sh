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

#sudo /home/peasantl/PC-Manager/master/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 80    
uvicorn app:app --host 0.0.0.0 --port 80
