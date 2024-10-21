from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx
import toml
import socket
import struct

# Load configuration from config.toml
config = toml.load('config.toml')

# Extract settings from the config file
SSH_KEY_PATH = config['key_paths'].get('ssh_key')
USER = config['network'].get('user')
HOST = config['network'].get('host')
HOST_MAC = config['network'].get('host_mac')
PORT = config['network'].get('port')

# Construct MAIN_PC_URL dynamically
MAIN_PC_URL = f"http://{HOST}:{PORT}"

app = FastAPI()
router = APIRouter()

# Development CORS settings
if os.getenv('APP_MODE') == 'dev':
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@router.get("/get_hello_world")
async def get_hello_world():
    async with httpx.AsyncClient() as client:
        try:
            # Send a request to the slave server's /test endpoint
            response = await client.get(f"{MAIN_PC_URL}/test")
            response.raise_for_status()
            return {"message": response.text}
        except httpx.HTTPStatusError as e:
            return {"message": f"Failed to fetch Hello World: {e}"}
        except Exception as e:
            return {"message": f"Error: {e}"}


@app.get("/ping")
async def ping_slave_server():
    try:
        # Set a custom timeout (e.g., 2 seconds)
        timeout = httpx.Timeout(2.0)  # Timeout set to 2 seconds

        # Make an asynchronous request to the slave server with the custom timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{MAIN_PC_URL}/ping")

        # If the response is successful (status code 200), the server is online
        if response.status_code == 200:
            return {"detail": 1}  # Online
        else:
            return {"detail": 0}  # Offline if not 200 response
    except httpx.RequestError:
        # If there is a request error (e.g., timeout, connection error), the server is offline
        return {"detail": 0}  # Offline

class Item(BaseModel):
    value: str

@router.get("/retrieve_scripts")
async def retrieve_misc_scripts():
    # Fetch the script data from the main PC
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{MAIN_PC_URL}/retrieve_scripts")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"message": f"Failed to fetch script data: {e}"}
        except Exception as e:
            return {"message": f"Error: {e}"}

@router.post("/run_misc_script")
async def run_misc_script(item: Item):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MAIN_PC_URL}/run_script", json={"script": item.value})
        return response.json()

def wake_on_lan(mac_address: str):
    """Send a Wake-on-LAN (WOL) packet to the specified MAC address."""
    mac_bytes = bytes.fromhex(mac_address.replace(':', ''))
    magic_packet = b'\xff' * 6 + mac_bytes * 16

    # Send the packet to the broadcast address
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, ('<broadcast>', 9))

@router.post("/start_desktop")
async def start_desktop(item: Item):
    if item.value == "ValidData":
        try:
            wake_on_lan(HOST_MAC)
            return {"message": "WOL packet sent successfully"}
        except Exception as e:
            return {"message": f"Error sending WOL packet: {e}"}
    else:
        return {"message": "Error: Invalid data received"}

@router.post("/shut_down_desktop")
async def shut_down_desktop(item: Item):
    if item.value == 'ValidData':
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{MAIN_PC_URL}/shutdown")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"message": f"Failed to initiate shutdown: {e}"}
            except Exception as e:
                return {"message": f"Error: {e}"}
    else:
        return {"message": "Error: Invalid data received"}


app.include_router(router)

if os.getenv('APP_MODE') != 'dev':
    app.mount("/", StaticFiles(directory="build", html=True), name="static")
