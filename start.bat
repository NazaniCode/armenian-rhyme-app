@echo off
REM Armenian Rhyme Finder - Quick Start for Windows

echo ======================================
echo Armenian Rhyme Finder - Quick Start
echo ======================================
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python not found. Please install Python 3.7+
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK %PYTHON_VERSION% found

REM Check if requirements are installed
echo.
echo Checking dependencies...
python -c "import flask; import flask_cors" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo X Failed to install dependencies
        pause
        exit /b 1
    )
)
echo OK Dependencies installed

REM Check if dictionary exists
echo.
echo Checking dictionary file...
if exist "dictionary-hy.reordered.jsonl" (
    echo OK dictionary-hy.reordered.jsonl found
) else (
    echo X dictionary-hy.reordered.jsonl not found in current directory
    pause
    exit /b 1
)

REM Start the backend
echo.
echo Starting backend server...
echo.
title Armenian Rhyme Finder - Backend Server
python backend.py

pause
