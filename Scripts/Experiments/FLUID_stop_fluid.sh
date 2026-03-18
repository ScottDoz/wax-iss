#!/bin/bash

echo "Stopping fluid rotation script"
sudo python ~/wax-iss/wax/melt_client.py set_target_load_speed 0 # Stop rotation
echo "Ramping down motor"
sleep 1 # Sleep
sudo python ~/wax-iss/wax/melt_client.py stop_log_exp # Stop data log, turn off lights, camera
echo "Stopping lights, camera, data log"
sleep 5
echo "Fluid rotation complete"
