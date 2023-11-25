#!/bin/bash

# Execute the python script.
# Assuming Python 3.11 is installed and available in your system's PATH.
python{{pyversion}} ./src/main.py

# Wait for user input before proceeding.
read -p "Press enter to continue"
