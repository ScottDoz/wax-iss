'''
Test script for Laptop
Listen for telemetry messages from Pi.

'''
import serial
import time

# Define serial connection
laptop_port = serial.Serial(
	port='COM4',
	baudrate=115200, # Data rate (from SpaceTango ICD document)
	timeout=1,
)

# Try sen
try:
	while True:
		
		# Read incoming data (if any)
		#print("Waiting status: ", laptop_port.in_waiting)
		if laptop_port.in_waiting > 0:
			data = laptop_port.read(laptop_port.in_waiting)
			print(f"Received from Pi. Paket size = {len(repr(data))}")
			print(repr(data))
			print('')
		
		# Send reply
		#message = "Laptop received your message!\n"
		#laptop_port.write(message.encode('utf-8'))
		#print(f"Send: {message.strip()}")
		
		time.sleep(0.1)

except KeyboardInterrupt:
	
	# Send reply
	#message = "Stopped listening. Goodbye!\n"
	#laptop_port.write(message.encode('utf-8'))
	#print(f"Send: {message.strip()}")
	
	time.sleep(1)
	
	laptop_port.close()
	print("Telemetry connection closed")	
	
