#!/bin/bash

# Variables
label="TMI_Tests_21Aug2026"
rpm=100
setpoint=40
sudo_pass="raspberry"

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Starting melting experiemnt"
#sudo python ~/wax-iss/wax/melt_client.py start_log_exp $label,"Melt","$rpm","$setpoint" # Lights, camera, data log
supy ~/wax-iss/wax/melt_client.py start_log_preview_exp $label,"Melt","$rpm","$setpoint" # Lights, camera, data log
sleep 3
supy ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint
sleep 1
supy ~/wax-iss/wax/melt_client.py set_target_load_speed "$rpm" # Ramp up motors
sleep 10
