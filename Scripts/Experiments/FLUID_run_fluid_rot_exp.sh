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
echo "Starting fluid rotation experiemnt"
#sudo python ~/wax-iss/wax/melt_client.py start_log_exp $label,"Fluid","$rpm","$setpoint" # Lights, camera, data log
supy ~/wax-iss/wax/melt_client.py start_log_preview_exp $label,"Fluid","$rpm","$setpoint" # Lights, camera, data log
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

# Speed = 10 RPM ------------------------------------------------------

rpm=10

# Individual time-based st-curve profiles

# Profile A-1
T13=10.0
T2=0.0
echo "10 RPM Profile A-1: T1=T3=$T13 s, T2=$T2 s"
supy ~/wax-iss/wax/melt_client.py set_motor_mode_st_time_based "$T13","$T2" # Mode 2: St-curve time-based
sleep 1
supy ~/wax-iss/wax/melt_client.py set_target_load_speed "$rpm" # Ramp up motors
SLEEP_TIME=$(awk "BEGIN {print 2 * $T13 + $T2 + 10}")
sleep "$SLEEP_TIME" # Wait until ramped up, hold for 10 sec
supy ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
SLEEP_TIME=$(awk "BEGIN {print 2 * $T13 + $T2 + 5}")
sleep "$SLEEP_TIME" # Wait until ramped down, hold for 5 sec

# Speed = 50 RPM ------------------------------------------------------

rpm=50

# Profile A-1
T13=10.0
T2=0.0
echo "50 RPM Profile A-1: T1=T3=$T13 s, T2=$T2 s"
supy ~/wax-iss/wax/melt_client.py set_motor_mode_st_time_based "$T13","$T2" # Mode 2: St-curve time-based
sleep 1
supy ~/wax-iss/wax/melt_client.py set_target_load_speed "$rpm" # Ramp up motors
SLEEP_TIME=$(awk "BEGIN {print 2 * $T13 + $T2 + 10}")
sleep "$SLEEP_TIME" # Wait until ramped up, hold for 10 sec
supy ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
SLEEP_TIME=$(awk "BEGIN {print 2 * $T13 + $T2 + 5}")
sleep "$SLEEP_TIME" # Wait until ramped down, hold for 5 sec

# Speed = 100 RPM ------------------------------------------------------

rpm=100

# Profile A-1
T13=10.0
T2=0.0
echo "100 RPM Profile A-1: T1=T3=$T13 s, T2=$T2 s"
supy ~/wax-iss/wax/melt_client.py set_motor_mode_st_time_based "$T13","$T2" # Mode 2: St-curve time-based
sleep 1
supy ~/wax-iss/wax/melt_client.py set_target_load_speed "$rpm" # Ramp up motors
SLEEP_TIME=$(awk "BEGIN {print 2 * $T13 + $T2 + 15}")
sleep "$SLEEP_TIME" # Wait until ramped up, hold for 10 sec
supy ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
SLEEP_TIME=$(awk "BEGIN {print 2 * $T13 + $T2 + 10}")
sleep "$SLEEP_TIME" # Wait until ramped down, hold for 5 sec

# Speed = 150 RPM ------------------------------------------------------

rpm=150

# Profile A-1
T13=10.0
T2=0.0
echo "150 RPM Profile A-1: T1=T3=$T13 s, T2=$T2 s"
supy ~/wax-iss/wax/melt_client.py set_motor_mode_st_time_based "$T13","$T2" # Mode 2: St-curve time-based
sleep 1
supy ~/wax-iss/wax/melt_client.py set_target_load_speed "$rpm" # Ramp up motors
SLEEP_TIME=$(awk "BEGIN {print 2 * $T13 + $T2 + 15}")
sleep "$SLEEP_TIME" # Wait until ramped up, hold for 10 sec
supy ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
SLEEP_TIME=$(awk "BEGIN {print 2 * $T13 + $T2 + 10}")
sleep "$SLEEP_TIME" # Wait until ramped down, hold for 5 sec


# OLD: Constant accel ramp
#sudo python ~/wax-iss/wax/melt_client.py motor_ramp_updown_const_accel "50" # Motion profile 50 RPM
#sleep 1
#sudo python ~/wax-iss/wax/melt_client.py motor_ramp_updown_const_accel "100" # Motion profile 100 RPM
#sleep 1

# Stop script
echo "Stopping fluid rotation experiemnt"
supy ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
echo "Ramping down motor"
sleep 1 # Sleep
supy ~/wax-iss/wax/melt_client.py stop_log_exp # Stop data log, turn off lights, camera
echo "Stopping lights, camera, data log"
sleep 5
echo "Fluid rotation complete"
