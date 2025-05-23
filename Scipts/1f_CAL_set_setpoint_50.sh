#!/bin/bash

echo "Change Temp Setpoint"
sudo python ~/wax-iss/wax/melt_client.py set_setpoint 50
sleep 5 
