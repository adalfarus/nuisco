#!/bin/bash

# Define the build directory
BUILD_DIR="./build"

# Check if the build directory exists and is not empty
if [ ! -d "$BUILD_DIR" ] || [ -z "$(ls -A $BUILD_DIR)" ]; then
    echo "Build directory does not exist or is empty."
    exit 1
fi

# Copying files from build to a target directory
TARGET_DIR="/usr/local/bin/{{project_name}}"
mkdir -p "$TARGET_DIR"
cp -R "$BUILD_DIR/"* "$TARGET_DIR/"

echo "Installation complete."
