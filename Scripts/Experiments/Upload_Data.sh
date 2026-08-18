#!/bin/bash

# Activate venv
source ~/Documents/dataenv/bin/activate

# Run script and parse arguments
cd ~/wax-iss/wax/DataUpload
python GoogleDriveFolderUpload.py "$@"

# Keep terminal open
exec bash
