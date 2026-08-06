#!/bin/bash

# Activate venv
source ~/Documents/myenv/bin/activate

echo "Testing Video"
supy ~/wax-iss/tests/camera/test_video.py


# Keep terminal open
exec bash
