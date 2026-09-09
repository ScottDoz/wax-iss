#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Stopping melt script. Maintaining speed and temp setpoints."

# Stop heating
#supy ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint
#sleep 1 # Sleep
#supy ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint (Run again to be sure)
#sleep 3 # Sleep

# Dont stop motor
#supy ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
#echo "Ramping down motor"
#sleep 20 # Sleep


# Stop logging/recording
echo "Stopping lights, camera, data log"
supy ~/wax-iss/wax/melt_client.py stop_log_exp # Stop data log, turn off lights, camera
sleep 5
echo "Melt complete"
