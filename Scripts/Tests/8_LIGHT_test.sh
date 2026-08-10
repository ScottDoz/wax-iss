#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Light test. Turning on and off."
supy ~/wax-iss/tests/neopixel/lighttest.py

# Keep terminal open
exec bash
