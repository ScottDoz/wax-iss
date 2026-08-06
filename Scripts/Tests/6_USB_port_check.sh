#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

supy ~/wax-iss/tests/check_usb_ports.py

# Keep terminal open
exec bash
