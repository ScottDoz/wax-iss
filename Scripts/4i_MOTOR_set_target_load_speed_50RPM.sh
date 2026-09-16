#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "SOLO Set load speed 100 RPM"
supy ~/wax-iss/wax/melt_client.py set_target_load_speed 50
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
