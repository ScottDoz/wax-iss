#!/bin/bash

# Activate plotenv
#source ~/Documents/myenv/bin/activate
source ~/Documents/plotenv/bin/activate

echo "Plotting latest cast experiment"
python3 ~/wax-iss/wax/plot_latest_cast.py

# Keep terminal open
exec bash
