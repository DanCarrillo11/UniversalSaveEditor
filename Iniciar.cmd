@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Ejecuta primero Instalar.cmd para preparar UniversalSaveEditor.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" app.py
if errorlevel 1 pause
