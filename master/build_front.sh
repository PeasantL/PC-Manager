#!/bin/bash

# Check if the build folder exists, then remove it
if [ -d "./build" ]; then
  rm -rf ./build
fi

# Navigate to the 'front' directory
cd ../front || exit

# Run npm build
npm run build

# Move the build folder to the '../master' directory
mv ./build ../master/
