@echo off

REM Building the project.
nuisco build --src=./src/ --out=./build/ --inLibs=PySide6 --enablePlugins=pyside6 --p=2 --extraArgs=select-dll,urllib3-module,hmac-module,email-module

REM Wait for the user input brefore proceeding.
pause
