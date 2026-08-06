#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Testing Thermocouples"
supy ~/wax-iss/tests/thermocouple/test_thermocouple.py

# Keep terminal open
exec bash
