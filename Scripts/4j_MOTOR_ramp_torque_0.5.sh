#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Ramping torque Iq: 0.5A in 5 s"
supy ~/wax-iss/wax/melt_client.py ramp_torque_reference_iq 0.5, 5
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
