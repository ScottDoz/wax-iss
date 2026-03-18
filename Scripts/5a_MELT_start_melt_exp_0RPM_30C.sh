#!/bin/bash

# Variables
label="TMI_Tests"
rpm=0
setoint=30
sudo_pass="raspberry"

echo "Starting melt experiemnt"
sudo python ~/wax-iss/wax/melt_client.py start melt $label,0,30
#sudo python ~/wax-iss/wax/melt_client.py start melt $label,$rpm,$setpoint
sleep 5
