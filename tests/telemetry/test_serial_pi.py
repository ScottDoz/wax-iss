'''
Test script for sending telemetry from Pi
Send a message every second. Print received messages.

'''

import serial
import time

# Define serial connection
serial_port = serial.Serial(
	port='/dev/ttyUSB1',
	baudrate=9600,
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
	
