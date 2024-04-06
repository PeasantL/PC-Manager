#!/bin/bash

# Navigate to your project directory, replace /path/to/your/project with the actual path
cd ../front

# Run the build command
echo "Starting build..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful. Starting to copy files..."

    # Copy the build directory to the remote server
    # Replace /path/to/build with the path to your build directory
    # Replace user@remote_server with your actual username and server IP or domain
    # Replace /path/on/remote/server with the actual path where you want to copy the build
    scp -r build pi@192.168.1.143:peasant-house

    if [ $? -eq 0 ]; then
        echo "Files copied successfully."
    else
        echo "Error occurred during file copy."
    fi
else
    echo "Build failed. Aborting file copy."
fi
