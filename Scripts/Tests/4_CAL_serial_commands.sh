#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Testing CAL controller"
supy ~/wax-iss/tests/calcontroller/test_serial_read_setpoint_temp.py
sleep 15

# Keep terminal open
exec bash
