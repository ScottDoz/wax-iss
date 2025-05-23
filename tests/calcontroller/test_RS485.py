import serial
import time

#set the serial hexadecimal message to request temperature and humidity data
temp_ref_frame = [0x01, 0x04, 0x00, 0x01, 0x00, 0x01, 0x60, 0x0a] #request frame fro temp sensor
humid_ref_frame = [0x01, 0x04, 0x00, 0x02, 0x00, 0x01, 0x90, 0x0a] #request frame for humidity sensor

#set serial port
ser=serial.Serial(port='/dev/ttyUSB0',baudrate=9600) 

#define functions to get temperature and humidity
def get_temp_and_humidity():
	ser.write(bytes(temp_ref_frame)) #send the message to request data
	time.sleep(0.05) #wait 0.1 seconds
	buf=ser.read(7) #read reply message to a buffer of length 7 bits
	#decode temperature
	temp_value=(buf[3]<<8)|buf[4] 
	temperature=temp_value/10.0

	#read humidity
	ser.write(bytes(humid_ref_frame))
	time.sleep(0.05) #wait 0.1 seconds
	buf=ser.read(7)
	humid_value = (buf[3]<<8)|buf[4]
	humidity=humid_value/10.0

	return temperature, humidity
t0=time.time()
while True:
	t = time.time()-t0
	temp,humid = get_temp_and_humidity()
	print("time: %.3f   temp: %.1f C  humidity: %.2f " %(t,temp,humid))
	time.sleep(0.1)
