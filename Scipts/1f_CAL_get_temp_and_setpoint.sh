#!/bin/bash

echo "Spy temperature"
sudo python ~/wax-iss/wax/melt_client.py get_temp_and_setpoint
sleep 5 
