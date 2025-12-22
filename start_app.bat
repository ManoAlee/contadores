@echo off
REM Lança a GUI do app. Mantenha este .bat na raiz do repositório.
REM Uso:
REM   start_app.bat            -> abre o launcher Python (padrão)
REM   start_app.bat psgui     -> abre o launcher PowerShell (UI nativa)
REM   start_app.bat test      -> executa fluxo de teste (gera rascunho via CLI)

set SCRIPT_DIR=%~dp0
set VENV_PY=%SCRIPT_DIR%.venv\Scripts\python.exe

if "%1"=="psgui" (
	echo Abrindo PowerShell GUI launcher...
	start "Contadores - PS GUI" powershell -NoProfile -STA -ExecutionPolicy Bypass -File "%SCRIPT_DIR%app\scripts\ps_gui_launcher.ps1"
	goto :eof
)

if "%1"=="test" (
	echo Executando teste: gerando rascunho via CLI...
	if exist "%VENV_PY%" (
		echo Using Python: "%VENV_PY%"
		"%VENV_PY%" -c "import sys; print('sys.executable->', sys.executable)"
		"%VENV_PY%" -u "%SCRIPT_DIR%app\scripts\cli_launcher.py" draft --email "%SCRIPT_DIR%app\data\incoming_email.txt" --ips "%SCRIPT_DIR%app\data\ips.txt" --out "%SCRIPT_DIR%app\data"
	) else (
		echo Using system python
		python -c "import sys; print('sys.executable->', sys.executable)"
		python -u "%SCRIPT_DIR%app\scripts\cli_launcher.py" draft --email "%SCRIPT_DIR%app\data\incoming_email.txt" --ips "%SCRIPT_DIR%app\data\ips.txt" --out "%SCRIPT_DIR%app\data"
	)
	echo Teste finalizado.
	pause
	goto :eof
)

REM Sem argumentos: comportamento original - tentar abrir o launcher Python GUI
if exist "%VENV_PY%" (
	echo Using Python: "%VENV_PY%"
	"%VENV_PY%" -c "import sys; print('sys.executable->', sys.executable)"
	"%VENV_PY%" -u "%SCRIPT_DIR%app\gui\launcher.py"
) else (
	echo Using system python
	python -c "import sys; print('sys.executable->', sys.executable)"
	python -u "%SCRIPT_DIR%app\gui\launcher.py"
)
pause
