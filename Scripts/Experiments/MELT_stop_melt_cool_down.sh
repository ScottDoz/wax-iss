#!/bin/bash

# Variables
setpoint=20 # New temperature setpoint at room temperature

echo "Stopping melt script"
sudo python ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint
sleep 3 # Sleep
sudo python ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
echo "Ramping down motor"
sleep 10 # Sleep
sudo python ~/wax-iss/wax/melt_client.py stop_log_exp # Stop data log, turn off lights, camera
echo "Stopping lights, camera, data log"
sleep 5
echo "Melt complete"
