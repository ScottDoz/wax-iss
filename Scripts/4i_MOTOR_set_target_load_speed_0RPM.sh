#!/bin/bash

echo "SOLO Set load speed 0 RPM"
sudo python ~/wax-iss/wax/melt_client.py set_target_load_speed 0
sleep 5 
