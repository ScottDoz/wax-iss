# Recover CAL controller and reset temp to 20C
# Use in case of power loss during melting

import serial
import time
from pymodbus.utilities import computeCRC
import configparser
import pdb


t0=time.time() # Start time of program

# Read config parser
config = configparser.ConfigParser()
config.read(r'/home/pi/wax-iss/wax/config.ini')
#print("Config files read:", files)
#print("Config sections: ", config.sections())
#version = config['info']['experiment_id'] # Read experiment ID (which pi is this?)
CAL_port = config['serialports']['CAL_port'] # Read from config file
#SOLO_port = "/dev/ttyACM0"
#print("CAL_port: ", CAL_port)
#print("")

#t = time.time()-t0
#print(f"Config read time: {t} s.")

# Create messages ------------------------------------------------------

def add_crc(message):
	crc = computeCRC(message)
	#separate crc into hi and low bytes
	crc_low = crc & 0xFF
	crc_hi = (crc >> 8) & 0xFF
	
	#append crc to message
	message_with_crc = message + bytes([crc_hi, crc_low])
	#print(hex(crc_low),hex(crc_hi))

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


#construct serial messages
first_message = add_crc(bytes([0x01,0x06,0x03,0x00,0x00,0x05])) # enter program mode
second_message = add_crc(bytes([0x01,0x06,0x15,0x00,0x00,0x00])) # security message
exit_program_mode = add_crc(bytes([0x01,0x06,0x03,0x00,0x00,0x06]))
exit_program_mode_2nd = add_crc(bytes([0x01,0x06,0x16,0x00,0x00,0x00]))

#setpoint_message = add_crc(bytes([0x01,0x06,0x00,0x7F, ])) #setpoint 1B0 = 432 = 43.2 C
setpoint_message = add_crc(bytes([0x01,0x06,0x00,0x7f,0x00,0xc8,0xb9,0x84])) # Setpoint = 20C
#setpoint_message = create_setpoint_message(20)  # Setpoint message

# Set the serial hexadecimal message to request temperature and setpoint data
temp_read_frame =     [0x01,0x03,0x00,0x1C,0x00,0x01,0x45,0xCC] #request frame for temperature
setpoint_read_frame = [0x01,0x03,0x00,0x7F,0x00,0x01,0xB5,0xD2] #request frame for setpoint temperature


# Modbus message Function ----------------------------------------------

def transact_message(message, reply_len=8):
	ser.reset_input_buffer()
	
	ser.write(message)
	ser.flush()
	
	reply = ser.read(reply_len)
	
	if len(reply) != reply_len:
		raise RuntimeError("No reply")

	return reply
	
def modbus_write(message, timeout=0.5):
	ser.reset_input_buffer()
	
	ser.write(message)
	ser.flush()
	
	start = time.perf_counter()
	while time.perf_counter() - start < timeout:
		if ser.in_waiting >=8:
			reply = ser.read(8)
			
			if reply == message:
				return True
			else:
				print("Unexpected reply:", reply.hex())
				return False
		
		time.sleep(0.001) # Sleep 1ms
	
	raise RuntimeError("No reply")
	

# Read temp and setpoint -----------------------------------------------	

# Define functions to get temperature and setpoint temperature
def get_temp_and_setpoint():
	# Request temperature data
	ser.write(bytes(temp_read_frame)) #send the message to request data
	#print("sent request for temp")
	time.sleep(0.1) #wait 0.1 seconds
	if ser.in_waiting>0:
		buf = ser.read(ser.in_waiting) #read all available bytes
		#print('recieved: ',buf.hex())
	else:
		print('Temperature: no data recieved')

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
		print('Setpoint: no data recieved')
	#buf=ser.read(7)
	setpoint = ((buf[3]<<8)+buf[4])/10.0
	#print(setpoint)
	
	return temperature, setpoint


# Main program ------------------------------------------------------


# Create serial port connection
ser=serial.Serial(
	port=CAL_port, # Serial port
	baudrate=9600,       # Data rate 9600
	bytesize=serial.EIGHTBITS,      # Data bits
	stopbits =serial.STOPBITS_ONE,  # Stop bits
	parity = serial.PARITY_NONE,    # Parity
	timeout=0.03, # Timeout (s) short timeout
)
ser.flush() #clear any junk data 


while True:
	
	# First message: enter program mode.
	# Detect when first reply from CAL serial connection
	try:
		modbus_write(first_message)
		t1 = time.time()-t0 #~0.05 s
		#print(f"CAL detection time: {t1} s.")
		break
		# TODO: check to see if this loop prevents the heater PID from working
		# Comment out the break to keep the loop running. Check current draw.
	except RuntimeError:
		pass

# Now write next messages
time.sleep(0.05)
modbus_write(second_message)    # security message
modbus_write(setpoint_message)  # setpoint message
modbus_write(exit_program_mode) # Exit program mode message
modbus_write(exit_program_mode_2nd) # Security byte

t2 = time.time()-t0 #~0.05 s


# Confirm reset
time.sleep(0.1)
temp,setpoint = get_temp_and_setpoint()


# Printouts
print(f"CAL serial detection time: {t1} s.")
print(f"Reset setpoint within {t2-t1} s of connection.")
print("temp: %.2f C  setpoint: %.2f " %(temp,setpoint))

#time.sleep(10)


# ~ # Loop: Try to reset setpoint
# ~ temp_reset = False
# ~ while True:
	# ~ try:
		# ~ set_setpoint_20()
		# ~ temp_reset = True # Update flag
		# ~ t = time.time()-t0
		# ~ print(f"Change setpoint sent after {t} s.")
		# ~ break
	# ~ except:
		# ~ time.sleep(0.05)
		# ~ print()
	

# ~ # Read temp and setpoint
# ~ time.sleep(0.1)
# ~ temp,setpoint = get_temp_and_setpoint()
# ~ print("time: %.3f   temp: %.2f C  setpoint: %.2f " %(t,temp,setpoint))

# ~ time.sleep(1)
