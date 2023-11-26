@echo off
REM Check if the dist exists
set DIST=.\{{project_name}}-pyprojecttemplate-v0.1.0-win-x64-installer.exe
if not exist "%DIST%" (
    echo Dist does not exist.
    exit /b
)
echo Running installer %DIST%...
%DIST%
echo Installation complete. Press any key to exit.
pause
