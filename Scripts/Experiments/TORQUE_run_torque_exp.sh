#!/bin/bash

# Variables
label="TMI_Tests_16Sept2026"
accel=20 # Acceleration/deceleration value (rev/s/s)
rpm=100
setpoint=20
sudo_pass="raspberry"

# Activate venv
source ~/Documents/myenv/bin/activate

# Start logging
echo "Starting torque experiemnt"
#sudo python ~/wax-iss/wax/melt_client.py start_log_exp $label,"Fluid","$rpm","$setpoint" # Lights, camera, data log
supy ~/wax-iss/wax/melt_client.py start_log_preview_exp $label,"Torque","$rpm","$setpoint" # Lights, camera, data log
sleep 3

# Reset motor current limit to 5A
echo "Setting current limit to 5A"
supy ~/wax-iss/wax/melt_client.py set_current_limit 5
sleep 1

# Turn heater off
supy ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint (turn off)
sleep 1
supy ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint (turn off) # Run again to make sure
sleep 1

# Set torque mode ---------------------------------------------------------

supy ~/wax-iss/tests/motor_solo/test_motor_torque.py


# Reset to speed mode ------------------------------------------------------

# Profile A-1
T13=10.0
T2=0.0

echo "100 RPM Profile A-1: T1=T3=$T13 s, T2=$T2 s"
supy ~/wax-iss/wax/melt_client.py set_motor_mode_st_time_based "$T13","$T2" # Mode 2: St-curve time-based

# Stop script
echo "Stopping fluid rotation experiemnt"
supy ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
echo "Ramping down motor"
sleep 1 # Sleep
supy ~/wax-iss/wax/melt_client.py stop_log_exp # Stop data log, turn off lights, camera
echo "Stopping lights, camera, data log"
sleep 5
echo "Fluid rotation complete"
