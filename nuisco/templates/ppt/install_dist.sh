#!/bin/bash

# Define the tar.gz file and the target directory for installation
TAR_FILE="{{project_name}}-pyprojecttemplate-0.1.0.tar.gz"
INSTALL_DIR="/usr/local/bin"

# Extract the tar.gz file to the installation directory
tar -xzvf "$TAR_FILE" -C "$INSTALL_DIR"

# Check if the extraction was successful
if [ $? -ne 0 ]; then
    echo "Failed to extract $TAR_FILE"
    exit 1
fi

# Create a symbolic link (shortcut) in the original location
# This assumes the main executable is named 'app_executable'
ln -s "$INSTALL_DIR/app_executable" "./app_shortcut"

# Notify user
echo "Application installed to $INSTALL_DIR"
echo "Shortcut created in the current directory."

# Pause for user input
read -p "Press enter to continue"
