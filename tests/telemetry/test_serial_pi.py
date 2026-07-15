'''
Test script for sending telemetry from Pi
Send a message every second. Print received messages.


To get port number, run
ls -l /dev/serial/by-id/

'''

import serial
import time
import configparser


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


# Set serial port


# Define serial connection
serial_port = serial.Serial(
	port=TELEM_port,
	baudrate=115200, # Data rate (from SpaceTango ICD document)
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1,
)

# Try sent
count = 0
try:
	while True:
		# Send data
		message = f"Hello from Raspberry Pi! #{count}\n"
		serial_port.write(message.encode('utf-8'))
		print(f"Send: {message.strip()}")
		count +=1
		
		# Read incoming data (if any)
		print("Waiting status: ", serial_port.in_waiting)
		if serial_port.in_waiting > 0:
			incoming = serial_port.readline().decode('utf-8').strip()
			print(f"Received: {incoming}")
		
		time.sleep(1)

except KeyboardInterrupt:
	
	# Send reply
	message = "Stopped sending messages. Goodbye!\n"
	serial_port.write(message.encode('utf-8'))
	print(f"Send: {message.strip()}")
	
	time.sleep(1)
	
	serial_port.close()
	print("Telemetry connection closed")	
	
