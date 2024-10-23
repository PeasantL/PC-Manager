from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import socket
import platform
import asyncio
import logging

app = FastAPI()

SCRIPTS_DIR = 'scripts'  # Path to the scripts directory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Detect the current operating system
IS_LINUX = platform.system() == "Linux"
IS_WINDOWS = platform.system() == "Windows"

class ScriptRequest(BaseModel):
    script: str

# Utility functions

def get_scripts_structure(base_dir):
    try:
        scripts_structure = {}
        for root, dirs, files in os.walk(base_dir):
            rel_folder = os.path.relpath(root, base_dir)
            scripts = [f for f in files if f.endswith('.sh')]

            if scripts:
                scripts_structure[rel_folder] = scripts
        return scripts_structure
    except Exception as e:
        logger.error(f"Error retrieving script structure: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve script structure")

async def run_command_async(command):
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode()
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        raise HTTPException(status_code=500, detail="Command execution failed")

def get_vram_usage():
    try:
        result = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits']
        )
        used, total = result.decode().strip().split(',')
        return {"used_vram": int(used), "total_vram": int(total)}
    except subprocess.CalledProcessError as e:
        logger.error(f"nvidia-smi command failed: {str(e)}")
        return {"error": "Failed to retrieve VRAM usage"}

# Routes

@app.get("/health")
async def health_check():
    """Check if the server is running."""
    return {"status": "ok"}

@app.get("/system/hostname")
def get_hostname():
    """Get the system hostname."""
    try:
        hostname = socket.gethostname()
        return {"status": "success", "data": {"hostname": hostname}}
    except Exception as e:
        logger.error(f"Error retrieving hostname: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve hostname")

@app.get("/system/vram-usage")
async def vram_usage():
    """Get the VRAM usage."""
    return get_vram_usage()

@app.get("/system/os")
async def get_os_info():
    """Return the operating system of the slave PC."""
    os_info = platform.system()  # Returns 'Windows', 'Linux', etc.
    return {"os": os_info}

@app.get("/scripts")
async def get_scripts():
    """Retrieve the list of scripts."""
    try:
        scripts = get_scripts_structure(SCRIPTS_DIR)
        return {"status": "success", "data": scripts}
    except Exception as e:
        logger.error(f"Error retrieving scripts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve scripts")
        

@app.post("/scripts/run")
async def run_script(request: ScriptRequest):
    """Run a specified script."""
    try:
        scripts_structure = get_scripts_structure(SCRIPTS_DIR)
        script_path = None
        for folder, scripts in scripts_structure.items():
            if request.script in scripts:
                script_path = os.path.join(SCRIPTS_DIR, folder, request.script)
                break

        if not script_path or not os.path.isfile(script_path):
            raise HTTPException(status_code=404, detail="Script not found.")

        stdout, stderr = await run_command_async(script_path)
        if stderr:
            logger.error(f"Error running script {request.script}: {stderr}")

        return {"status": "success", "stdout": stdout, "stderr": stderr}

    except Exception as e:
        logger.error(f"Exception running script: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to run script")

@app.post("/system/shutdown")
async def shutdown():
    """Shut down the system."""
    try:
        if IS_LINUX:
            command = "sudo shutdown now"
        elif IS_WINDOWS:
            command = "shutdown /s /t 0"

        stdout, stderr = await run_command_async(command)

        if stderr:
            logger.error(f"Error during shutdown: {stderr}")
            raise HTTPException(status_code=500, detail="Shutdown failed")

        return {"status": "success", "detail": "Shutdown initiated"}
    except Exception as e:
        logger.error(f"Exception during shutdown: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate shutdown")