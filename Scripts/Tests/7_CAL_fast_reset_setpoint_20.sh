#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

#echo "Resetting CAL controller setpoint"
supy ~/wax-iss/tests/calcontroller/test_fast_reset_setpoint_20C.py

# Keep terminal open
exec bash
