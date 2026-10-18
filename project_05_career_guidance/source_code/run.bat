@echo off
title Career Guidance ML AI System
echo ====================================================================
echo           Career Guidance & Job Role Recommendation AI
echo ====================================================================
echo.

set PYTHON_EXE=

if exist "D:\vicky folder\cropai-main\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=D:\vicky folder\cropai-main\.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=python"
    ) else (
        where py >nul 2>nul
        if %errorlevel% equ 0 (
            set "PYTHON_EXE=py"
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python was not found on your system!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo Using Python: %PYTHON_EXE%
echo Installing / checking requirements...
"%PYTHON_EXE%" -m pip install -r requirements.txt --quiet >nul 2>&1

echo.
echo Starting Career Guidance Web Application...
echo Opening http://localhost:5055 in your browser...
start "" http://localhost:5055
"%PYTHON_EXE%" app.py
pause
