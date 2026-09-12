@echo off
setlocal
cd /d "%~dp0"

set "VENV_PY=%CD%\.venv\Scripts\python.exe"
set "PYTHON_CMD=python"
where py >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=py -3"

if not exist "%VENV_PY%" (
    %PYTHON_CMD% --version >nul 2>&1
    if errorlevel 1 (
        echo Python 3.11 or newer was not found.
        echo Install Python from https://www.python.org/downloads/ and run this file again.
        echo During installation, enable "Add python.exe to PATH".
        pause
        exit /b 1
    )

    echo First launch: creating the local environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo Could not create the local environment.
        pause
        exit /b 1
    )

    echo First launch: installing dependencies...
    "%VENV_PY%" -m pip install --disable-pip-version-check -r requirements.txt
    if errorlevel 1 (
        echo Could not install dependencies. Check the internet connection and run this file again.
        pause
        exit /b 1
    )
)

echo Starting Padel Match at http://127.0.0.1:8000
start "Padel Match server" cmd /k ""%VENV_PY%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000"
endlocal
