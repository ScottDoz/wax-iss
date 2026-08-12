#!/bin/bash

# Exit if any command fails
set -e

# Environment location
ENV_DIR="$HOME/Documents/myenv"

# Create virtual environment if it does not exist
if [ ! -d "$ENV_DIR" ]; then
	echo "Creating virtual environment ..."
	python3 -m venv --system-site-packages ~/Documents/myenv
	
	
	
else
	echo "Virtual environment already exists."
fi

# Create supy executable
cat > "$ENV_DIR/bin/supy" <<'EOF'
#!/bin/bash
exec sudo "$VIRTUAL_ENV/bin/python3" "$@"
EOF
# Make it executable
chmod +x "$ENV_DIR/bin/supy"
echo "Created $ENV_DIR/bin/supy"

# Activate environment
source "$ENV_DIR/bin/activate"

# Upgrade pip
python -m pip install --upgrade pip

# Other packages
pip3 install pymodbus==2.5.3
pip3 install SoloPy
#pip3 install numpy==2.0.2
pip3 install pandas #==2.2.3
pip3 install matplotlib #==3.9.4
pip3 install picamera2==0.3.31

pip3 install numpy==1.26.0

# FIXME: some error in picamera2
# Was initially working, now not. Dependencies conflicts?

# Neopixel Setup -------------------------------------------------------

# Install adafruit packages
pip3 install adafruit-circuitpython-neopixel
python3 -m pip install adafruit-blinka
pip3 install --upgrade adafruit-python-shell
pip3 install adafruit-circuitpython-max31865


# Download and blinka test
wget -P ~/Documents http://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo -E env PATH=$PATH python3 ~/Documents/raspi-blinka.py
