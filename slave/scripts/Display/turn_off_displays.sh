#!/bin/bash

# Set the display variable (adjust as needed)
export DISPLAY=:0
export XAUTHORITY=/run/user/$(id -u)/gdm/Xauthority

# Turn off both monitors
xrandr --output DP-2 --off
xrandr --output HDMI-0 --off

