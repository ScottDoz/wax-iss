#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Camera metadata"
supy ~/wax-iss/wax/melt_client.py get_camera_metadata
sleep 10

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
