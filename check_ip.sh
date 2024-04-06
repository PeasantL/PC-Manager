#!/bin/bash

if ping -c 1 -W 0.1 $1 >/dev/null; then
    exit 0;
else
    exit 1;
fi
