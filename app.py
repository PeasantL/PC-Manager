import subprocess
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles


app = FastAPI()
router = APIRouter()

"""
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""


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



@router.get("/start_desktop")
async def start_desktop():
    run_scripts('./start_desktop.sh')
    
@router.get("/shut_down_desktop")
async def shut_down_desktop():
    run_scripts('./shut_down_desktop.sh')


app.include_router(router)
app.mount("/", StaticFiles(directory="build", html=True), name="static")
