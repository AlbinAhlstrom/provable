# run.ps1 — PowerShell convenience wrapper to run python run.py
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$ScriptDir\.."
python run.py
