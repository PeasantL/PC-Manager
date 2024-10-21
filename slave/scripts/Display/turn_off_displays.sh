#!/bin/bash

# Turn off the primary large monitor
xrandr --output DP-2 --off

# Reposition the portrait monitor
xrandr --output HDMI-0 --rotate right --pos 0x0

