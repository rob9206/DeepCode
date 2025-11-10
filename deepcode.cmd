@echo off
setlocal

rem Determine repository root so the script works from anywhere
set "SCRIPT_DIR=%~dp0"

if not exist "%SCRIPT_DIR%deepcode.py" (
    echo DeepCode launcher not found in "%SCRIPT_DIR%".
    exit /b 1
)

python "%SCRIPT_DIR%deepcode.py" %*
