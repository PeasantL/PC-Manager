#!/bin/bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

export DISPLAY=:0

#/home/peasantl/Documents/TextGen/custom_scripts/kill.sh

# Run tabbyAPI
xterm -e /home/peasantl/Documents/TextGen/koboldcpp/koboldcpp-linux-x64-cuda1210 /home/peasantl/Documents/TextGen/koboldcpp/config.kcpps &
# Run SillyTavern
cd /home/peasantl/Documents/TextGen/SillyTavern
xterm -e /home/peasantl/Documents/TextGen/SillyTavern/start.sh &
