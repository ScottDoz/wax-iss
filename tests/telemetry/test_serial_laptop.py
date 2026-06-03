'''
Test script for Laptop
Listen for messages from Pi.
Reply to confirm receipt of message.

'''
import serial
import time

# Define serial connection
laptop_port = serial.Serial(
	port='COM4',
	baudrate=9600,
	timeout=1,
)

# Try sen
try:
	while True:
		
		
		# Read incoming data (if any)
		if laptop_port.in_waiting > 0:
			incoming = laptop_port.readline().decode('utf-8').strip()
			print(f"Received from Pi: {incoming}")
		
		# Send reply
		message = "Laptop received your message!\n"
		laptop_port.write(message.encode('utf-8'))
		print(f"Send: {message.strip()}")
		
		time.sleep(0.1)

except KeyboardInterrupt:
	laptop_port.close()
	print("Telemetry connection closed")	
	
