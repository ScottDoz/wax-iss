#!/bin/bash

# Variables
label="TMI_Tests_8Sept2026"
rpm=50
setpoint=65
sudo_pass="raspberry"

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Starting melting experiemnt"

# Start logging
supy ~/wax-iss/wax/melt_client.py start_log_preview_exp $label,"Melt","$rpm","$setpoint" # Lights, camera, data log
sleep 3

# Ramp up motors -------------------------------------------------------------
#echo "Ramping up motor"
#supy ~/wax-iss/wax/melt_client.py set_target_load_speed "$rpm" # Ramp up motor
#sleep 10

# Ramp up motors. ST-curve profile
T13=10
T2=0.0
echo "Ramping motor. Profile: T1=T3=$T13 s, T2=$T2 s"
supy ~/wax-iss/wax/melt_client.py set_motor_mode_st_time_based "$T13","$T2" # Mode 2: St-curve time-based
sleep 1
supy ~/wax-iss/wax/melt_client.py set_target_load_speed "$rpm" # Ramp up motors
SLEEP_TIME=$(awk "BEGIN {print 2 * $T13 + $T2 + 5}")
sleep "$SLEEP_TIME" # Wait until ramped up, hold for 5 sec

# Turn on heater -----------------------------------------------------------------
sleep 30 # Wait for motors to even out
echo "Enabling heaters."
supy ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint
sleep 1
supy ~/wax-iss/wax/melt_client.py set_setpoint "$setpoint" # Change CAL temperature setpoint # Send signal again to confirm
sleep 1