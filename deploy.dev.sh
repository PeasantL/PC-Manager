#!/bin/bash

cd ./front

# Run the build command
echo "Starting build..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful. Starting to copy files..."

    scp -r build peasantl@192.168.0.108:pc-manager-server
    cd ..
    #Copy the contents of server to the destination
    scp -r server/* peasantl@192.168.0.108:pc-manager-server

    if [ $? -eq 0 ]; then
        echo "Files copied successfully."
    else
        echo "Error occurred during file copy."
    fi
else
    echo "Build failed. Aborting file copy."
fi
