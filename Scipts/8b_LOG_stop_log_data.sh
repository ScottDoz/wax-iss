#!/bin/bash

echo "Stopping log data"
sudo python ~/wax-iss/wax/melt_client.py stop_log_data
sleep 10
