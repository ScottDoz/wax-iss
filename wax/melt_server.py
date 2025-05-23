'''
Melt server
-----------

Comands to run melting experiment

How to run

Terminal 1: Start server
>> sudo python melt_server.py

# Terminal 2: Run commands
>> sudo python melt_client.py start melt session_03,800,42 # Start a melt experiment label="session_03",rpm=800,temp=42 C
>> sudo python melt_client.py exit # Stop the server


'''
# Imports

#from light_module import light_turn_on, light_set_color, light_turn_off, light_set_brightness
import socket 
import threading
import sys
import board
import neopixel
import time
import busio
import digitalio
import getopt
from datetime import datetime
import os
from libcamera import Transform
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
import pdb
import glob
import numpy as np
import pandas as pd

import pigpio
import rotary_encoder

# Cal3300 imports
from pymodbus.utilities import computeCRC
import serial
#thermocoupel imports
import adafruit_max31856 # Wrong package us 31865
import adafruit_max31865 

# ######################################################################
# Light commands
# ######################################################################

def light_turn_on(client_socket,data):
	''' Turn lights on '''
	global light_is_on
	if light_is_on:
		client_socket.sendall(b"Lights already on.\n")
		return
	try:
		light_is_on = True
		pixels.fill(color)
		pixels.show()
		client_socket.sendall(b"Turning on lights.\n")
	except Exception as e:
		client_socket.sendall(f"Error in turning on: {str(e)}\n".encode('utf-8'))
		
		
def light_set_color_socket(client_socket,data): #light set color
	''' Set light color (socket version) '''
	global light_is_on
	arg_color = data[11:]
	color = [int(x) for x in arg_color.split(',')]
	if len(color) != 3:
		raise ValueError
	try:
		pixels.fill(color)
		pixels.show()
		light_is_on = True
		client_socket.sendall(b"Setting color.\n")
	except:
		client_socket.sendall(f"Error in setting color: {str(e)}\n".encode('utf-8'))
		
		
def light_set_color(color):
	''' Set light color '''
	global light_is_on
	if len(color) != 3:
		raise ValueError
	try:
		pixels.fill(color)
		light_is_on = True
		pixels.show()
	except:
		pass

def light_turn_off_client(client_socket): 
	''' Turn lights off '''
	global light_is_on
	if not light_is_on:
		client_socket.sendall(b"Lights already off.\n")
		return
	try:
		pixels.fill((0,0,0))
		pixels.show()
		light_is_on=False
		client_socket.sendall(b"Turning lights off\n")
	except Exception as e:
		client_socket.sendall(f"Error in turning off: {str(e)}\n".encode('utf-8'))

def light_turn_off(): 
	''' Turn lights off '''
	global light_is_on
	if not light_is_on:
		#client_socket.sendall(b"Lights already off.\n")
		return
	try:
		pixels.fill((0,0,0))
		pixels.show()
		light_is_on=False
		#client_socket.sendall(b"Turning lights off\n")
	except Exception as e:
		pass
		#client_socket.sendall(f"Error in turning off: {str(e)}\n".encode('utf-8'))
		
def light_set_brightness(client_socket, data):
	''' Set light brightness '''
	brightness = data[17:]
	try:
		pixels.brightness = float(brightness)
		pixels.show()
		client_socket.sendall(b"Setting brightness.\n")
	except Exception as e:
		client_socket.sendall(f"Error in setting brightness: {str(e)}\n".encode('utf-8'))

# ######################################################################		
# Camera commands
# ######################################################################

def start_recording(client_socket, preview=False):
	''' Start camera recording '''
	global camera_is_recording, rotation, video_output_file, exper_folder, picam2, camera_is_running
	global camera_preview
	
	#restart camera
	picam2 = Picamera2()
	camera_is_running = True
	camera_preview = preview
	
	if camera_is_recording:
		client_socket.sendall(b"Recording is already in progress.\n")
		return

	try:
		base_folder = "video.h264"
		#  if len(data.split()) > 1:
		#       file_name = data.split(" ", 1)[1]
		#      if not file_name.startswith(base_folder):
		video_output_file = os.path.join(exper_folder, os.path.basename(base_folder))
		#      else:
		#        video_output_file = file_name
		#else:
		#    video_output_file = os.path.join(base_folder, "output_video.h264")
		#rotation
		if rotation:
			video_config = picam2.create_video_configuration(main={'size':(1920,1080)},transform=Transform(hflip=True, vflip=True))
		else:
			video_config = picam2.create_video_configuration(main={'size':(1920,1080)},transform=Transform(hflip=True,vflip=True))
	
		try:
			picam2.configure(video_config)
		except:
			pdb.set_trace()
			
		
		# Start camera preview
		if preview:
			try:
				picam2.start_preview(Preview.QTGL)
			except Exception as e:
				print(f"Error in camera preview: {e}")
		
		
		picam2.start()
		picam2.start_recording(encoder, video_output_file)
		camera_is_recording = True
		print("Recording started.")
		client_socket.sendall(f"Recording started. Saving to {video_output_file}\n".encode('utf-8'))
	except Exception as e:
		client_socket.sendall(f"Error starting recording: {str(e)}\n".encode('utf-8'))
        
def rotate_camera(client_socket, data):
	''' Rotate camera view by 180 deg '''
	global rotation, picam2
	try:
		rotation = True
		client_socket.sendall(f"Camera rotation set to 180 degrees.\n".encode('utf-8'))
	except Exception as e:
		client_socket.sendall(f"Error rotating camera: {str(e)}\n".encode('utf-8'))


def stop_recording():
	''' Stop camera recording '''
	global camera_is_recording, picam2
	global camera_preview

	if not camera_is_recording:
		#client_socket.sendall(b"No recording in progress to stop.\n")
		return

	try:
		picam2.stop_recording()
		try:
			picam2.stop_preview()
		except:
			pass
		#picam2.close()
		camera_is_recording = False
		print("Recording stopped.")
		#client_socket.sendall(b"Recording stopped.\n")
	except Exception as e:
		pass
		#client_socket.sendall(f"Error stopping recording: {str(e)}\n".encode('utf-8'))
		
def stop_recording_client(client_socket):
	''' Stop camera recording '''
	global camera_is_recording

	if not camera_is_recording:
		client_socket.sendall(b"No recording in progress to stop.\n")
		return

	try:
		picam2.stop_recording()
		try:
			picam2.stop_preview()
		except:
			pass
		#picam2.close()
		camera_is_recording = False
		print("Recording stopped.")
		client_socket.sendall(b"Recording stopped.\n")
	except Exception as e:
		client_socket.sendall(f"Error stopping recording: {str(e)}\n".encode('utf-8'))

def stop_camera():
	global picam2, camera_is_running
	if camera_is_running:
		picam2.close()
	camera_is_running = False
	
	   
# ######################################################################
# Thermocouple commands
# ######################################################################

def change_file_pathway(client_sockey, data):
        global thermocouple_file_path
        try:
                index = data.find(" ")
                new_path = data[index+1:]
                file_path = new_path
                #client_socket.sendall(b"setting file path to")
        except Exception as e:
                client_socket.sendall(f"Error updating filename\n".encode('utf-8'))

def show_data(client_socket):
	global stime,spy, timestep, thermocouple, thermocouple2

	if spy == True:
		client_socket.sendall(b"Already showing data.\n")
		return
	
	try:
		spy = True
		client_socket.sendall(b"Showing Data:")
		print(spy)
		while spy:
			#print("here")
			temp = thermocouple.temperature
			temp2 = thermocouple2.temperature
			t = (time.perf_counter()-stime)
			print("Time {:.2f} s Temp1: {:.2f}, Temp2: {:.2f}".format(t,temp,temp2))
			time.sleep(timestep)
	except Exception as e:
		client_socket.sendall(f"Error in starting spy: {str(e)}\n".encode('utf-8'))


def hide_data(client_socket):
	global spy
	
	if spy == False:
		client_socket.sendall(b"Already hiding data.\n")
		return
	try:
		spy = False
		client_socket.sendall(b"Hiding Data\n")
	except Exception as e:
		client_socket.sendall(f"Error in stopping spy: {str(e)}\n".encode('utf-8'))

def set_timestep(client_socket, data):
	global timestep
	try:
		index = data.find(" ")
		new_timestep = data[index+1:]
		timestep = float(new_timestep)
		client_socket.sendall(b"Updateing timestep")
	except Exception as e:
		client_socket.sendall(f"Error in updating timestep: {str(e)}\n".encode('utf-8'))

def start_log(client_socket):
	global thermocouple_recording, thermocouple_file_path,stime, timestep, thermocouple, thermocouple2, exper_file

	try:
		thermocouple_file_path = os.path.join(exper_folder, os.path.basename("templog.txt"))
		file = open(thermocouple_file_path, "w")
		thermocouple_recording = True
		client_socket.sendall(b"Starting log:")
		while thermocouple_recording:
			temp = thermocouple.temperature
			temp2 = thermocouple2.temperature
			t = (time.perf_counter()-stime)
			file.write("Time {:.2f} s Temp1: {:.2f} Temp2: {:.2f}\n".format(t,temp,temp2))
			file.flush()
			time.sleep(timestep)
		print("closed file")
	except Exception as e:
                client_socket.sendall(f"Error in starting log: {str(e)}\n".encode('utf-8'))
	finally:
		file.close()

def start_log_melt():
        global thermocouple_recording, thermocouple_file_path,stime, timestep, thermocouple, thermocouple2, exper_file

        try:
                thermocouple_file_path = os.path.join(exper_folder, os.path.basename("templog.txt"))
                file = open(thermocouple_file_path, "w")
                thermocouple_recording = True
                while thermocouple_recording:
                        temp = thermocouple.temperature
                        temp2s = thermocouple2.temperature
                        t = (time.perf_counter()-stime)
                        file.write("Time {:.2f} s temperature: {:.2f}\n".format(t,temp))
                        file.flush()
                        time.sleep(timestep)
                print("closed file")
        except Exception as e:
                pass
        finally:
                file.close()

def stop_log(client_socket):
	global thermocouple_recording,picam2
	
	if thermocouple_recording == False:
		client_socket.sendall(b"Alread stopped log\n")
		return
	try:
		thermocpuple_recording = False
		client_socket.sendall(b"Stopping log")
	except Exception as e:
		client_socket.sendall(f"Error in stopping log: {str(e)}\n".encode('utf-8'))
		
# ######################################################################		
# CAL controller commands
# ######################################################################

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

# Define functions to get temperature and setpoint temperature

def get_temp_and_setpoint_socket(client_socket):
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
		
	return temperature, setpoint
	
#get cal controller temperature and setpoint without socket
def get_temp_and_setpoint(sleep_time=.1):
	global ser, temp_read_frame, setpoint_read_frame
	try:
		# Request temperature data
		ser.write(bytes(temp_read_frame)) #send the message to request data
		#print("sent request for temp")
		time.sleep(sleep_time) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf1 = ser.read(ser.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())

		# Decode temperature response
		temp_value=buf1[4]
		#temperature=temp_value/10.0
		temperature = ((buf1[3]<<8)+buf1[4])/10.0
		#print(temperature)

		# Request setpoint data
		ser.write(bytes(setpoint_read_frame)) # Send the message to request data
		time.sleep(sleep_time) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf2 = ser.read(ser.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())
		#buf=ser.read(7)
		setpoint = ((buf2[3]<<8)+buf2[4])/10.0
		#print(setpoint)	
		
	except:
		return np.nan, np.nan
		
	return temperature, setpoint
	
	

def set_setpoint_socket(client_socket, data):
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
		
		
		
def set_setpoint(temp):
	global ser
	try:
		#construct serial messages
		first_message = add_crc(bytes([0x01,0x06,0x03,0x00,0x00,0x05]))
		second_message = add_crc(bytes([0x01,0x06,0x15,0x00,0x00,0x00]))
		#setpoint_message = add_crc(bytes([0x01,0x06,0x00,0x7F, ])) #setpoint 1B0 = 432 = 43.2 C
		exit_program_mode = add_crc(bytes([0x01,0x06,0x03,0x00,0x00,0x06]))
		exit_program_mode_2nd = add_crc(bytes([0x01,0x06,0x16,0x00,0x00,0x00]))
		setpoint_message = create_setpoint_message(temp)

	
	
		ser.write(first_message)
		#print("sent first message (enter program mode)")
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())
		#else:
			#print('Temperature: no data recieved')

		ser.write(second_message)
		#print("sent second message (security message)")
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())
		#else:
		#	print('Temperature: no data recieved')

		ser.write(setpoint_message)
		#print("writing setpoint")
		time.sleep(0.1)

		ser.write(exit_program_mode)
		#print("exiting program mode")
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())
		#else:
			#print('Temperature: no data recieved')

		ser.write(exit_program_mode_2nd)
		#print("security byte")
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())
		#else:
		#	print('Temperature: no data recieved')

		# Request setpoint data
		ser.write(bytes(setpoint_read_frame)) # Send the message to request data
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())
		#else:
		#	print('Setpoint: no data recieved')
		#buf=ser.read(7)
		setpoint = ((buf[3]<<8)+buf[4])/10.0
		#client_socket.sendall(f"new setpoint = {setpoint}".encode('utf-8'))
	
	except Exception as e:
		pass
		#client_socket.sendall(f"Error in setting setpoint: {str(e)}\n".encode('utf-8'))
		
		
		
def set_setpoint_melt(client_socket, setpoint):
	global ser
	temp = int(setpoint)
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



# ######################################################################		
# Motor commands
# ######################################################################
def callback(way):
    global curr_pos
    curr_pos += way

def calc_new(prev, rpm):
    global ed, ei, rpm_setpoint, kp,kd,ki, pwm_range
    e = rpm_setpoint - rpm
    outp = prev + e*kp
    outpd = prev + e*kp + ed*kd
    outpid = prev + e*kp + ed*kd + ei*ki
    #print(int(outp), int(outpd), int(outpid))
    ed = e
    ei += e
    return max(min(pwm_range, outpid), 0)  
    
def change_rpm_setpoint(rpm_new):
	global rpm_setpoint
	rpm_setpoint = rpm_new
	print("rpm setpoint changed to: ", rpm_setpoint)
	return

def pause_rotation():
	change_rpm_setpoint(0)
	print("pausing rotation")
	return
	
def resume_rotation():
	global experiment_rpm_setpoint
	change_rpm_setpoint(experiment_rpm_setpoint)
	print("resuming rotation at ", experiment_rpm_setpoint)
	return
	
def stop_motors():
	global pi
	
	Motor1A = 23 # header 18, wpi 5
	Motor1B = 24 # header 16, wpi 4
	Motor1E = 12 # header 33, wpi 23
	
	pi.write(Motor1A, 0)
	pi.write(Motor1B, 1)
	print("Stoping motors")
	
	return


# ######################################################################		
# Overall commands
# ######################################################################


#create file folder
def create_folder(client_socket, prefix, label,rpm_set,temp_setpoint):

		#creating session folder
	try: 
		session_file_path = "/home/pi/Data/" + label
		if not os.path.exists(session_file_path):
			os.makedirs(session_file_path)
			print("created folder:", session_file_path)
	except Exception as e:
		client_socket.sendall(f"Error in making directory: {str(e)}\n".encode('utf-8'))
		
		
	#count number of existing melt folders

	items = glob.glob(os.path.join(session_file_path, prefix+"*"))
	print(items)
	if len(items) == 0:
		count = 0
	else:
		try:
			count = len(items)	
			#for root, dirs, files in os.walk(session_file_path):
				#count += dirs.count("Melt*")
			#directories = [item for item in items is os.path.isdir(item)] # list of directories
			#count = len(directories)
		except:
			pdb.set_trace()	
		
	#create experiment folder
	exper_folder = session_file_path + "/"+prefix+"_" + str((rpm_set)) + "_" + str(count)
	if not os.path.exists(exper_folder):
		os.makedirs(exper_folder)
		print("created folder:", exper_folder)
	return exper_folder

# Melting experiment commands
def start_melt(client_socket, label, rpm_set, temp_setpoint):
	global melt_running
	global exper_folder, thermocouple_recording 
	global curr_pos, rpm_setpoint, pwm_range, experiment_rpm_setpoint
	global kp,kd,ki, ed, ei
	global print_rotation
	
	#global pi
	
	melt_running = True
	print_rotation = True
	
	#create the experiment folder
	exper_folder = create_folder(client_socket, "Melt", label, rpm_set, temp_setpoint) 
	
	
	#start camera recording
	try:
		start_recording(client_socket)
	except:
		print("Error starting camera")
	
	#turn on lights
	light_set_color([250,250,250])
	
	#set the cal controller setpoint
	set_setpoint(temp_setpoint)
	
	#motor setup (LAB SETTINGS)
	#Pins for Motor Driver Inputs
	#Motor1A = 23 # header 18, wpi 5
	#Motor1B = 24 # header 16, wpi 4
	#Motor1E = 12 # header 33, wpi 23
	#encA, encB = 26, 16 # these are BCM pins, headers 13 and 15, wPi 2 and 3 (LAB settings)
	
	#motor setup (FLIGHT SETTINGS)
	#Pins for Motor Driver Inputs
	Motor1A = 23 # header 18, wpi 5
	Motor1B = 24 # header 16, wpi 4
	Motor1E = 12 # header 33, wpi 23
	#encA, encB = 23, 24 # these are BCM pins, headers 13 and 15, wPi 2 and 3 (LAB settings)
	encA, encB = 26, 25 # these are BCM pins, headers 13 and 15, wPi 2 and 3 (FLIGHT settings)
	
	
	# Ramp time
	ramp_time = 10 # Ramp up time
	
	
	last_pos, curr_pos = 0, 0
	start = 0
	LOOP_TIME = .15
	G = 6.3
	CPR = 16
	pwm_range = 500
	prev = 0
	rpm = 0
	ed, ei = 0, 0
	rpm_setpoint = rpm_set
	experiment_rpm_setpoint = rpm_set

	kp, ki, kd = 0.4, 0.1, 0 #pid settings

	# Create handle for motor and decoder
	pi = pigpio.pi()
	pi.set_PWM_frequency(Motor1E, 19200)
	pi.set_PWM_range(Motor1E, pwm_range)
	decoder = rotary_encoder.decoder(pi, encA, encB, callback) 
	
	# Set up the data log
	data_file_path = os.path.join(exper_folder, os.path.basename("melt_data.csv"))
	file = open(data_file_path, "w")
	file.write("Time, Temp, Temp_CAL, Temp_setpoint, RPM, RPM_setpoint\n") #write the header
	client_socket.sendall(b"Starting log:") # Print to terminal
	thermocouple_recording = True
	timestep = 1
	
	
	# Main time loop
	try:
		# Initialize loop
		stime =time.perf_counter() # Start time
		t_prev =  (time.perf_counter()-stime)
		dt, dpos = time.perf_counter() - stime, curr_pos - last_pos # initialize motor positions
		while melt_running:
			# Get current time
			t = (time.perf_counter()-stime)
			dt = t - t_prev # get the change in time 
			t_prev = t #update previous time
			
			# Read thermocouple temperature
			temp = thermocouple.temperature
			# Read CAL controller temperature and setpoint
			temp_cal, setpoint = get_temp_and_setpoint(sleep_time = 0.05)
			
			# Compute rpm
			dpos = curr_pos - last_pos 
			if dt > LOOP_TIME:
				last_pos = curr_pos
				rpm = (dpos*60)/(G*CPR*dt)
				time.sleep(.001)
				new = calc_new(prev, rpm)
				pi.set_PWM_dutycycle(Motor1E, new)
				prev = new
				
				if print_rotation:
					print(f"Motor RPM: {rpm}")
			
			pi.write(Motor1A, 0)
			pi.write(Motor1B, 1)
			

			# Write data to log file
			file.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.4f}\n".format(t,temp,temp_cal, setpoint,rpm, rpm_setpoint))
			file.flush()
			
			# Sleep
			t_1 = (time.perf_counter()-stime) #get current time again
			#time.sleep(1-t_1 % 1) # sleep until time top of next second 
			#time.sleep(1) # Sleep 1 sec
			
		# End time loop
		pi.set_PWM_dutycycle(Motor1E, 0)
		pi.write(Motor1A, 0)
		pi.write(Motor1B, 0)
		print("Motors stopped")
		
		
	except Exception as e:
                client_socket.sendall(f"Error in starting log: {str(e)}\n".encode('utf-8'))
	finally:
		file.close()
		print("closed file")
		pi.write(Motor1A, 0)
		pi.write(Motor1B, 0)
		pi.stop()
		print("Set motors to 00")
		
		
def stop_melt_client(client_socket):
	global melt_running, thermocouple_is_running,camera_is_running, light_is_running, cal3300_is_running, camera_is_recording
	try:
		
		#stop_camera()
		#stop_motors()
		light_turn_off_client(client_socket)
		print("DEBUG: stop_melt_client: lights off")
		melt_running = False	
		#camera_is_running = False
		stop_recording()
		print("DEBUG: stop_melt_client: stop_recording")
		try:
			stop_camera()
		except:
			print("Error stopping camera")
		light_is_running = False
		thermocouple_is_running = False
		cal3300_is_running = False	
		#print("DEBUG: stop_melt_client: end of stop_melt_client")
		#print("DEBUG: melt_running, light_is_running, thermocouple_is_running, cal3300_is_running")
		#print(melt_running)
	except Exception as e:
		client_socket.sendall(f"Error in stopping melt: {str(e)}\n".encode('utf-8'))
		
def stop_melt():
	global melt_running, thermocouple_is_running,camera_is_running, light_is_running, cal3300_is_running
	try:
		try:
			stop_camera()
		except:
			print("Failed to stop camera")
		light_turn_off() 
		melt_running = False	
		stop_recording()
		stop_camera()
		light_is_running = False
		thermocouple_is_running = False
		cal3300_is_running = False	
	except Exception as e:
		pass
		#client_socket.sendall(f"Error in stopping melt: {str(e)}\n".encode('utf-8'))


#casting experiment

def start_cast(client_socket, label, rpm_set, temp_setpoint):
	global melt_running
	global exper_folder, thermocouple_recording, curr_pos, rpm_setpoint, pwm_range, melt_running, experiment_rpm_setpoint
	global kp,kd,ki, ed, ei
	
	melt_running = True
	print_rotation = True
	
	#create the experiment folder
	exper_folder = create_folder(client_socket, "Cast", label, rpm_set, temp_setpoint) 
	
	
	#start camera recording
	try:
		start_recording(client_socket)
	except:
		print("Error starting camera")
	
	#turn on lights
	light_set_color([250,250,250])
	
	#set the cal controller setpoint
	set_setpoint(temp_setpoint)
	
	#motor setup
	#Pins for Motor Driver Inputs
	Motor1A = 23 # header 18, wpi 5
	Motor1B = 24 # header 16, wpi 4
	Motor1E = 12 # header 33, wpi 23
	encA, encB = 26, 25 # these are BCM pins, headers 13 and 15, wPi 2 and 3

	last_pos, curr_pos = 0, 0
	start = 0
	LOOP_TIME = .15
	G = 6.3
	CPR = 16
	pwm_range = 500
	prev = 0
	rpm = 0
	ed, ei = 0, 0
	rpm_setpoint = rpm_set
	experiment_rpm_setpoint = rpm_set

	kp, ki, kd = 0.4, 0.1, 0 #pid settings

	# Create handle for motor and decoder
	pi = pigpio.pi()
	pi.set_PWM_frequency(Motor1E, 19200)
	pi.set_PWM_range(Motor1E, pwm_range)
	decoder = rotary_encoder.decoder(pi, encA, encB, callback) 
	
	# Set up the data log
	data_file_path = os.path.join(exper_folder, os.path.basename("cast_data.csv"))
	file = open(data_file_path, "w")
	file.write("Time, Temp, Temp_CAL, Temp_setpoint, RPM, RPM_setpoint\n") #write the header
	client_socket.sendall(b"Starting log:") # Print to terminal
	thermocouple_recording = True
	timestep = 1
	
	
	# Main time loop
	try:
		# Initialize loop
		stime =time.perf_counter() # Start time
		t_prev =  (time.perf_counter()-stime)
		dt, dpos = time.perf_counter() - stime, curr_pos - last_pos # initialize motor positions
		while melt_running:
			# Get current time
			t = (time.perf_counter()-stime)
			dt = t - t_prev # get the change in time 
			t_prev = t #update previous time
			
			# Read thermocouple temperature
			temp = thermocouple.temperature
			# Read CAL controller temperature and setpoint
			temp_cal, setpoint = get_temp_and_setpoint(sleep_time = 0.05)
			
			# Compute rpm
			dpos = curr_pos - last_pos 
			if dt > LOOP_TIME:
				last_pos = curr_pos
				rpm = (dpos*60)/(G*CPR*dt)
				time.sleep(.001)
				new = calc_new(prev, rpm)
				pi.set_PWM_dutycycle(Motor1E, new)
				prev = new
				
				if print_rotation:
					print(f"Motor RPM: {rpm}")
			
			pi.write(Motor1A, 0)
			pi.write(Motor1B, 1)
			

			# Write data to log file
			file.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.4f}\n".format(t,temp,temp_cal, setpoint,rpm, rpm_setpoint))
			file.flush()
			
			# Sleep
			t_1 = (time.perf_counter()-stime) #get current time again
			#time.sleep(1-t_1 % 1) # sleep until time top of next second 
			#time.sleep(1) # Sleep 1 sec
			
		# End time loop
		pi.set_PWM_dutycycle(Motor1E, 0)
		pi.write(Motor1A, 0)
		pi.write(Motor1B, 0)
		print("Motors stopped")
		
		
	except Exception as e:
                client_socket.sendall(f"Error in starting log: {str(e)}\n".encode('utf-8'))
	finally:
		file.close()
		print("closed file")
		pi.set_PWM_dutycycle(Motor1E, 0)
		pi.write(Motor1A, 0)
		pi.write(Motor1B, 0)
		pi.stop()
		print("Motors stopped")

def stop_cast(client_socket):
	#wrapper to stop melt
	stop_melt_client(client_socket)
	return
	
	
##fluid rotation commands"

def start_fluid_rotation(client_socket, label, rpm_profile, temp_setpoint):
	global exper_folder, thermocouple_recording, curr_pos, rpm_setpoint, pwm_range, melt_running, experiment_rpm_setpoint
	global kp,kd,ki, ed, ei
	global melt_running
	
	melt_running = True

	#create the experiment folder
	exper_folder = create_folder(client_socket, "Fluid_Rotation", label, rpm_profile.split('/')[-1].split(".")[0], temp_setpoint) 
	

	#start camera recording
	try:
		start_recording(client_socket)
	except:
		print("Error starting camera")
	
	#turn on lights
	light_set_color([250,250,250])
	
	#set the cal controller setpoint
	set_setpoint(temp_setpoint)
	
	#read rpm profile	
	df = pd.read_csv(rpm_profile)
	x=df.Time.to_numpy() #time
	y=df.RPM.to_numpy() #rpm
	t_profile_end = x[-1]  #get the end time of rpm profile
	
	#telemetry update time, maximum frequency one packet every 5 seconds
	telem_update_time = 5
	
	
	
	#motor setup
	#Pins for Motor Driver Inputs
	Motor1A = 23 # header 18, wpi 5
	Motor1B = 24 # header 16, wpi 4
	Motor1E = 12 # header 33, wpi 23
	encA, encB = 26, 25 # these are BCM pins, headers 13 and 15, wPi 2 and 3

	last_pos, curr_pos = 0, 0
	start = 0
	LOOP_TIME = .1 #update tiem for the rpm pid controller
	G = 6.3
	CPR = 16
	pwm_range = 500
	prev = 0
	rpm = 0
	ed, ei = 0, 0
	rpm_setpoint = y[0]
	experiment_rpm_setpoint = y[0] #use the starting rpm in profile
 
	kp, ki, kd = 0.4, 0.1, 0 #pid settings

	# Create handle for motor and decoder
	pi = pigpio.pi()
	pi.set_PWM_frequency(Motor1E, 19200)
	pi.set_PWM_range(Motor1E, pwm_range)
	decoder = rotary_encoder.decoder(pi, encA, encB, callback) 
	
	# Set up the data log
	data_file_path = os.path.join(exper_folder, os.path.basename("fluid_data.csv"))
	file = open(data_file_path, "w")
	file.write("Time, Time_Thermo, Temp_Thermo, Time_CAL, Temp_CAL, Temp_setpoint, Time_RPM, RPM, RPM_setpoint\n") #write the header
	#client_socket.sendall(b"Starting log:") # Print to terminal
	thermocouple_recording = True
	timestep = 1
	
	
	# Main time loop
	try:
		# Initialize loop
		stime =time.perf_counter() # Start time
		t_prev =  (time.perf_counter()-stime)
		dt, dpos = time.perf_counter() - stime, curr_pos - last_pos # initialize motor positions
		t_rpm = 0
		t_thermo = 0
		t_cal = 0
		t_since_last_telem = 0
		while melt_running:
			# Get current time
			t = (time.perf_counter()-stime)
			if t > t_profile_end:
				stop_melt()
			
			
			dt = t - t_prev # get the change in time 
			t_prev = t #update previous time
			
			#interpolate rpm setpoint from profile
			rpm_t = np.interp(t,x,y) #interpolate rpm profile to get rpm as current timestep
			change_rpm_setpoint(rpm_t)
			
			
			# Compute rpm
			dpos = curr_pos - last_pos 
			if dt > LOOP_TIME:
				last_pos = curr_pos
				rpm = (dpos*60)/(G*CPR*dt)
				t_rpm = (time.perf_counter()-stime) #get current time again
				time.sleep(.001)
				new = calc_new(prev, rpm)
				pi.set_PWM_dutycycle(Motor1E, new)
				prev = new
			
			pi.write(Motor1A, 0)
			pi.write(Motor1B, 1)
			
			# Read thermocouple temperature
			temp = thermocouple.temperature
			t_thermo = (time.perf_counter()-stime) #get current time again
			# Read CAL controller temperature and setpoint
			temp_cal, setpoint = get_temp_and_setpoint(sleep_time = 0.05)
			t_cal = (time.perf_counter()-stime) #get current time again
			# Write data to log file
			file.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.4f},{:.4f}, {:.4f}\n".format(t,t_thermo,temp,t_cal,temp_cal, setpoint,t_rpm,rpm, rpm_setpoint))
			file.flush()
			
			
			
			
			#Set serial port for telemetry downlink
			#telem = serial.Serial(port ='/dev/ttyUSB1', baudrate=115200) #open serial port
			#print(telem.name()) #check which port was really used
			#telem.write(b'\"Temperature1\":98.3,\"experiment_time\":10.45') #write a string
			#telem.close() #close port
			
			
			# Sleep
			t_1 = (time.perf_counter()-stime) #get current time again
			t_since_last_telem += t_1 - t #cumulative loop time since last telemetry update
			
			
			#send telemetry 
			t_telem = (time.perf_counter()-stime)
			if  ((t_telem % 1) < (t % 1)):
				if int(t_1 % 5) ==0 : 
					#((t_telem % 1) < (t % 1)) will detect when time jumps from .9 to 1.0 , will only happen once per second
					#(t_1 // 5 ==1) detects when time is integer multiples of 5
					
					print("send telemetry at:", t_telem )
					#send data
				
				
			if LOOP_TIME - (t_1-t) > 0:
				time.sleep(LOOP_TIME - (t_1-t)) #sleeping until dt = loop time
			
			
			
			#time.sleep(1-t_1 % 1) # sleep until time top of next second 
			#time.sleep(0.1) # Sleep 1 sec
			
		# End time loop	
		pi.set_PWM_dutycycle(Motor1E, 0)
		pi.write(Motor1A, 0)
		pi.write(Motor1B, 0)
		#pi.stop()
		print("Motors stopped")
		
		
	except Exception as e:
                client_socket.sendall(f"Error in starting log: {str(e)}\n".encode('utf-8'))
	finally:
		file.close()
		print("closed file\n")
		pi.write(Motor1A, 0)
		pi.write(Motor1B, 0)
		pi.stop()
		stop_melt()
		print("end of experiment")



def shutdown(client_socket):
	global thermocouple_recording, thermocouple_is_running,camera_is_running, is_running, light_is_running, cal3300_is_running,picam2
	try:
		#stop_camera()
		#stop_motors()
		light_turn_off_client(client_socket) 
		thermocouple_recording= False	
		camera_is_running = False
		is_running = False
		light_is_running = False
		thermocouple_is_running = False
		cal3300_is_running = False	
	except Exception as e:
		client_socket.sendall(f"Error in shutting down: {str(e)}\n".encode('utf-8'))
		

def handle_client_connection(client_socket):
	global color, brightness, is_on, is_running, camera_is_running, picam2, thermocouple_is_running, thermocouple_recording, cal3300_is_running
	
	while True:
		try:
			data = client_socket.recv(1024).decode('utf-8').strip()
			print(f"Recieved command: {data}")
			
			if not data:
				break

			#light commands
			if data == "light_on":
				light_turn_on(client_socket,data)
				break
			elif data.startswith("light_color"):
				light_set_color_socket(client_socket, data)
				break
			elif data == "light_off":
				light_turn_off_client(client_socket)
				break
			elif data.startswith("light_brightness"):
				light_set_brightness(client_socket, data)
				break
			
			#Camera commands
			if data.startswith("start_camera"):
				if len(data.split()) > 1:
					output_file = data.split(" ", 1)[1]
				start_recording(client_socket)
				break
			elif data == "stop_camera":
				stop_recording()
				break
			elif data.startswith("rotate_camera"):
				rotate_camera(client_socket, data)
				break
			#thermocpuple commands
			elif data == "spy":
				show_data(client_socket)
				break
			elif data.startswith("spy"):
				set_timestep(client_socket, data)
				show_data(client_socket)
				break
			elif data == "stop spy":
				hide_data(client_socket)
				break
			elif data == "thermocouple_start":
				start_log(client_socket)
				break
			elif data.startswith("thermocouple_start"):
				set_timestep(client_socket, data)
				start_log(client_socket)
				break
			elif data == "thermocouple_stop":
				stop_log(client_socket)
				break
			elif data.startswith("thermocouple_stop"):
				set_timestep(client_socket, data)
				stop_log(client_socket)
				break
			elif data.startswith("thermocouple_filepath"):
				change_file_pathway(client_socket, data)
				print("changing file path")
				break
			
			
			#cal 3300 commands
			elif data.startswith("set_setpoint"):
				set_setpoint_socket(client_socket,data)
				break
			elif data == "get_temp_and_setpoint":
				get_temp_and_setpoint_socket(client_socket)
				break
			
				#TODO: add other shutdown items here
			elif data == "exit":
				
				shutdown(client_socket)
				client_socket.sendall(b"Exiting Server.\n")
				
				break
			
			#start melt commend
			
			elif data.startswith("start melt"):
				data_list = data[11:].split(",")
				start_melt(client_socket, str.strip(data_list[0]),float(data_list[1]), float(data_list[2]))
				#client_socket.sendall(b"starting melt.\n") #FIXME: something wrong with this printout
				break
			elif data == "stop melt":
				client_socket.sendall(b"Stopping Melt.\n")
				stop_melt_client(client_socket)
				
				break
			elif data.startswith("change rpm setpoint"):
				rpm = data[19:]
				change_rpm_setpoint(float(rpm))
				break
			elif data == "pause rotation":
				pause_rotation()
				client_socket.sendall(b"Pausing rotation.\n")
				break
			elif data == "resume rotation":
				resume_rotation()
				client_socket.sendall(b"Resuming rotation.\n")
				break
				
			# start casting
			elif data.startswith("start cast"):
				data_list = data[11:].split(",")
				if len(data_list) > 2:
					temp = data_list[2]
				else:
					temp = 0.0
				start_cast(client_socket, str.strip(data_list[0]), float(data_list[1]), temp)
				break
			elif data == "stop cast":
				client_socket.sendall(b"Stopping Cast.\n")
				stop_melt_client(client_socket)
				break
			elif data.startswith("start fluid experiment"):
				client_socket.sendall(b"starting fluid experiment")
				data_list = data[23:].split(",")
			
				start_fluid_rotation(client_socket, str.strip(data_list[0]),str.strip(data_list[1]), float(data_list[2]))
				break
			elif data == "stop":
				client_socket.sendall(b"Stopping all components.\n")
				shutdown(client_socket)
			else:
				client_socket.sendall(b"Invalid command.\n")
		except Exception as e:
			client_socket.sendall(f"Error: {str(e)}\n".encode('utf-8'))
			break
	client_socket.close()	



def melt_server_program():
	global pixels, light_is_running, pixel_pin, ORDER, num_pixels, brightness, color, light_is_on, is_running 
	global picam2, encoder, video_output_file, camera_is_recording,camera_is_running, rotation
	global thermocouple_is_running, thermocouple_recording, thermocouple_file_path,spy,stime,timestep, thermocouple, thermocouple2
	global temp_read_frame, setpoint_read_frame, t0, temp_crc, ser, cal3300_is_running
	
	
	global exper_folder, melt_running, experiment_rpm_setpoint
	
	#overall setup
	is_running = True
	melt_running = False
	exper_folder = "/home/pi/Data/data_temp" #default
 	#light setup
	pixel_pin = board.D18
	ORDER = neopixel.GRBW
	num_pixels = 24
	brightness = 0.5
	color = [250,250,250] # Defualt color
	light_is_on = False
	light_is_running = True
	is_running = True
	pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5,auto_write=False, pixel_order = ORDER)
	
	#camera setup
	#picam2 = Picamera2()
	encoder = H264Encoder(bitrate=1000000)
	video_output_file = "Video/output_video.h264"
	camera_is_recording = False
	#camera_is_running = True
	rotation = False
	
	#thermocouple setup
	#settings
	spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)

	# Thermocouple 1 (GPIO 5)
	#alloctate cs pin and set direction
	cs = digitalio.DigitalInOut(board.D5)
	cs.direction = digitalio.Direction.OUTPUT
	thermocouple = adafruit_max31865.MAX31865(spi,cs)
	
	# Thermocouple 2 (GPIO 6)
	#alloctate cs pin and set direction
	cs2 = digitalio.DigitalInOut(board.D6)
	cs2.direction = digitalio.Direction.OUTPUT
	thermocouple2 = adafruit_max31865.MAX31865(spi,cs2)


	stime =time.perf_counter() 
	thermocouple_is_running = True
	thermocouple_recording = False
	spy = False
	thermocouple_file_path = "templog.txt"
	timestep = 0.5
	
	

	#setup motor
	
	
	
	#cal controller setup
	# Set the serial hexadecimal message to request temperature and setpoint data
	temp_read_frame =     [0x01,0x03,0x00,0x1C,0x00,0x01,0x45,0xCC] #request frame for temperature
	setpoint_read_frame = [0x01,0x03,0x00,0x7F,0x00,0x01,0xB5,0xD2] #request frame for setpoint temperature
	cal3300_is_running = True

	temp_crc = add_crc(bytes([0x01,0x03,0x00,0x1C,0x00,0x01]))
	t0=time.time()
	
	# Set serial port fpr cal controller
	ser=serial.Serial(
		port='/dev/ttyUSB0', # Serial port /dev/ttyUSB0
		baudrate=9600,       # Data rate
		bytesize=serial.EIGHTBITS,      # Data bits
		stopbits =serial.STOPBITS_ONE,  # Stop bits
		parity = serial.PARITY_NONE,    # Parity
		timeout=1, # Timeout (s)
	)

	ser.flush() #clear any junk data 
	
	#Set serial port for telemetry downlink
	#telem = serial.Serial(port ='/dev/ttyUSB1', baudrate=115200) #open serial port
	#print(telem.name()) #check which port was really used
	#telem.write(b'\"Temperature1\":98.3,\"experiment_time\":10.45') #write a string
	#telem.close() #close port
	
	
	#server info
	host = "localhost"
	port = 65433
	
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((host,port))
	server_socket.listen(5)
	
	print("Melting Server started. Waiting for connections...")
	
	while is_running:
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
			is_running = False
	print("Server stopped.")
	server_socket.close()

if __name__ == "__main__":
	melt_server_program()
