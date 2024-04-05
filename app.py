import subprocess
from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter()


def run_scripts(script_path):
    process = subprocess.Popen([script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        print("Script executed successfully")
        print(stdout.decode())
    else:
        print("Script execution failed")
        print(stderr.decode())


@router.get("/start_desktop")
async def start_desktop():
    run_scripts('./start_desktop.sh')
    
@router.get("/shut_down_desktop")
async def shut_down_desktop():
    run_scripts('./shut_down_desktop.sh')


app.include_router(router)