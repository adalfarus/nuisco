#!/bin/bash

# Building the project.
nuisco build --src=./src/ --out=./build/ --inLibs=PySide6 --enablePlugins=pyside6 --p=2 --extraArgs=select-dll,urllib3-module,hmac-module,email-module

# Wait for user input before proceeding.
read -p "Press enter to continue"
