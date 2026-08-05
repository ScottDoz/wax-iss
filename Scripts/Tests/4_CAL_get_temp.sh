#!/bin/bash

echo "Testing CAL controller"
sudo python ~/wax-iss/tests/calcontroller/test_controller.py

# Keep terminal open
exec bash
