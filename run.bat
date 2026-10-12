@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%\src
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -m variant24 %*
) else (
    py -3.12 -m variant24 %*
)
