#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Exiting melt server"
supy ~/wax-iss/wax/melt_client.py exit

# Keep terminal open
exec bash
