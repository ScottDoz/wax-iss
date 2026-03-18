#!/bin/bash

# Variables
label="TMI_Tests"
setoint=30
sudo_pass="raspberry"

echo "Starting fluid rotation experiment"
sudo python ~/wax-iss/wax/melt_client.py start cfluid experiment $label,"/home/pi/wax-iss/wax/rpm_profile_500RPM.csv",20
sleep 10
