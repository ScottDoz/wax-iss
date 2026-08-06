#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Testing CAL controller"
supy ~/wax-iss/tests/calcontroller/test_controller.py

# Keep terminal open
exec bash
