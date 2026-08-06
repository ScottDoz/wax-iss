#!/bin/bash

sudo pigpiod

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Testing GPIOs"
supy ~/wax-iss/tests/gpio/test_gpios.py

# Keep terminal open
exec bash
