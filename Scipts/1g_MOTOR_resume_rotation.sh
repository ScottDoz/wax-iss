#!/bin/bash

echo "Resuming motor rotation"
sudo python ~/wax-iss/wax/melt_client.py resume rotation
sleep 5 
