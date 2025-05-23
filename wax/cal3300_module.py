import serial
import time
from pymodbus.utilities import computeCRC
import pdb
import socket 
import threading
import sys



#controller commands

def add_crc(message):
	crc = computeCRC(message)
	#separate crc into hi and low bytes
	crc_low = crc & 0xFF
	crc_hi = (crc >> 8) & 0xFF
	
	#append crc to message
	message_with_crc = message + bytes([crc_hi, crc_low])
	print(hex(crc_low),hex(crc_hi))

	return message_with_crc


def create_setpoint_message(temp):
	"""
	input temperature in celcius
	"""
	temp = int(temp*10)
	hex_value = hex(int(temp)) #shift to account for decimal and convert to int, e.g. for 30.0c enter 300
	hi_byte = (temp >> 8) & 0xFF
	low_byte = temp & 0xFF
	setpoint_message = add_crc(bytes([0x01,0x06,0x00,0x7F, hi_byte, low_byte]))
	return setpoint_message

# Define functions to get temperature and setpoint temperature
def get_temp_and_setpoint(client_socket):
	global ser, temp_read_frame, setpoint_read_frame
	try:
		# Request temperature data
		ser.write(bytes(temp_read_frame)) #send the message to request data
		#print("sent request for temp")
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())
		else:
			client_socket.sendall('Temperature: no data recieved')

		# Decode temperature response
		temp_value=buf[4]
		#temperature=temp_value/10.0
		temperature = ((buf[3]<<8)+buf[4])/10.0
		#print(temperature)

		# Request setpoint data
		ser.write(bytes(setpoint_read_frame)) # Send the message to request data
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())
		else:
			client_socket.sendall('Setpoint: no data recieved')
		#buf=ser.read(7)
		setpoint = ((buf[3]<<8)+buf[4])/10.0
		#print(setpoint)
		client_socket.sendall(f"Temperature: {temperature} Setpoint: {setpoint}".encode('utf-8'))
		client_socket.sendall(b"showing temp and setpoint.\n")
		
		
	except:
		client_socket.sendall(f"Error in showing temperature: ".encode('utf-8'))
	
	

def set_setpoint(client_socket, data):
	global ser
	index = data.find(" ")
	temp = data[index+1:]
	temp = int(temp)
	print(temp)
	try:
		#construct serial messages
		first_message = add_crc(bytes([0x01,0x06,0x03,0x00,0x00,0x05]))
		second_message = add_crc(bytes([0x01,0x06,0x15,0x00,0x00,0x00]))
		#setpoint_message = add_crc(bytes([0x01,0x06,0x00,0x7F, ])) #setpoint 1B0 = 432 = 43.2 C
		exit_program_mode = add_crc(bytes([0x01,0x06,0x03,0x00,0x00,0x06]))
		exit_program_mode_2nd = add_crc(bytes([0x01,0x06,0x16,0x00,0x00,0x00]))
		setpoint_message = create_setpoint_message(temp)

	
	
		ser.write(first_message)
		print("sent first message (enter program mode)")
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			print('recieved: ',buf.hex())
		else:
			print('Temperature: no data recieved')

		ser.write(second_message)
		print("sent second message (security message)")
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			print('recieved: ',buf.hex())
		else:
			print('Temperature: no data recieved')

		ser.write(setpoint_message)
		print("writing setpoint")
		time.sleep(0.1)

		ser.write(exit_program_mode)
		print("exiting program mode")
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			print('recieved: ',buf.hex())
		else:
			print('Temperature: no data recieved')

		ser.write(exit_program_mode_2nd)
		print("security byte")
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			print('recieved: ',buf.hex())
		else:
			print('Temperature: no data recieved')

		# Request setpoint data
		ser.write(bytes(setpoint_read_frame)) # Send the message to request data
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())
		else:
			print('Setpoint: no data recieved')
		#buf=ser.read(7)
		setpoint = ((buf[3]<<8)+buf[4])/10.0
		client_socket.sendall(f"new setpoint = {setpoint}".encode('utf-8'))
	
	except Exception as e:
		client_socket.sendall(f"Error in setting setpoint: {str(e)}\n".encode('utf-8'))
	
#socket functions

def handle_client_connection(client_socket):
	global setpoint, ser,temp_read_frame,setpoint_read_frame, cal3300_is_running
	while True:
		try:
			data = client_socket.recv(1024).decode('utf-8').strip()
			print(f"Recieved command: {data}")
			
			if not data:
				break
			if data.startswith("set_setpoint"):
				set_setpoint(client_socket,data)
				break
			elif data == "get_temp_and_setpoint":
				get_temp_and_setpoint(client_socket)
				break
			elif data == "exit":
				client_socket.sendall(b"Exiting Server.\n")
				cal3300_is_running = False
				break
			else:
				client_socket.sendall(b"Invalid command.\n")
		except Exception as e:
			client_socket.sendall(f"Error: {str(e)}\n".encode('utf-8'))
			break
	client_socket.close()	

def send_command(command):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 65343))
        client_socket.sendall(command.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(response)
        client_socket.close()
    except Exception as e:
        print(f"Error: {e}")




def cal3300_server_program():
	global temp_read_frame, setpoint_read_frame, t0, temp_crc, ser, cal3300_is_running
	
	
	# Set the serial hexadecimal message to request temperature and setpoint data
	temp_read_frame =     [0x01,0x03,0x00,0x1C,0x00,0x01,0x45,0xCC] #request frame for temperature
	setpoint_read_frame = [0x01,0x03,0x00,0x7F,0x00,0x01,0xB5,0xD2] #request frame for setpoint temperature
	cal3300_is_running = True

	temp_crc = add_crc(bytes([0x01,0x03,0x00,0x1C,0x00,0x01]))
	t0=time.time()
	
	# Set serial port
	ser=serial.Serial(
		port='/dev/ttyUSB0', # Serial port
		baudrate=9600,       # Data rate
		bytesize=serial.EIGHTBITS,      # Data bits
		stopbits =serial.STOPBITS_ONE,  # Stop bits
		parity = serial.PARITY_NONE,    # Parity
		timeout=1, # Timeout (s)
	)

	ser.flush() #clear any junk data 


		
	host = "localhost"
	port = 65343
	
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((host,port))
	server_socket.listen(5)
	
	print("Light Controller Server started. Waiting for connections...")
	
	while cal3300_is_running:
		try:
			server_socket.settimeout(1.0)
			try:
				client_socket, address = server_socket.accept()
				print(f"Connection established with {address}")
				client_handler = threading.Thread(target=handle_client_connection, args = (client_socket,))
				client_handler.start()
			except socket.timeout:
				continue
		except KeyboardInterrupt:
			print("\nServer shutting down (KeyboardInterrupt).")
			cal3300_is_running = False
	print("Server stopped.")
	server_socket.close()
