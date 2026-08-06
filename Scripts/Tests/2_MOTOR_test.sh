#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Testing Motor with SOLO controller"
supy ~/wax-iss/tests/motor_solo/test_motor_usb.py

# Keep terminal open
exec bash
