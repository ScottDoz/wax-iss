#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Lights color blue"
supy ~/wax-iss/wax/melt_client.py light_color 0,0,255

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
