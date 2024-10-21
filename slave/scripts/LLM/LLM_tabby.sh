#!/bin/bash

/home/peasantl/Documents/TextGen/custom_scripts/kill.sh

# Run tabbyAPI
gnome-terminal -- /home/peasantl/Documents/TextGen/tabbyAPI/start.sh -iu &
# Run SillyTavern
cd /home/peasantl/Documents/TextGen/SillyTavern
gnome-terminal -- /home/peasantl/Documents/TextGen/SillyTavern/start.sh &