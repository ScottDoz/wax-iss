#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Setting torque Iq: 3.0A"
supy ~/wax-iss/wax/melt_client.py set_torque_reference_iq 3.0
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
