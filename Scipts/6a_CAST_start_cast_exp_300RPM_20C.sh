#!/bin/bash

# Variables
label="TMI_Tests"
rpm=300
setoint=20
sudo_pass="raspberry"

echo "Starting casting experiemnt"
sudo python ~/wax-iss/wax/melt_client.py start cast $label,300,20
#sudo python ~/wax-iss/wax/melt_client.py start cast $label,$rpm,$setpoint
sleep 10
