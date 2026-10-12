@echo off
cd /d "%~dp0"
py -3.12 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install -e . -r requirements-dev.txt
if errorlevel 1 goto fail
echo Setup complete. Run run.bat demo or test.bat.
pause
exit /b 0
:fail
echo Setup failed. Copy the error text and send it for help.
pause
exit /b 1
