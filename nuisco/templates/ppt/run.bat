@echo off

REM Execute the python script.
py -{{pyversion}} ./src/main.py

REM Wait for user input before proceeding.
pause
