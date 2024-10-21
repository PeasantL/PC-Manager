from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import socket

app = FastAPI()

SCRIPTS_DIR = 'scripts'  # Update this to the actual path

class ScriptRequest(BaseModel):
    script: str

@app.get("/test")
async def retrieve_misc_scripts():
    return "Hello World"

@app.get("/get_hostname")
def get_hostname():
    hostname = socket.gethostname()
    return {"hostname": hostname}

@app.get("/ping")
async def ping():
    return {"detail": 1}  # Always returns online status

def get_scripts_structure(base_dir):
    scripts_structure = {}
    for root, dirs, files in os.walk(base_dir):
        # Get the relative folder path
        rel_folder = os.path.relpath(root, base_dir)
        
        # Filter out non-script files, assuming .sh extension
        scripts = [f for f in files if f.endswith('.sh')]

        if scripts:
            scripts_structure[rel_folder] = scripts

    return scripts_structure

@app.get("/retrieve_scripts")
async def get_scripts():
    try:
        scripts = get_scripts_structure(SCRIPTS_DIR)
        return scripts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_script")
async def run_script(request: ScriptRequest):
    try:
        # Get the scripts structure
        scripts_structure = get_scripts_structure(SCRIPTS_DIR)

        # Search for the script within the scripts structure
        script_path = None
        for folder, scripts in scripts_structure.items():
            if request.script in scripts:
                script_path = os.path.join(SCRIPTS_DIR, folder, request.script)
                break

        if not script_path or not os.path.isfile(script_path):
            raise HTTPException(status_code=404, detail="Script not found.")

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
        # Run the shutdown command as a subprocess
        result = subprocess.run(
            ["sudo", "shutdown", "now"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            return {"detail": "Shutdown initiated"}
        else:
            # Return the error message if the shutdown command fails
            return {"error": result.stderr}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
