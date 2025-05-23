#!/bin/bash

echo "Starting gpio daemon: sudo pigpiod"
sudo pigpiod

echo "Starting melt server"
sudo python ~/Documents/wax/melt_server.py
