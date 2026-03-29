$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$pythonExe = "E:\code\python312\python.exe"
$scriptPath = Join-Path $PSScriptRoot "hero_winrate_analysis_refactored.py"

& $pythonExe $scriptPath
