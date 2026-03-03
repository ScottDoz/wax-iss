#!/bin/bash

echo "SOLO Set load speed 100 RPM"
sudo python ~/wax-iss/wax/melt_client.py set_target_load_speed 100
sleep 5 
