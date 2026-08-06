#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Stopping casting script"
supy ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
echo "Ramping down motor"
sleep 20 # Sleep
supy ~/wax-iss/wax/melt_client.py stop_log_exp # Stop data log, turn off lights, camera
echo "Stopping lights, camera, data log"
sleep 5
echo "Cast complete"
