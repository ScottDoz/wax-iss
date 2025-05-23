#!/bin/bash

echo "Pausing motor rotation"
sudo python ~/wax-iss/wax/melt_client.py pause rotation
sleep 5 
