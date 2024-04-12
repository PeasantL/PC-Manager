@echo off
REM Check if the activate script exists
IF EXIST ".venv\Scripts\activate.bat" (
    CALL .venv\Scripts\activate.bat
) ELSE (
    echo Virtual environment does not exist. Creating virtual environment
    python -m venv .venv
    CALL .venv\Scripts\activate.bat
)

echo Checking Dependencies
pip install -r requirements.txt
echo Running Server

IF "%1" == "--dev" (
    SET APP_MODE=dev
    REM Run Uvicorn with hot reload and more CORS options for development
    uvicorn app:app --reload --host 0.0.0.0 --port 8001
) ELSE (
    REM Run Uvicorn normally without hot reload for production
    uvicorn app:app --host 0.0.0.0 --port 80
)
