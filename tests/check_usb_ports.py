'''
Test script for sending telemetry from Pi
Send a message every second. Print received messages.


To get port number, run
ls -l /dev/serial/by-id/

'''

import serial
import time
import configparser
import subprocess
from pymodbus.utilities import computeCRC
import SoloPy as solo
import pdb


# Read config parser
config = configparser.ConfigParser()
config.read(r'/home/pi/wax-iss/wax/config.ini')

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


# List USB ports
print("Available USB Ports")
print("===================")
result = subprocess.run("ls -l /dev/serial/by-id/", shell=True, capture_output=True, text=True)
text = result.stdout
print(result.stdout)

# Check CAL_port
if "/dev/serial/by-id/" in CAL_port:
	# Port defined by ID
	CAL_port_id = CAL_port.split("/dev/serial/by-id/")[1]
elif "/dev" in CAL_port:
	# Port defined by /dev/ttyxxx
	CAL_port_id = CAL_port.split("/dev/")[1]
if CAL_port_id in text:
	print("CAL_port is ok: ", CAL_port)
else:
	print("CAL_port not found in /dev/serial/by-id/")

# Check SOLO_port
if "/dev/serial/by-id/" in SOLO_port:
	# Port defined by ID
	SOLO_port_id = SOLO_port.split("/dev/serial/by-id/")[1]
elif "/dev" in SOLO_port:
	# Port defined by /dev/ttyxxx
	SOLO_port_id = SOLO_port.split("/dev/")[1]
if SOLO_port_id in text:
	print("SOLO_port is ok: ", SOLO_port)
else:
	print("SOLO_port not found in /dev/serial/by-id/")

# Check TELEM_port
if "/dev/serial/by-id/" in TELEM_port:
	# Port defined by ID
	TELEM_port_id = TELEM_port.split("/dev/serial/by-id/")[1]
elif "/dev" in TELEM_port:
	# Port defined by /dev/ttyxxx
	TELEM_port_id = TELEM_port.split("/dev/")[1]
if TELEM_port_id in text:
	print("TELEM_port is ok: ", TELEM_port)
else:
	print("TELEM_port not found in /dev/serial/by-id/")
print("")

# Telemetry ------------------------------------------------------------

print("Telemetry Connection")
print("====================")

# Open connection
try:
	ser_telem = serial.Serial(
		port=TELEM_port,
		baudrate=115200, # Data rate (from SpaceTango ICD document)
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		bytesize=serial.EIGHTBITS,
		timeout=1,
	)
	ser_telem.flush() #clear any junk data 
	print("Connection created")
	
except Exception as e:
	print("Error creating telemetry serial connection")
	print(e)

# Send message
time.sleep(1)
message = f"Hello from Raspberry Pi!"
print("Sending message: ", message)
try:
	ser_telem.write(message.encode('utf-8'))
except Exception as e:
	print("Error sending telemetry message")
	print(e)

# Close connection
time.sleep(1)
try:
	ser_telem.close()
	print("Telemetry connection closed")
except Exception as e:
	print("Error closing telemetry connection")
	print(e)
print("")


# CAL ------------------------------------------------------------------

def add_crc(message):
	crc = computeCRC(message)
	#separate crc into hi and low bytes
	crc_low = crc & 0xFF
	crc_hi = (crc >> 8) & 0xFF
	
	#append crc to message
	message_with_crc = message + bytes([crc_hi, crc_low])
	#print(hex(crc_low),hex(crc_hi))

	return message_with_crc


# Set the serial hexadecimal message to request temperature and setpoint data
temp_read_frame =     [0x01,0x03,0x00,0x1C,0x00,0x01,0x45,0xCC] #request frame for temperature
setpoint_read_frame = [0x01,0x03,0x00,0x7F,0x00,0x01,0xB5,0xD2] #request frame for setpoint temperature

temp_crc = add_crc(bytes([0x01,0x03,0x00,0x1C,0x00,0x01]))



print("CAL Controller Connection")
print("=========================")

# Open connection
try:
	ser_cal=serial.Serial(
		port=CAL_port, # Serial port /dev/ttyUSB0
		baudrate=9600,       # Data rate
		bytesize=serial.EIGHTBITS,      # Data bits
		stopbits =serial.STOPBITS_ONE,  # Stop bits
		parity = serial.PARITY_NONE,    # Parity
		timeout=1, # Timeout (s)
	)
	ser_cal.flush() #clear any junk data 
	print("Connection created")
	
except Exception as e:
	print("Error creating telemetry serial connection")
	print(e)


# Request temperature data
try:
	ser_cal.write(bytes(temp_read_frame)) #send the message to request data
	#print("sent request for temp")
	time.sleep(0.1) #wait 0.1 seconds
except Exception as e:
	print("Error writing temp_read_frame")
	print(e)

if ser_cal.in_waiting>0:
	
	try:
		buf = ser_cal.read(ser_cal.in_waiting) #read all available bytes
		#print('recieved: ',buf.hex())
	except Exception as e:
		print("Error reading temp_read_frame buffer")
		print(e)
	
	# Decode temperature response
	try:
		temp_value=buf[4]
		#temperature=temp_value/10.0
		temp = ((buf[3]<<8)+buf[4])/10.0
	except Exception as e:
		print("Error decoding buffer")
		print(e)

	
	# Request setpoint data
	try:
		ser_cal.write(bytes(setpoint_read_frame)) # Send the message to request data
		time.sleep(0.1) #wait 0.1 seconds
	except Exception as e:
		print("Error writing setpoint_read_frame")
		print(e)
	
	if ser_cal.in_waiting>0:
		
		try:
			buf = ser_cal.read(ser_cal.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())
		except Exception as e:
			print("Error reading setpoint_read_frame buffer")
			print(e)
		
		try:
			#buf=ser.read(7)
			setpoint = ((buf[3]<<8)+buf[4])/10.0
			print("temp: %.2f C  setpoint: %.2f " %(temp,setpoint))
		except Exception as e:
			print("Error decoding buffer")
			print(e)
		
	else:
		print('Setpoint: no data recieved')
		
else:
	print('Temperature: no data recieved')
print("")


# SOLO Motor Controller ------------------------------------------------

print("SOLO Motor Controller Connection")
print("================================")

time.sleep(1)

try:
	# Instanciate a SOLO object:
	# check with SOLO motion terminal that you are able to connect to your device 
	# and make sure the port name in the code is the correct one 
	mySolo = solo.SoloMotorControllerUart(SOLO_port, 0, solo.UartBaudRate.RATE_937500)
	print("Connection created")
	
	# wait here till communication is established
	print("Trying to connect to SOLO")
	communication_is_working = False
	count = 0
	while communication_is_working is False:
		time.sleep(1)
		communication_is_working, error = mySolo.communication_is_working()
		count += 1
		if count>5:
			print("Error instantiating SOLO. Timeout.")
			break
	if communication_is_working:
		print("Communication Established succuessfully!")
	
except Exception as e:
	print("Error instantiating SOLO")
	print(e)

time.sleep(2)

try:
	# Close connection
	print("Closing SOLO connection")
	mySolo.serial_close()
except Exception as e:
	print("Error closing SOLO connection")
	print(e)

time.sleep(5)
