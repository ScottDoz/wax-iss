#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "SOLO Hide motor speed"
supy ~/wax-iss/wax/melt_client.py hide_motor_speed
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
