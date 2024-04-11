from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from file_io import read_json
from fastapi.middleware.cors import CORSMiddleware
import os
from controllers import ssh_shutdown, WOL, run_script, fetch_ping

JSON_PATH = './misc_scripts.json'

app = FastAPI()
router = APIRouter()

#if flagged as dev
if os.getenv('APP_MODE') == 'dev':
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # List your origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@router.get("/test")
async def test():
    print("Hello World")
    return {"message": "Foo Bar"}

class Item(BaseModel):
    value: str

#how dangerous is it for people to know where your scripts are stored?
@router.get("/retrive_misc_script") 
async def retrive_misc_scripts():
    script_data = read_json(JSON_PATH)
    return script_data 


@router.post("/run_misc_script")
async def run_misc_script(item:Item):

    script_data = read_json(JSON_PATH)

    if item.value in script_data:
        run_script(script_data[item.value])
    else:
        return {"message": "Error: Invalid script name recieved"}


@router.post("/start_desktop")
async def start_desktop(item: Item):
    if item.value == "ValidData":
        WOL()
    else:
        return {"message": "Error: Invalid data recieved"}
        

@router.post("/shut_down_desktop")
async def shut_down_desktop(item: Item):
    if item.value == 'ValidData':
        ssh_shutdown()
    else:
        return {"message": "Error: Invalid data recieved"}

@router.get("/ping")
async def ping():
    return {"detail": fetch_ping('./check_ip.sh')}

app.include_router(router)

if os.getenv('APP_MODE') != 'dev':
    app.mount("/", StaticFiles(directory="build", html=True), name="static")
