#!/bin/bash

echo "SOLO Stop motor rotation"
sudo python ~/wax-iss/wax/melt_client.py stop_rotation
sleep 5 
