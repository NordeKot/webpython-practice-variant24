@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%\src
py -m variant24 %*
