from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import socket
import platform
import asyncio
import logging
import json
from typing import Dict
from model_downloader import ModelDownloader  # your existing script

app = FastAPI()

SCRIPTS_DIR = 'scripts'  # Path to the scripts directory
GGUF_DIR = '/mnt/storagedrive/Storage/TextGenStorage/models/gguf' # Path to your .gguf directory
CONFIG_FILE_PATH = "/home/peasantl/Documents/TextGen/koboldcpp/config.kcpps"

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

@app.get("/koboldcpp/models")
async def list_gguf_files():
    try:
        all_gguf_files = []
        for root, dirs, files in os.walk(GGUF_DIR):
            for file in files:
                if file.endswith(".gguf"):
                    all_gguf_files.append(os.path.join(root, file))
        return {"models": all_gguf_files}
    except Exception as e:
        logger.error(f"Error retrieving gguf files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve .gguf files")
    
class SetParametersRequest(BaseModel):
    model_path: str
    context_length: int

@app.post("/koboldcpp/set-parameters")
async def set_parameters(payload: SetParametersRequest):

    try:
        # 1. Load the current config
        with open(CONFIG_FILE_PATH, "r") as f:
            config_data = json.load(f)

        # 2. Modify only the specified fields
        config_data["model_param"] = payload.model_path
        config_data["contextsize"] = payload.context_length

        # 3. Save changes back to file
        with open(CONFIG_FILE_PATH, "w") as f:
            json.dump(config_data, f, indent=4)

        return {"status": "success", "msg": "Parameters updated successfully"}

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Config file not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in config file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating config: {str(e)}")

# Track the download status in a global dictionary
# "job_id" -> {"progress_ratio": float, "done": bool, "error": None or str}
download_status: Dict[str, dict] = {}

# A lock if you want to ensure only one download at a time
download_lock = asyncio.Lock()

class DownloadRequest(BaseModel):
    hf_model: str
    branch: str = "main"
    job_id: str
    specific_file: str = None

@app.post("/download/start")
async def start_download(request: DownloadRequest):
    """
    Start the download in a background thread or task, so this request returns quickly
    and doesn't block the entire server.
    """
    # Optionally, ensure only one download at a time:
    if download_lock.locked():
        raise HTTPException(status_code=409, detail="A download is already in progress.")

    # Reset or initialize the status
    download_status[request.job_id] = {
        "progress_ratio": 0.0,
        "done": False,
        "error": None,
        "filename": ""
    }

    # Acquire the lock if you only want one download at a time
    await download_lock.acquire()

    # Spawn the actual blocking work in a separate thread
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        None,  # default ThreadPoolExecutor
        _download_in_background,  # the function to run
        request,  # argument to the function
    )

    return {"status": "started", "job_id": request.job_id}


@app.get("/download/progress/{job_id}")
async def download_progress(job_id: str):
    """
    Polling endpoint to check the status of an ongoing download.
    """
    if job_id not in download_status:
        raise HTTPException(status_code=404, detail="Job not found.")

    return download_status[job_id]


def _download_in_background(request: DownloadRequest):
    """
    This function runs in a worker thread so it doesn't block the main event loop.
    """
    try:
        hf_model = request.hf_model
        branch = request.branch
        job_id = request.job_id
        specific_file = request.specific_file

        downloader = ModelDownloader()

        # Attach a chunk_callback to update the progress ratio in the global dict
        def chunk_callback(filename, ratio):
            download_status[job_id]["filename"] = filename
            download_status[job_id]["progress_ratio"] = ratio

        downloader.chunk_callback = chunk_callback

        # Get the links to download
        links, sha256, is_lora, is_llamacpp = downloader.get_download_links_from_huggingface(
            hf_model, 
            branch,
            specific_file=specific_file
        )

        # Force everything to the /mnt/storagedrive/Storage/TextGenStorage/models/gguf/
        output_folder = downloader.get_output_folder(
            hf_model, branch, is_lora, is_llamacpp, model_dir=None
        )

        # Start the download (blocking, but in this thread, not main)
        downloader.download_model_files(
            hf_model,
            branch,
            links,
            sha256,
            output_folder,
            specific_file=specific_file,
            threads=4,
            is_llamacpp=is_llamacpp
        )

        # Mark completion
        download_status[job_id]["progress_ratio"] = 1.0
        download_status[job_id]["done"] = True

    except Exception as e:
        download_status[job_id]["error"] = str(e)
        download_status[job_id]["done"] = True

    finally:
        # Release the lock
        download_lock.release()
