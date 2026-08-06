#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Reading cal temp and setpoint"
supy ~/wax-iss/wax/melt_client.py get_temp_and_setpoint
sleep 5 

# Keep terminal open on error
#exec bash
if [ $? -ne 0 ]; then
	echo "***********************"
	echo "!!! Error Detected!!!!"
	read -p "Press [ENTER] to close the terminal..."
	exit 1
else
	exit 0
fi
