@echo off
echo Setting up virtual environment for SPCA Maps...

REM Check if Python 3.9 is available
python3.9 --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python3.9
) else (
    python3 --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_CMD=python3
        echo Warning: Using python3 instead of python3.9
    ) else (
        echo Error: Python 3 not found. Please install Python 3.9 or later.
        pause
        exit /b 1
    )
)

REM Create virtual environment
echo Creating virtual environment...
%PYTHON_CMD% -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install exact package versions
echo Installing packages with exact versions...
pip install -r requirements.txt

echo Virtual environment setup complete!
echo To activate the environment, run: venv\Scripts\activate.bat
echo To run the app, run: streamlit run app.py
pause 