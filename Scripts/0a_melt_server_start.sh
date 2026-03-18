#!/bin/bash

echo "Starting gpio daemon: sudo pigpiod"
sudo pigpiod

echo "Starting melt server"
sudo python ~/wax-iss/wax/melt_server.py
