#!/bin/bash

echo "Testing Thermocouples"
sudo python ~/wax-iss/tests/thermocouple/test_thermocouple.py

# Keep terminal open
exec bash
