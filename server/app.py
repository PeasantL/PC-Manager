import subprocess
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from file_io import read_json

JSON_PATH = './misc_scripts.json'


app = FastAPI()
router = APIRouter()


def run_scripts(script_path):
    process = subprocess.Popen(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    return process.returncode

@router.get("/test")
async def test():
    print("Hello World")
    return {"message": "Foo Bar"}

class Item(BaseModel):
    value: str

@router.get("/retrive_misc_script") 
async def retrive_misc_scripts():
    script_data = read_json(JSON_PATH)
    return script_data 

@router.post("/start_desktop")
async def start_desktop(item: Item):
    if item.value == "ValidData":
        run_scripts('./start_desktop.sh')
    else:
        return {"message": "Error: Invalid data recieved"}
        

@router.post("/shut_down_desktop")
async def shut_down_desktop(item: Item):
    if item.value == 'ValidData':
        run_scripts('./shut_down_desktop.sh')
    else:
        return {"message": "Error: Invalid data recieved"}

@router.get("/ping")
async def ping():
    ip = "192.168.1.107"
    return {"detail": run_scripts(['./check_ip.sh', str(ip)])}

app.include_router(router)
#app.mount("/", StaticFiles(directory="build", html=True), name="static")
