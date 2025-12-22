@echo off
REM start_gui.bat
REM Launches the Contadores Impressoras GUI
REM Automatically activates venv if present

set SCRIPT_DIR=%~dp0
set VENV_PY=%SCRIPT_DIR%.venv\Scripts\python.exe

echo Iniciando Contadores Impressoras...

if exist "%VENV_PY%" (
    echo Using VirtualEnv Python: "%VENV_PY%"
    start "" "%VENV_PY%" "%SCRIPT_DIR%run.py"
) else (
    echo [WARN] VirtualEnv not found at .venv. Using system python.
    echo Recomenda-se criar o venv: python -m venv .venv
    start "" /WAIT python "%SCRIPT_DIR%run.py"
)

pause
