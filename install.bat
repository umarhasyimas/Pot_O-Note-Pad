@echo off
setlocal

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Downloading Python...
    powershell -Command "Start-Process 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait"
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed. Installing pip...
    python -m ensurepip --upgrade
)

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed. Downloading Git...
    powershell -Command "Start-Process 'https://github.com/git-for-windows/git/releases/download/v2.39.2.windows.1/Git-2.39.2-64-bit.exe' -ArgumentList '/VERYSILENT' -Wait"
)

REM Clone the repository
if not exist "Pot-O_Note_Pad" (
    echo Cloning repository...
    git clone https://github.com/username/repository.git Pot-O_Note_Pad
)

REM Navigate to the script directory
cd Pot-O_Note_Pad

REM Install dependencies and run the script
python Pot-O_Note_Pad_v0.0.1-beta.py

echo Installation complete!
pause
