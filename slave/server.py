from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json
import os

app = FastAPI()

JSON_PATH = './misc_scripts.json'  # Update this to the actual path

class ScriptRequest(BaseModel):
    script: str

@app.get("/retrieve_misc_scripts")
async def retrieve_misc_scripts():
    # Read the JSON file containing the scripts
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
        result = subprocess.run(request.script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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

@app.post("/wol")
async def wol(mac_address: str):
    try:
        command = ["wakeonlan", mac_address]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return {"stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
