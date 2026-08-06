#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Starting gpio daemon: sudo pigpiod"
sudo pigpiod

echo "Starting melt server"
supy ~/wax-iss/wax/melt_server.py

# Keep terminal open
exec bash
