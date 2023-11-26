@echo off
setlocal

REM Define the build directory
set BUILD_DIR=.\build

REM Check if the build directory exists and is not empty
if not exist "%BUILD_DIR%\*" (
    echo Build directory does not exist or is empty.
    exit /b
)

REM Copying files from build to a target directory
set TARGET_DIR=C:\Program Files\{{project_name}}
xcopy "%BUILD_DIR%\*" "%TARGET_DIR%" /E /I

echo Installation complete.
pause
