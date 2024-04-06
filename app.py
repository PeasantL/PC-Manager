import subprocess
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


app = FastAPI()
router = APIRouter()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

def run_scripts(script_path):
    process = subprocess.Popen([script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        print("Script executed successfully")
        print(stdout.decode())
    else:
        print("Script execution failed")
        print(stderr.decode())


@router.get("/test")
async def test():
    print("Hello World")
    return {"message": "Foo Bar"}

class Item(BaseModel):
    value: str

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


app.include_router(router)