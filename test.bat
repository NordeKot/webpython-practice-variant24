@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo Run setup.bat first.
    pause
    exit /b 1
)
.venv\Scripts\python.exe -m pycodestyle --max-line-length=79 src tests
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pycodestyle --select=W505 --max-doc-length=72 src tests
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m ruff check .
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m coverage erase
.venv\Scripts\python.exe -m coverage run -m pytest -q
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m coverage report -m
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m coverage html
if errorlevel 1 goto fail
echo Open htmlcov\index.html to view coverage.
pause
exit /b 0
:fail
echo Check failed. Copy the output and send it for help.
pause
exit /b 1
