# Title: SoloPy
# Motor Test
# ----------

# Test control of the motor using SOLO mini via usb communication
# Code adapted from example code in SoloPy/examples/raspberry_pi/usb


import SoloPy as solo
import time
import configparser
import inspect


# INPUTS
# Target speed profile -----------------------------------
speedAccelValue = 5.0 # Speed acceleration value (rev/s/s)
speedDecelValue = 5.0 # Speed deceleration value (rev/s/s)
target_speed_shaft = 200. # Load speed (RPM)
# ---------------------------------------------------------

# Read config parser
config = configparser.ConfigParser()
config.read(r'/home/pi/wax-iss/wax/config.ini')
#print("Config files read:", files)
print("Config sections: ", config.sections())
#version = config['info']['experiment_id'] # Read experiment ID (which pi is this?)
CAL_port = config['serialports']['CAL_port'] # Read from config file
SOLO_port = config['serialports']['SOLO_port'] # Read from config file
TELEM_port = config['serialports']['TELEM_port'] # Read from config file
#SOLO_port = "/dev/ttyACM0"
print("CAL_port: ", CAL_port)
print("SOLO_port: ", SOLO_port)
print("TELEM_port: ", TELEM_port)
print("")

# Instanciate a SOLO object:
# check with SOLO motion terminal that you are able to connect to your device 
# and make sure the port name in the code is the correct one 
mySolo = solo.SoloMotorControllerUart(SOLO_port, 0, solo.UartBaudRate.RATE_937500)


# ----------------------------------------------------------------------

def decode_solo_errors(error_code):
    
    # Define error codes
    errors = {
                0: "Over-current error: current exceeded 62 A for > 0.1 ms",
                1: "Over-voltage error: BUS voltage exceeded 57 V for > 35 us",
                2: "Over-temperature error: board temperature exceeded 85 C",
                3: "Encoder calibration tmeout: index pulse is missing",
                4: "Hall sensor calibration timeout",
                5: "CAN communication lost: lifetime expired",
                6: "Stall timeout error",
                # Bit 7 is listed as N/A in the manual
            }
    
    # Reject invalid regiter value, including -1
    if not isinstance(error_code, int) or not 0 <= error_code <= 0xFFFFFFFF:
        print(f"Invalid fault register response: {error_code!r}")
        return []
    
    # No active errors
    if error_code == 0:
        print("No active faults.")
        return []
    
    # Print raw error code
    print(f"Raw Fault Code: 0x{error_code:08X}")
    
    active_errors = []
    
    for bit, description in errors.items():
        if error_code & (1 << bit):
            active_errors.append(description)
    
    if not active_errors:
        print("No recognized errors reported.")
    else:
        print(f"Fault register: 0x{error_code:08X}")
        print("Active errors:")
        for error in active_errors:
            print(f"  - {error}")
    
    
    return active_errors


# Read error register to identify what triggered the blinking red light
error_code, _ = mySolo.get_error_register()
print(error_code)
print(f"Active Fault Code: {hex(error_code)}")
print(f"Raw Fault Code: 0x{error_code:08X}")
decode_solo_errors(error_code)

# Clear the error
print("Clearing errors")
time.sleep(0.1)
success, _ = mySolo.overwrite_error_register()
time.sleep(1)

# Close connection
#print("Closing solo connection")
#mySolo.serial_close()
