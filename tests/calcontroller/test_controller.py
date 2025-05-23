import serial
import time
from pymodbus.utilities import computeCRC
import pdb





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



# Set the serial hexadecimal message to request temperature and setpoint data
temp_read_frame =     [0x01,0x03,0x00,0x1C,0x00,0x01,0x45,0xCC] #request frame for temperature
setpoint_read_frame = [0x01,0x03,0x00,0x7F,0x00,0x01,0xB5,0xD2] #request frame for setpoint temperature



temp_crc = add_crc(bytes([0x01,0x03,0x00,0x1C,0x00,0x01]))





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
	

def set_setpoint(temp):
	
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
	print("new setpoint = ",setpoint)
	
	return  
	


t0=time.time()

set_setpoint(30)
time.sleep(2)
while True:
	t = time.time()-t0
	temp,setpoint = get_temp_and_setpoint()
	print("time: %.3f   temp: %.2f C  setpoint: %.2f " %(t,temp,setpoint))
	time.sleep(1)
