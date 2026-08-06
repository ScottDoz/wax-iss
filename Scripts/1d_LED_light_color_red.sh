#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Lights color red"
sudo python ~/wax-iss/wax/melt_client.py light_color 255,0,0

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
