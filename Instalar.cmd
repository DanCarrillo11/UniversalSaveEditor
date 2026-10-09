@echo off
setlocal
cd /d "%~dp0"
python -m venv .venv
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
echo UniversalSaveEditor esta listo. Abre Iniciar.cmd.
pause
exit /b 0
:error
echo No se pudo instalar. Necesitas Python 3.10 o posterior y conexion a internet.
pause
exit /b 1
