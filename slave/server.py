from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json
import os

app = FastAPI()

JSON_PATH = './misc_scripts.json'  # Update this to the actual path

class ScriptRequest(BaseModel):
    script: str

@app.get("/test")
async def retrieve_misc_scripts():
    return "Hello World"

@app.get("/retrieve_misc_scripts")
async def retrieve_misc_scripts():
    try:
        with open(JSON_PATH, 'r') as file:
            script_data = json.load(file)
        return script_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Script data not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_script")
async def run_script(request: ScriptRequest):
    try:
        # Read the JSON file to get the script paths
        with open(JSON_PATH, 'r') as file:
            script_data = json.load(file)
        
        # Find the script path by name
        script_path = script_data.get(request.script)
        if not script_path:
            raise HTTPException(status_code=404, detail="Script not found.")

        # Check if the script file exists
        if not os.path.isfile(script_path):
            raise HTTPException(status_code=404, detail="Script file does not exist.")

        # Run the script
        result = subprocess.run(
            script_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        return {"stdout": result.stdout, "stderr": result.stderr}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/shutdown")
async def shutdown():
    try:
        subprocess.run(["sudo", "shutdown", "now"], check=True)
        return {"detail": "Shutdown initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
