#!/bin/bash

# Variables
label="TMI_Tests"
rpm=200
setoint=30
sudo_pass="raspberry"

echo "Starting melt experiemnt"
sudo python ~/Documents/wax/melt_client.py start melt $label,200,30
#sudo python ~/Documents/wax/melt_client.py start melt $label,$rpm,$setpoint
sleep 5
