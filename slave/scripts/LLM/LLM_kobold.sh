#!/bin/bash

/home/peasantl/Documents/TextGen/custom_scripts/kill.sh

# Run tabbyAPI
gnome-terminal -- /home/peasantl/Documents/TextGen/koboldcpp/koboldcpp-linux-x64-cuda1210 /home/peasantl/Documents/TextGen/koboldcpp/config.kcpps &
# Run SillyTavern
cd /home/peasantl/Documents/TextGen/SillyTavern
gnome-terminal -- /home/peasantl/Documents/TextGen/SillyTavern/start.sh &
