#!/bin/bash

echo "Stopping camera"
sudo python ~/wax-iss/wax/melt_client.py stop_camera
sleep 10
