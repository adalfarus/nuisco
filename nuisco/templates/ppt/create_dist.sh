#!/bin/bash
# Basic script to package an application in Unix-like systems

# Define the build directory and the output file
BUILD_DIR="./build"
OUTPUT_FILE="{{project_name}}-pyprojecttemplate-0.1.0.tar.gz"

# Check if the build directory exists and is not empty
if [ ! -d "$BUILD_DIR" ]; then
    echo "Build directory does not exist."
    exit 1
fi

if [ -z "$(ls -A $BUILD_DIR)" ]; then
    echo "Build directory is empty."
    exit 1
fi

# Package the application
tar -czvf "$OUTPUT_FILE" -C "$BUILD_DIR" .

# Notify user
echo "Application packaged into $OUTPUT_FILE"
