#!/bin/bash

# Variables
setpoint=20 # New temperature setpoint at room temperature

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Stopping melt script"
supy ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint
sleep 1 # Sleep
supy ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint (Run again to be sure)
sleep 3 # Sleep
supy ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
echo "Ramping down motor"
sleep 30 # Sleep
supy ~/wax-iss/wax/melt_client.py stop_log_exp # Stop data log, turn off lights, camera
echo "Stopping lights, camera, data log"
sleep 5
echo "Melt complete"
