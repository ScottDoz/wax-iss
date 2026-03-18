#!/bin/bash

echo "SOLO Stopping log motor speed"
sudo python ~/wax-iss/wax/melt_client.py stop_log_motor
sleep 5 
