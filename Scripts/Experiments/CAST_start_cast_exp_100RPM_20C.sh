#!/bin/bash

# Variables
label="TMI_Tests"
rpm=100
setpoint=20
sudo_pass="raspberry"

echo "Starting casting experiemnt"
sudo python ~/wax-iss/wax/melt_client.py start_log_exp $label,"Cast","$rpm","$setpoint" # Lights, camera, data log
sleep 3
sudo python ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint
sleep 1
sudo python ~/wax-iss/wax/melt_client.py set_target_load_speed "$rpm" # Ramp up motors
sleep 10
