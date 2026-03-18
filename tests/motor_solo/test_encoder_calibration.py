# Title: SoloPy
# Motor Test
# ----------

# Test running the sensor calibration

import SoloPy as solo

import time

# Instanciate a SOLO object:
# check with SOLO motion terminal that you are able to connect to your device 
# and make sure the port name in the code is the correct one 
mySolo = solo.SoloMotorControllerUart("/dev/ttyACM0", 0, solo.UartBaudRate.RATE_937500)


# wait here till communication is established
print("Trying to Connect To SOLO")
communication_is_working = False
while communication_is_working is False:
    time.sleep(1)
    communication_is_working, error = mySolo.communication_is_working()
print("Communication Established succuessfully!")


# Run calibration
mySolo.sensor_calibration(1) # 1 = Incremental encoder start calibration

time.sleep(30)

mySolo.sensor_calibration(0) # 0 = Stop calibration

