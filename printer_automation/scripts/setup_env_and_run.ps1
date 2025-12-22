# Script PowerShell para criar venv Python 3.11, instalar dependências e executar a consulta
param(
    [string]$venvName = '.venv311',
    [string]$requirements = '..\requirements.txt'
)

Write-Output "Criando/ativando venv $venvName"
if (-not (Test-Path $venvName)) {
    python -m venv $venvName
}

Write-Output "Ativando venv"
.\$venvName\Scripts\Activate.ps1

Write-Output "Instalando dependências"
pip install --upgrade pip
pip install -r $requirements

Write-Output "Executando consulta de impressoras"
python ..\src\get_printer_counters.py --ips ..\data\ips.txt --community public
