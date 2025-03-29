from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx
import toml
import socket
import struct
import logging

# Load configuration from config.toml
config = toml.load('config.toml')

# Extract settings from the config file
USER = config['network'].get('user')
HOST = config['network'].get('host')
HOST_MAC = config['network'].get('host_mac')
PORT = config['network'].get('port')

# Construct MAIN_PC_URL dynamically
MAIN_PC_URL = f"http://{HOST}:{PORT}"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
router = APIRouter()

# Utility function for Wake-on-LAN
def wake_on_lan(mac_address: str):
    """Send a Wake-on-LAN (WOL) packet to the specified MAC address."""
    try:
        mac_bytes = bytes.fromhex(mac_address.replace(':', ''))
        magic_packet = b'\xff' * 6 + mac_bytes * 16

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, ('<broadcast>', 9))
        return {"status": "success", "message": "WOL packet sent successfully"}
    except Exception as e:
        logger.error(f"Error sending WOL packet: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send WOL packet")

# Route definitions

@app.get("/health")
async def check_slave_health():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MAIN_PC_URL}/health")
            if response.status_code == 200:
                return {"status": "ok"}
            else:
                raise HTTPException(status_code=500, detail="Slave is not healthy")
    except httpx.RequestError:
        raise HTTPException(status_code=500, detail="Slave is unreachable")

@router.get("/system/hostname")
async def get_hostname():
    """Get the hostname from the slave server."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MAIN_PC_URL}/system/hostname")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        logger.error(f"Error fetching hostname: {str(exc)}")
        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as e:
        logger.error(f"Error contacting slave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to contact the slave server")

@router.get("/scripts")
async def retrieve_scripts():
    """Retrieve the list of scripts from the slave server."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MAIN_PC_URL}/scripts")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        logger.error(f"Error fetching scripts: {str(exc)}")
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to fetch scripts")
    except Exception as e:
        logger.error(f"Error contacting slave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to contact the slave server")

class ScriptRequest(BaseModel):
    script: str

@router.post("/scripts/run")
async def run_script(request: ScriptRequest):
    """Run a script on the slave server."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{MAIN_PC_URL}/scripts/run", json=request.dict())
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        logger.error(f"Error running script: {str(exc)}")
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to run script")
    except Exception as e:
        logger.error(f"Error contacting slave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to contact the slave server")

@router.post("/system/start-desktop")
async def start_desktop(item: ScriptRequest):
    """Send a Wake-on-LAN packet to start the desktop."""
    if item.script == "ValidData":
        return wake_on_lan(HOST_MAC)
    else:
        raise HTTPException(status_code=400, detail="Invalid data received")

@router.post("/system/shutdown")
async def shut_down_desktop(item: ScriptRequest):
    """Shut down the desktop via the slave server."""
    if item.script == 'ValidData':
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{MAIN_PC_URL}/system/shutdown")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(f"Error initiating shutdown: {str(exc)}")
            raise HTTPException(status_code=exc.response.status_code, detail="Failed to initiate shutdown")
        except Exception as e:
            logger.error(f"Error contacting slave: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to contact the slave server")
    else:
        raise HTTPException(status_code=400, detail="Invalid data received")

@router.get("/system/vram-usage")
async def get_vram_usage():
    """Get VRAM usage from the slave server."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MAIN_PC_URL}/system/vram-usage")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        logger.error(f"Error fetching VRAM usage: {str(exc)}")
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to fetch VRAM usage")
    except Exception as e:
        logger.error(f"Error contacting slave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to contact the slave server")

@router.get("/system/os")
async def get_os():
    """Get the operating system of the slave server."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MAIN_PC_URL}/system/os")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        logger.error(f"Error fetching OS info: {str(exc)}")
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to fetch OS info")
    except Exception as e:
        logger.error(f"Error contacting slave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to contact the slave server")

@router.get("/koboldcpp/models")
async def get_models():
    """Get the available models from the slave server."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MAIN_PC_URL}/koboldcpp/models")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        logger.error(f"Error fetching models: {str(exc)}")
        raise HTTPException(status_code=exc.response.status_code, detail="Failed to fetch models")
    except Exception as e:
        logger.error(f"Error contacting slave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to contact the slave server")

class SetParametersRequest(BaseModel):
    model_path: str
    context_length: int
    kv_cache_quant: int = 0  # Added KV Cache Quant parameter with default value 0 (FP16)

@app.post("/koboldcpp/set-parameters")
async def set_parameters(payload: SetParametersRequest):
    try:
        async with httpx.AsyncClient() as client:
            # Forward the request to the SLAVE server:
            response = await client.post(
                f"{MAIN_PC_URL}/koboldcpp/set-parameters",
                json=payload.dict()
            )
            response.raise_for_status()

        # Return the slave server's response
        return response.json()

    except httpx.HTTPStatusError as exc:
        logger.error(f"Error forwarding set-parameters: {str(exc)}")
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Failed to set parameters on the slave server"
        )
    except Exception as e:
        logger.error(f"Error contacting slave: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to contact the slave server")

app.include_router(router)

# Check if the app is running in development mode
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

if DEV_MODE:
    @app.middleware("http")
    async def add_cors_middleware(request, call_next):
        """Allow CORS for development mode."""
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response
else:
    app.mount("/", StaticFiles(directory="build", html=True), name="static")
