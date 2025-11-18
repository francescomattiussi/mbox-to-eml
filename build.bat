@echo off
REM This batch file builds the mbox_to_eml_gui.py script into an executable using PyInstaller.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>nul
IF ERRORLEVEL 1 (
    echo PyInstaller is not installed. Please install it using 'pip install pyinstaller'.
    exit /b 1
)

REM Build the executable
pyinstaller --onefile --windowed src\mbox_to_eml_gui.py

REM Check if the build was successful
IF ERRORLEVEL 1 (
    echo Build failed. Please check the output for errors.
    exit /b 1
)

echo Build completed successfully. The executable can be found in the 'dist' directory.