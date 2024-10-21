#!/bin/bash

# Turn on the primary large monitor with saved position and resolution
xrandr --output DP-2 --mode 5120x1440 --rate 120 --primary --pos 0x0

# Set the portrait monitor with saved position
xrandr --output HDMI-0 --rotate right --mode 2560x1080 --pos 5120x0

