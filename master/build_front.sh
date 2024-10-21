#!/bin/bash

# Remove the build folder in the current directory
rm -rf ./build

# Navigate to the 'front' directory
cd ../front || exit

# Run npm build
npm run build

# Move the build folder to the '../master' directory
mv ./build ../master/
