from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx

app = FastAPI()
router = APIRouter()

MAIN_PC_URL = os.getenv('MAIN_PC_URL', 'http://<main_pc_ip>:<main_pc_port>')  # Set this to your main PC's IP/port

# Development CORS settings
if os.getenv('APP_MODE') == 'dev':
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@router.get("/test")
async def test():
    return {"message": "Foo Bar"}

class Item(BaseModel):
    value: str

@router.get("/retrieve_misc_scripts")
async def retrieve_misc_scripts():
    # Fetch the script data from the main PC
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{MAIN_PC_URL}/retrieve_misc_scripts")
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

@router.post("/start_desktop")
async def start_desktop(item: Item):
    if item.value == "ValidData":
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{MAIN_PC_URL}/wol", json={"mac_address": "your_mac_address"})
            return response.json()
    else:
        return {"message": "Error: Invalid data received"}

@router.post("/shut_down_desktop")
async def shut_down_desktop(item: Item):
    if item.value == 'ValidData':
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{MAIN_PC_URL}/shutdown")
            return response.json()
    else:
        return {"message": "Error: Invalid data received"}

app.include_router(router)

if os.getenv('APP_MODE') != 'dev':
    app.mount("/", StaticFiles(directory="build", html=True), name="static")
