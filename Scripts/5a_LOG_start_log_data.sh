#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Starting log data"
supy ~/wax-iss/wax/melt_client.py start_log_data
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
