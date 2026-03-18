#!/bin/bash

echo "SOLO Set load speed 200 RPM"
sudo python ~/wax-iss/wax/melt_client.py set_target_load_speed 200
sleep 5 
