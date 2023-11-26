@echo off
REM Check if the build directory exists and is not empty
set BUILD_DIR=.\build\
if not exist "%BUILD_DIR%" (
    echo Build directory does not exist.
    exit /b
)
dir /b /a-d "%BUILD_DIR%" | findstr "^" >nul || (
    echo Build directory is empty.
    exit /b
)

REM Path to your Inno Setup script file
set INNO_SCRIPT=inno_setup_script.iss

REM Compile the Inno Setup script
ISCC.exe "%INNO_SCRIPT%"

REM Pause the script to view any output messages
pause
