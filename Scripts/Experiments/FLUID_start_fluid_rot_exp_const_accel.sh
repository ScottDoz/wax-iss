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

# Stop script
echo "Stopping fluid rotation experiemnt"
sudo python ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
echo "Ramping down motor"
sleep 1 # Sleep
sudo python ~/wax-iss/wax/melt_client.py stop_log_exp # Stop data log, turn off lights, camera
echo "Stopping lights, camera, data log"
sleep 5
echo "Fluid rotation complete"
