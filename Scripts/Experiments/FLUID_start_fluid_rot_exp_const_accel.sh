#!/bin/bash

# Variables
label="TMI_Tests"
accel=20 # Acceleration/deceleration value (rev/s/s)
rpm=100
setpoint=20
sudo_pass="raspberry"

echo "Starting fluid rotation experiemnt"
sudo python ~/wax-iss/wax/melt_client.py start_log_exp $label,"Fluid","$rpm","$setpoint" # Lights, camera, data log
sleep 3
sudo python ~/wax-iss/wax/melt_client.py set_solo_accel "$accel" # Set acceleration 
sudo python ~/wax-iss/wax/melt_client.py set_solo_decel "$accel" # Set deceleration 
sleep 1
sudo python ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint (turn off)
sleep 1
sudo python ~/wax-iss/wax/melt_client.py motor_ramp_updown_const_accel "50" # Motion profile 50 RPM
sleep 1
sudo python ~/wax-iss/wax/melt_client.py motor_ramp_updown_const_accel "100" # Motion profile 100 RPM
sleep 1
