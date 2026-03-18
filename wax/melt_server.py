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
import csv

import pigpio
import rotary_encoder

import SoloPy as solo

# Cal3300 imports
from pymodbus.utilities import computeCRC
import serial
#thermocoupel imports
import adafruit_max31856 # Wrong package us 31865
import adafruit_max31865 

# ######################################################################
# Threading
# ######################################################################

# Stop log events
stop_log_motor_event = threading.Event()
stop_log_thermo_event = threading.Event()
stop_log_cal_event = threading.Event()

# Thread handles
log_motor_thread = None
log_thermo_thread = None
log_cal_thread = None




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

def show_temp_data(client_socket):
	''' Print thermocouple temperature data to the terminal '''
	global stime, spy_temp, timestep_thermocouple, thermocouple, thermocouple2

	if spy_temp == True:
		client_socket.sendall(b"Already showing data.\n")
		return
	
	try:
		spy_temp = True
		client_socket.sendall(b"Showing Data:")
		print(spy_temp)
		while spy_temp:
			#print("here")
			temp = thermocouple.temperature
			temp2 = thermocouple2.temperature
			t = (time.perf_counter()-stime)
			print("Time {:.2f} s Temp1: {:.2f}, Temp2: {:.2f}".format(t,temp,temp2))
			time.sleep(timestep_thermocouple)
	except Exception as e:
		client_socket.sendall(f"Error in starting spy: {str(e)}\n".encode('utf-8'))


def hide_temp_data(client_socket):
	''' Hide terminal printouts of thermocouple temperature data '''
	global spy_temp
	
	if spy_temp == False:
		client_socket.sendall(b"Already hiding data.\n")
		return
	try:
		spy_temp = False
		client_socket.sendall(b"Hiding Data\n")
	except Exception as e:
		client_socket.sendall(f"Error in stopping spy: {str(e)}\n".encode('utf-8'))

def set_thermocouple_timestep_client(client_socket, dt):
	global timestep_thermocouple
	try:
		#index = data.find(" ")
		#new_timestep = data[index+1:]
		timestep_thermocouple = float(dt)
		#client_socket.sendall(f"Updated thermocouple_timestep = {str(timestep_thermocouple)}".encode('utf-8'))
	except Exception as e:
		client_socket.sendall(f"Error in updating timestep: {str(e)}\n".encode('utf-8'))

def set_thermocouple_timestep(dt):
	global timestep_thermocouple
	try:
		#index = data.find(" ")
		#new_timestep = data[index+1:]
		timestep_thermocouple = float(dt)
		print("Updated thermocouple_timestep = {}".format(timestep_thermocouple))
	except Exception as e:
		print("Error in updating timestep: " + e)


def start_log_thermocouple_client(client_socket):
	''' Log thermocouple temprature data to a txt file '''
	global thermocouple_file_path,stime, timestep_thermocouple, thermocouple, thermocouple2, exper_file
	# global thermocouple_recording
	
	try:
		client_socket.sendall(f"Starting thermocouple log. Timestep = {timestep_thermocouple}".encode('utf-8'))
	except:
		pass

	try:
		#thermocouple_file_path = os.path.join(exper_folder, os.path.basename("thermo_log.txt"))
		#file = open(thermocouple_file_path, "w")
		
		thermocouple_file_path = os.path.join(exper_folder, os.path.basename("thermo_log.csv"))
		with open(thermocouple_file_path, "w", newline="") as file:
		
			
			# Create csv writer
			writer = csv.writer(file, delimiter=',')
			
			# Write header
			writer.writerow(["time_s","Temp1","Temp2"])
			
			thermocouple_recording = True
			
			print("Starting thermocouple log. Timestep = {}".format(timestep_thermocouple))
			
			# Time loop
			while not stop_log_thermo_event.is_set(): # while thermocouple_recording:
				
				# Read thermocouple data
				temp = thermocouple.temperature
				temp2 = thermocouple2.temperature
				t = (time.perf_counter()-stime)
				
				# Write to file
				#file.write("Time {:.2f} s Temp1: {:.2f} Temp2: {:.2f}\n".format(t,temp,temp2))
				writer.writerow([round(t,3), round(temp,3), round(temp2,3)])
				file.flush()
				
				# Sleep
				time.sleep(timestep_thermocouple)
				
			print("closed file")
		
	except Exception as e:
                print("Error in starting log: " + e)
	finally:
		file.close()

def stop_log_thermocouple(client_socket):
	''' Stop logging thermocouple data to file '''
	
	if stop_log_thermo_event.is_set(): # if motor_recording == False
		client_socket.sendall(b"Alread stopped thermocouple log\n")
		return
	try:
		stop_log_thermo_event.set() #thermocouple_recording = False
		print("Log thermo stop signal sent")
		#client_socket.sendall(b"Stopping thermo log")
	except Exception as e:
		client_socket.sendall(f"Error in stopping thermo log: {str(e)}\n".encode('utf-8'))




def start_log_melt():
        global thermocouple_recording, thermocouple_file_path,stime, timestep_melt, thermocouple, thermocouple2, exper_file

        try:
                thermocouple_file_path = os.path.join(exper_folder, os.path.basename("thermo_log.txt"))
                file = open(thermocouple_file_path, "w")
                thermocouple_recording = True
                while thermocouple_recording:
                        temp = thermocouple.temperature
                        temp2s = thermocouple2.temperature
                        t = (time.perf_counter()-stime)
                        file.write("Time {:.2f} s temperature: {:.2f}\n".format(t,temp))
                        file.flush()
                        time.sleep(timestep_melt)
                print("closed file")
        except Exception as e:
                pass
        finally:
                file.close()


		
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
	''' Serial command to read temperature and setpoint temperature. Sleep time = 2x0.1s '''
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
	''' Serial command to read temperature and setpoint temperature. Sleep time = 2x0.1s '''
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
	''' Serial command to change setpoint temperature. Sleep time = 2x0.1s '''
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
		
		# Write 1st message and return buffer
		ser.write(first_message)
		print("sent first message (enter program mode)")
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			print('recieved: ',buf.hex())
		else:
			print('Temperature: no data recieved')

		# Write 2nd message and return buffer
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
	''' Serial command to change setpoint temperature. Sleep time = 2x0.1s '''
	global ser
	try:
		#construct serial messages
		first_message = add_crc(bytes([0x01,0x06,0x03,0x00,0x00,0x05]))
		second_message = add_crc(bytes([0x01,0x06,0x15,0x00,0x00,0x00]))
		#setpoint_message = add_crc(bytes([0x01,0x06,0x00,0x7F, ])) #setpoint 1B0 = 432 = 43.2 C
		exit_program_mode = add_crc(bytes([0x01,0x06,0x03,0x00,0x00,0x06]))
		exit_program_mode_2nd = add_crc(bytes([0x01,0x06,0x16,0x00,0x00,0x00]))
		setpoint_message = create_setpoint_message(temp)

		# Write 1st message and return buffer
		ser.write(first_message)
		#print("sent first message (enter program mode)")
		time.sleep(0.1) #wait 0.1 seconds
		if ser.in_waiting>0:
			buf = ser.read(ser.in_waiting) #read all available bytes
			#print('recieved: ',buf.hex())
		#else:
			#print('Temperature: no data recieved')

		# Write 2nd message and return buffer
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

def set_CAL_timestep_client(client_socket, dt):
	global timestep_CAL
	try:
		#index = data.find(" ")
		#new_timestep = data[index+1:]
		timestep_CAL = float(dt)
		#client_socket.sendall(f"Updated timestep_CAL = {str(timestep_CAL)}".encode('utf-8'))
	except Exception as e:
		client_socket.sendall(f"Error in updating timestep: {str(e)}\n".encode('utf-8'))


def start_log_CAL_client(client_socket):
	''' Log CAL temperature controller ata to a txt file '''
	global CAL_file_path, stime, timestep_CAL, exper_file
	global CAL_recording
	
	
	try:
		client_socket.sendall(f"Starting CAL log. Timestep = {timestep_CAL}".encode('utf-8'))
	except:
		pass
		
	
	try:
		#CAL_file_path = os.path.join(exper_folder, os.path.basename("CAL_log.txt"))
		#file = open(CAL_file_path, "w")
		
		CAL_file_path = os.path.join(exper_folder, os.path.basename("CAL_log.csv"))
		with open(CAL_file_path, "w", newline="") as file:
		
			CAL_recording = True
			
			# Create csv writer
			writer = csv.writer(file, delimiter=',')
			
			# Write header
			writer.writerow(["time_s","Temp","Setpoint"])
			
			# Time loop
			while not stop_log_cal_event.is_set(): #while CAL_recording:
				
				# Read temp, setpoint data
				temp_cal, setpoint = get_temp_and_setpoint(sleep_time = 0.05) # Read data
				t = (time.perf_counter()-stime)
				
				# Write
				#file.write("Time {:.2f} s Temp: {:.2f} Setpoint: {:.2f}\n".format(t,temp_cal,setpoint))
				writer.writerow([round(t,3), round(temp_cal,3), round(setpoint,3)])
				file.flush()
				
				# Sleep
				time.sleep(timestep_CAL)
			
		print("closed file")
	except Exception as e:
                client_socket.sendall(f"Error in starting log: {str(e)}\n".encode('utf-8'))
	finally:
		file.close()

def stop_log_CAL(client_socket):
	''' Stop logging CAL data to file '''
	
	if stop_log_cal_event.is_set():
		client_socket.sendall(b"Alread stopped cal log log\n")
		return
	try:
		stop_log_cal_event.set() #motor_recording = False
		print("Log CAL stop signal sent")
		#client_socket.sendall(b"Stopping CAL log")
	except Exception as e:
		client_socket.sendall(f"Error in stopping CAL log: {str(e)}\n".encode('utf-8'))



# ######################################################################		
# Motor commands (SOLO)
# ######################################################################

def instantiate_solo_client(client_socket): 
	''' Instantiate solo handle '''
	global mySolo
	
	try:
		mySolo = solo.SoloMotorControllerUart("/dev/ttyACM0", 0, solo.UartBaudRate.RATE_937500)
		client_socket.sendall(b"Connecting to SOLO\n")
	except Exception as e:
		client_socket.sendall(f"Error in instantiating SOLO: {str(e)}\n".encode('utf-8'))

	return
	
def connect_to_solo_client(client_socket): 
	''' Connect to solo '''
	global mySolo, communication_is_working
	
	
	# wait here till communication is established
	#print("Trying to Connect To SOLO")
	client_socket.sendall(f"Trying to connect To SOLO".encode('utf-8'))
	communication_is_working = False
	
	try:
		while communication_is_working is False:
			time.sleep(1)
			communication_is_working, error = mySolo.communication_is_working()
		print("Communication Established succuessfully!")
		client_socket.sendall("Communication established succuessfully".encode('utf-8'))
		time.sleep(3)
	except Exception as e:
		client_socket.sendall(f"Error in instantiating SOLO: {str(e)}\n".encode('utf-8'))

def reset_solo_settings_client(client_socket): 
	''' Configure solo with default settings '''
	global mySolo, gear_ratio, rpm_limit
	
	try:
		print("\nSOLO Motor Settings")
	
		# Fixed settings
		numberOfPoles = 4 # Motor's Number of Poles
		numberOfEncoderLines = 1024 # Motor's Number of Encoder Lines (PPR pre-quad)
		mySolo.set_motor_type(solo.MotorType.BLDC_PMSM) # Motor type
		mySolo.set_motor_poles_counts(4) # Motor's Number of Poles (4)
		mySolo.set_incremental_encoder_lines(numberOfEncoderLines)
		print("Motor type: ", mySolo.get_motor_type())
		print("Motor poles count: ", mySolo.get_motor_poles_counts())
		print("Incremental encoder lines: ", mySolo.get_incremental_encoder_lines())
		
		# Control mode
		mySolo.set_feedback_control_mode(solo.FeedbackControlMode.ENCODERS) # Use Encoders for sensing
		mySolo.set_control_mode(solo.ControlMode.SPEED_MODE) # Speed control mode
		mySolo.set_command_mode(solo.CommandMode.DIGITAL)    # Digital mode
		print("Command mode: ", mySolo.get_command_mode())
		print("Control mode: ", mySolo.get_control_mode())
		print("Control feedback mode: ", mySolo.get_feedback_control_mode())
		
		# PWM and Current limit
		pwmFrequency = 80  # Desired Switching or PWM Frequency at Output (80 khz)
		currentLimit = 3.5 # Current Limit of the Motor (3.5 Amps)
		mySolo.set_output_pwm_frequency_khz(pwmFrequency)
		mySolo.set_current_limit(currentLimit)
		print("Output PWM Frequency (khz)", mySolo.get_output_pwm_frequency_khz())
		print("Current limit (A)", mySolo.get_current_limit())
		
		# PID settings
		speedControllerKp = 0.2219924 # Speed controller Kp
		speedControllerKi = 0.0070648 # Speed controller Ki
		mySolo.set_speed_controller_kp(speedControllerKp)
		mySolo.set_speed_controller_ki(speedControllerKi)
		print("Speed controller kp: ", mySolo.get_speed_controller_kp())
		print("Speed controller ki: ", mySolo.get_speed_controller_ki())
		
		# Acceleration/Deceleration, Speed limit values
		speedAccelValue = 5.0 # Speed acceleration value (rev/s/s)
		speedDecelValue = 5.0 # Speed deceleration value (rev/s/s)
		mySolo.set_speed_acceleration_value(speedAccelValue)
		mySolo.set_speed_deceleration_value(speedDecelValue)
		speedLimit = 700*24 # Speed limit (rpm)
		mySolo.set_speed_limit(speedLimit)
		print("Speed acceleration value", mySolo.get_speed_acceleration_value()) # Rev/s/s
		print("Speed deceleration value", mySolo.get_speed_deceleration_value())
		print("Speed limit", mySolo.get_speed_limit())
		
		# Other	
		print("encoder_hall_ccw_offset", mySolo.get_encoder_hall_ccw_offset())
		print("encoder_hall_cw_offset", mySolo.get_encoder_hall_cw_offset())
		print("Board temperature (C)", mySolo.get_board_temperature())
		print("Motor resistance (Ohm)", mySolo.get_motor_resistance())
		print("Motor inductance (H)", mySolo.get_motor_inductance())
		
		print("Communication is working", mySolo.communication_is_working())
		print("Motion profile mode", mySolo.get_motion_profile_mode())
		
		# Motor speed limit
		rpm_limit = 200*gear_ratio # Maximum allowed speed (motor)
		print("Motor speed limit (RPM)", rpm_limit)
		
		client_socket.sendall(b"SOLO parameters set\n")

		
	except Exception as e:
		client_socket.sendall(f"Error in reseting SOLO settings: {str(e)}\n".encode('utf-8'))

	return
	
def get_solo_settings_client(client_socket): 
	''' Get current solo settings '''
	global mySolo, gear_ratio, rpm_limit
	
	try:
		print("\nSOLO Motor Settings")
	
		# Fixed settings
		print("Motor type: ", mySolo.get_motor_type())
		print("Motor poles count: ", mySolo.get_motor_poles_counts())
		print("Incremental encoder lines: ", mySolo.get_incremental_encoder_lines())
		
		# Control mode
		print("Command mode: ", mySolo.get_command_mode())
		print("Control mode: ", mySolo.get_control_mode())
		print("Control feedback mode: ", mySolo.get_feedback_control_mode())
		
		# PWM and Current limit
		print("Output PWM Frequency (khz)", mySolo.get_output_pwm_frequency_khz())
		print("Current limit (A)", mySolo.get_current_limit())
		
		# PID settings
		print("Speed controller kp: ", mySolo.get_speed_controller_kp())
		print("Speed controller ki: ", mySolo.get_speed_controller_ki())
		
		# Acceleration/Deceleration, Speed limit values
		print("Speed acceleration value", mySolo.get_speed_acceleration_value()) # Rev/s/s
		print("Speed deceleration value", mySolo.get_speed_deceleration_value())
		print("Speed limit", mySolo.get_speed_limit())
		
		# Other	
		print("encoder_hall_ccw_offset", mySolo.get_encoder_hall_ccw_offset())
		print("encoder_hall_cw_offset", mySolo.get_encoder_hall_cw_offset())
		print("Board temperature (C)", mySolo.get_board_temperature())
		print("Motor resistance (Ohm)", mySolo.get_motor_resistance())
		print("Motor inductance (H)", mySolo.get_motor_inductance())
		
		print("Communication is working", mySolo.communication_is_working())
		print("Motion profile mode", mySolo.get_motion_profile_mode())
		
		print("Motor speed limit (RPM)", rpm_limit)

		
	except Exception as e:
		client_socket.sendall(f"Error in reading SOLO settings: {str(e)}\n".encode('utf-8'))

	return
	
# TODO: add setters for individual motor settings

def set_solo_accel_client(client_socket,val): 
	''' Set acceleration value. '''
	global mySolo
	
	try:
		mySolo.set_speed_acceleration_value(val)
		print("Speed acceleration value (rev/s/s)", mySolo.get_speed_acceleration_value())
		
	except Exception as e:
		client_socket.sendall(f"Error in setting value: {str(e)}\n".encode('utf-8'))

	return

def set_solo_decel_client(client_socket,val): 
	''' Set deceleration value. '''
	global mySolo
	
	try:
		mySolo.set_speed_deceleration_value(val)
		print("Speed deceleration value (rev/s/s)", mySolo.get_speed_deceleration_value())
		
	except Exception as e:
		client_socket.sendall(f"Error in setting value: {str(e)}\n".encode('utf-8'))

	return
	
def set_motor_speed_limit_client(client_socket,val): 
	''' Set acceleration value. '''
	global mySolo, rpm_limit
	
	#TODO: Consider adding a global max speed limit as a fail safe
	
	# Max continuous PRM = 12,000 RPM
	# Max intermittent RPM = 15,000 RPM
	
	try:
		
		if val > 12000:
			val = 12000
			print("Warning! Max continous motor speed is 12000 RPM. Setting RPM limit to 12000")
		
		rpm_limit = val
		print("Morot speed limit (RPM)", rpm_limit)
		
	except Exception as e:
		client_socket.sendall(f"Error in setting value: {str(e)}\n".encode('utf-8'))

	return

	
def stop_rotation_client(client_socket): 
	''' Stop rotation. Set target motor speed to zero. Using current deceleration value. '''
	global mySolo
	
	try:
		print("\nStopping rotation")
		print("Speed deceleration value", mySolo.get_speed_deceleration_value())
		mySolo.set_speed_reference(0.) #this is motor speed not shaft speed
		
		
		#client_socket.sendall(b"SOLO parameters set\n")

		
	except Exception as e:
		client_socket.sendall(f"Error in stopping rotation: {str(e)}\n".encode('utf-8'))

	return
	
def set_target_motor_speed_client(client_socket, rpm): 
	''' Set target motor speed. Using current accel/decel values. '''
	global mySolo, rpm_limit
	
	try:
		
		#rpm_limit = 200*24 # Maximum allowed speed
		
		if rpm >= rpm_limit :
			rpm = rpm_limit
			print("\nRequested speed too high. Resetting to max speed (RPM):",str(rpm))
		
		client_socket.sendall(f"Setting target motor speed (RPM): {str(rpm)}\n".encode('utf-8'))
		
		print("\nSetting target motor speed (RPM):",str(rpm))
		print("Speed acceleration value", mySolo.get_speed_acceleration_value())
		print("Speed deceleration value", mySolo.get_speed_deceleration_value())
		mySolo.set_speed_reference(rpm) #this is motor speed not shaft speed
		
		
		#client_socket.sendall(b"SOLO parameters set\n")

		
	except Exception as e:
		client_socket.sendall(f"Error in stopping rotation: {str(e)}\n".encode('utf-8'))

	return
	
def set_target_load_speed_client(client_socket, rpm_load): 
	''' Set target load speed. Using current accel/decel values. '''
	global mySolo, gear_ratio, rpm_limit
	
	#gear_ratio = 23.76 # Gear ratio
	
	# rpm is requested load speed.
	# Multiply by gear ratio to get target motor speed
	rpm = gear_ratio*rpm_load
	
	try:
		
		#rpm_limit = 200*24 # Maximum allowed speed (motor)
		
		if rpm >= rpm_limit :
			rpm = rpm_limit
			print("\nRequested speed too high. Resetting to max speed (RPM):",str(rpm))
		
		# FIXME: something wrong with sendall when running stop melt
		#client_socket.sendall(f"Setting target load speed (RPM): {str(rpm/gear_ratio)}\n".encode('utf-8'))
		
		print("\nSetting target load speed (RPM):",str(rpm/gear_ratio))
		print("Speed acceleration value", mySolo.get_speed_acceleration_value())
		print("Speed deceleration value", mySolo.get_speed_deceleration_value())
		mySolo.set_speed_reference(rpm) #this is motor speed not shaft speed
		
		#client_socket.sendall(b"SOLO parameters set\n")

		
	except Exception as e:
		client_socket.sendall(f"Error in stopping rotation: {str(e)}\n".encode('utf-8'))

	return
	
def spy_motor_speed_data(client_socket):
	''' Print motor speed data to screen '''
	global stime,spy_motor_flag, timestep_motor, mySolo

	if spy_motor_flag == True:
		client_socket.sendall(b"Already showing data.\n")
		return
	
	try:
		spy_motor_flag = True
		client_socket.sendall(b"Showing motor speed data:")
		print(spy_motor_flag)
		
		gear_ratio = 23.76 # Gear ratio
		
		while spy_motor_flag:
			#print("here")
			
			# Get the current speed and torque
			actualMotorSpeed, error = mySolo.get_speed_feedback()
			rpm_setpoint, error = mySolo.get_speed_reference()
			#rpm_setpoint = 0.0
			
			t = (time.perf_counter()-stime)
			print("Time {:.2f} s Shaft speed: {:.2f}, Motor speed: {:.2f}, Ref motor speed: {:.2f}".format(t,actualMotorSpeed/gear_ratio, actualMotorSpeed, rpm_setpoint))
			time.sleep(timestep_motor)
	except Exception as e:
		client_socket.sendall(f"Error in starting spy: {str(e)}\n".encode('utf-8'))

	return
	
def hide_motor_speed_data(client_socket):
	global spy_motor_flag 
	
	if spy_motor_flag  == False:
		client_socket.sendall(b"Already hiding data.\n")
		return
	try:
		spy_motor_flag  = False
		client_socket.sendall(b"Hiding Data\n")
	except Exception as e:
		client_socket.sendall(f"Error in stopping spy: {str(e)}\n".encode('utf-8'))



def start_log_motor_client(client_socket):
	''' Log motor data to a txt file '''
	global mySolo
	global motor_file_path, stime, timestep_motor, exper_file
	global motor_recording
	
	# Motor parameters
	gear_ratio = 23.76 # Gear ratio
	kt = 5.9e-3 # Motor torque constant (N.m/A) 5.9 mN.m/A = 5.9e-3 N.m/A for Faulhaber 2264 BP4

	try:
		
		try:
			client_socket.sendall(f"Starting motor log. Timestep = {timestep_motor}".encode('utf-8'))
		except:
			pass
		
		
		#motor_file_path = os.path.join(exper_folder, os.path.basename("motor_log.txt"))
		#file = open(motor_file_path, "w")
		
		# Csv file
		motor_file_path = os.path.join(exper_folder, os.path.basename("motor_log.csv"))
		
		with open(motor_file_path, mode='w', newline="") as file:
			
			# Create csv writer
			writer = csv.writer(file, delimiter=',')
			
			# Write header
			writer.writerow(["time_s","shaft_speed","motor_speed","ref_motor_speed","iq","motor_torque","load_torque"])
		
			# Time loop
			while not stop_log_motor_event.is_set(): # while motor_recording:
				
				# Get the current speed and torque
				motor_speed, error = mySolo.get_speed_feedback() # Speed of motor (RPM)
				rpm_setpoint, error = mySolo.get_speed_reference() # Reference speed of motor (RPM)
				motor_Iq, error = mySolo.get_quadrature_current_iq_feedback() # Motor quatrature current (A)
				
				# Computations
				load_speed = motor_speed/gear_ratio # Load speed (RPM)
				motor_torque = motor_Iq*kt # Motor torque (N.m)
				load_torque = motor_torque*gear_ratio # Load torque (N.m)
				
				# Get time
				t = (time.perf_counter()-stime)
				
				# Write to file
				#file.write("Time {:.2f} s Shaft speed: {:.2f}, Motor speed: {:.2f}, Ref motor speed: {:.2f}\n".format(t,motor_speed/gear_ratio, motor_speed, rpm_setpoint))
				writer.writerow([round(t,3), round(load_speed,3), round(motor_speed,3), round(rpm_setpoint,3), round(motor_Iq,6), round(motor_torque,6), round(load_torque,6)])
				file.flush()
				
				# Timestep
				time.sleep(timestep_motor)
				
			print("closed file")
		
	except Exception as e:
                client_socket.sendall(f"Error in starting log: {str(e)}\n".encode('utf-8'))
	finally:
		file.close()

def stop_log_motor(client_socket):
	''' Stop logging motor data to file '''
	global motor_recording
	
	
	if stop_log_motor_event.is_set(): # if motor_recording == False
		client_socket.sendall(b"Alread stopped motor log\n")
		return
	try:
		stop_log_motor_event.set() #motor_recording = False
		print("Log motor stop signal sent")
		#client_socket.sendall(b"Stopping motor log")
	except Exception as e:
		client_socket.sendall(f"Error in stopping motor log: {str(e)}\n".encode('utf-8'))

def set_motor_timestep_client(client_socket, dt):
	global timestep_motor
	try:
		#index = data.find(" ")
		#new_timestep = data[index+1:]
		timestep_motor = float(dt)
		#client_socket.sendall(f"Updated timestep_motor = {str(timestep_motor)}".encode('utf-8'))
	except Exception as e:
		client_socket.sendall(f"Error in updating timestep: {str(e)}\n".encode('utf-8'))

def set_motor_timestep(dt):
	global timestep_motor
	try:
		#index = data.find(" ")
		#new_timestep = data[index+1:]
		timestep_motor = float(dt)
		print("Updated timestep_motor = {}".format(timestep_motor))
	except Exception as e:
		print("Error in updating timestep: " + e)


def motor_ramp_updown_const_accel(client_socket, peak_rpm, t_start_delay=5., t_idle=20., t_stop_delay=20.):
	''' 
	Motion profile ramp up/down at constant acceleration. 
	
	accel = Speed acceleration/deceleration value (rev/s/s)
	
	# Ramp profile
	# 
	# RPM
	# ^             Idle
	# |            ________
	# |           /        \ 
	# |          /          \
	# |_________/            \____________
	# -------------------------------------> Time
	# start_delay             stop_delay
	#
	# t_start_delay = time before start of ramp up
	# t_idle = idle time at peak rpm
	# t_stop_delay = idle time at end of ramp down
	'''
	global mySolo
	
	gear_ratio = 23.76 # Gear ratio
	target_motor_speed = peak_rpm*gear_ratio # Motor speed
	
	
	# Start delay
	print("Start deltay: waiting for {} s".format(t_start_delay))
	time.sleep(t_start_delay)
	
	# Ramp up
	mySolo.set_speed_reference(target_motor_speed) # Change setpoint to target speed
	print("Ramping up to {} RPM".format(peak_rpm))
	while True:
		# Get time
		t = time.time() - t0 # Loop time
			
		# Get the current speed and torque
		actualMotorSpeed, error = mySolo.get_speed_feedback()
		#actualMotorTorque, error = mySolo.get_quadrature_current_iq_feedback()
		#print("time: " + str(t) + "s. " + "Motor Speed: " + str(actualMotorSpeed) + " RPM. " + "Measured Iq/Torque[A]: " + str(actualMotorTorque))
		time.sleep(1)
		
		if abs(actualMotorSpeed - target_motor_speed) <= 1.0:
			# Achieved target speed. End loop
			print("Achieved target speed")
			break
		
		# Timeout for safety
		# If takes too long to achieve target speed, break look.	
		if t>120.: # Set timeout at 2 minutes 
			# End loop
			print("Error: Did not achieved target speed")
			break
	
	# Idle
	print("Idle: waiting for {} s".format(t_idle))
	time.sleep(t_idle) # Wait for idle time.
	
	# Ramp up
	mySolo.set_speed_reference(0.) # Change setpoint to target speed
	print("Ramping down to 0 RPM")
	while True:
		# Get time
		t = time.time() - t0 # Loop time
			
		# Get the current speed and torque
		actualMotorSpeed, error = mySolo.get_speed_feedback()
		#actualMotorTorque, error = mySolo.get_quadrature_current_iq_feedback()
		#print("time: " + str(t) + "s. " + "Motor Speed: " + str(actualMotorSpeed) + " RPM. " + "Measured Iq/Torque[A]: " + str(actualMotorTorque))
		time.sleep(1)
		
		if abs(actualMotorSpeed - 0.) <= 1.0:
			# Achieved target speed. End loop
			print("Motor stopped")
			break
		
		# Timeout for safety
		# If takes too long to achieve target speed, break look.	
		if t>120.: # Set timeout at 2 minutes 
			# End loop
			print("Error: Did not achieve 0 RPM")
			break
	
	# Stop delay
	print("Stop deltay: waiting for {} s".format(t_stop_delay))
	time.sleep(t_stop_delay)
	print("Ramp profile complete")
	
	return



# ######################################################################		
# (OLD) Motor commands
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
def create_folder(client_socket, prefix, label, rpm_set, temp_setpoint):

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
	exper_folder = session_file_path + "/"+prefix + "_" + str(rpm_set) + "_" + str(temp_setpoint) + "_" + str(count)
	if not os.path.exists(exper_folder):
		os.makedirs(exper_folder)
		print("created folder:", exper_folder)
	return exper_folder


# ######################################################################
# LOGGING 
# ######################################################################

def start_log_data(client_socket):
	''' Start logging of data to file. Thermometer, CAL, motor '''
	
	global log_motor_thread, log_thermo_thread, log_cal_thread # Thread handles
	
	# Stop log events
	

	
	
	# Log data from components in separate threads
	# 1. Thermocouple
	# 2. Motor
	# 3. CAL
	
	# Set sampling rates
	set_thermocouple_timestep_client(client_socket, 0.1)
	set_motor_timestep_client(client_socket, 0.1)
	set_CAL_timestep_client(client_socket, 0.1)

	# Clear stop signals before starting
	stop_log_motor_event.clear()
	stop_log_thermo_event.clear()
	stop_log_cal_event.clear()
	
	# Create threads to log data separately
	log_thermo_thread = threading.Thread(
		target=start_log_thermocouple_client,
		args=(client_socket,),
		daemon=True
	)
	
	log_cal_thread = threading.Thread(
		target=start_log_CAL_client,
		args=(client_socket,),
		daemon=True
	)
	
	log_motor_thread = threading.Thread(
		target=start_log_motor_client,
		args=(client_socket,),
		daemon=True
	)
	
	# Start the threads
	log_thermo_thread.start()
	log_cal_thread.start()
	log_motor_thread.start()
	
	print("Data logging started.")
	
	return 

def stop_log_data(client_socket):
	''' Stop logging data '''
	
	# Signal all threads to stop
	stop_log_motor_event.set()
	stop_log_thermo_event.set()
	stop_log_cal_event.set()
	
	# Optional: wait for therads to finish cleanly
	if log_thermo_thread is not None:
		log_thermo_thread.join(timeout=2)
	if log_cal_thread is not None:
		log_cal_thread.join(timeout=2)
	if log_motor_thread is not None:
		log_motor_thread.join(timeout=2)
	
	print("Stopped loggin data.")
	
	return

# ######################################################################	
# Experiments
# ######################################################################

# Experiment logs
def start_log_exp(client_socket, label, prefix, rpm_set, temp_setpoint):
	''' Start lights, camera, data logging into an experiment folder '''
	global melt_running
	global exper_folder, thermocouple_recording, motor_recording
	global rpm_setpoint, melt_running, experiment_rpm_setpoint
	global stime
	#global kp,kd,ki, ed, ei, curr_pos, pwm_range
	
	# Workflow
	# 1. Start up
	#    - lights
	#    - camera
	#    - data log
	#
	# 2. Action
	# Run as separate commands
	
	
	melt_running = True
	print_rotation = True
	
	# Step 1: Startup ----------------------------
	
	stime = time.perf_counter() # Start common start time for data log
	
	#create the experiment folder
	exper_folder = create_folder(client_socket, prefix, label, rpm_set, temp_setpoint) 
	
	#turn on lights
	light_set_color([250,250,250])
	
	#start camera recording
	try:
		start_recording(client_socket)
	except:
		print("Error starting camera")
	
	
	# Start data log (runs in background threads)
	start_log_data(client_socket)
	
	
	# Step 2. Action ------------------------
	# Run separately
	
	
	return

def stop_log_exp(client_socket):
	''' Stop experiemnt log files, turn lights/camera off '''
	
	# Motor off (TODO)
	# Camera off
	# Lights off
	# Stop data log
	
	# 1. Stop camera
	camera_is_running = False
	stop_recording()
	print("DEBUG: stop_melt_client: stop_recording")
	try:
		stop_camera()
	except:
		print("Error stopping camera")
	
	# 2. Lights off
	light_turn_off_client(client_socket)
	print("DEBUG: stop_melt_client: lights off")
	
	time.sleep(0.5)
	
	# 3. Stop data log in separate thread
	stop_log_data(client_socket)
	
	#def stop_logging():
	#	stop_log_data(client_socket)
	#	print("Stopped data log")
	#log_thread = threading.Thread(target=stop_logging)
	#log_thread.start()
	
	# Wait for logging to finish
	#log_thread.join()
	
	time.sleep(1.) # Give threads a short time to exit
	print("Stopped experiment log.")
	
	
	return




def shutdown(client_socket):
	global thermocouple_recording, thermocouple_is_running, CAL_is_running
	global motor_recording
	global camera_is_running, is_running, light_is_running, picam2
	
	try:
		#stop_camera()
		#stop_motors()
		light_turn_off_client(client_socket) 
		thermocouple_recording= False	
		motor_recording = False
		camera_is_running = False
		is_running = False
		light_is_running = False
		thermocouple_is_running = False
		CAL_is_running = False	
	except Exception as e:
		client_socket.sendall(f"Error in shutting down: {str(e)}\n".encode('utf-8'))
		

def handle_client_connection(client_socket):
	global color, brightness, is_on, is_running
	global camera_is_running, picam2
	global thermocouple_is_running, thermocouple_recording 
	global motor_recording
	global CAL_recording, CAL_is_running
	
	while True:
		try:
			data = client_socket.recv(1024).decode('utf-8').strip()
			print(f"Recieved command: {data}")
			
			if not data:
				break

			# Light commands
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
			
			# Camera commands
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
				
			# Thermocouple commands
			elif data == "spy_temp":
				# Use default timestep
				show_temp_data(client_socket)
				break
			elif data.startswith("spy_temp"):
				dt = float(data[8:])
				set_thermocouple_timestep_client(client_socket, dt)
				show_temp_data(client_socket)
				break
			elif data == "stop_spy_temp":
				hide_temp_data(client_socket)
				break
			elif data == "start_log_thermocouple":
				start_log_thermocouple_client(client_socket)
				break
			elif data.startswith("start_log_thermocouple"):
				dt = float(data[22:])
				set_thermocouple_timestep_client(client_socket, dt)
				start_log_thermocouple_client(client_socket)
				break
			elif data == "stop_log_thermocouple":
				stop_log_thermocouple(client_socket)
				break
			elif data.startswith("thermocouple_filepath"):
				change_file_pathway(client_socket, data)
				print("changing file path")
				break
			elif data.startswith("set_thermocouple_timestep"):
				dt = float(data[25:])
				set_thermocouple_timestep_client(client_socket, dt)
				break
			
			
			# CAL 3300 commands
			elif data.startswith("set_setpoint"):
				set_setpoint_socket(client_socket,data)
				break
			elif data == "get_temp_and_setpoint":
				get_temp_and_setpoint_socket(client_socket)
				break
			elif data == "start_log_CAL":
				start_log_CAL_client(client_socket)
				break
			elif data == "stop_log_CAL":
				stop_log_CAL(client_socket)
				break
			
			
			# Motor commands
			elif data.startswith("instantiate_solo"):
				instantiate_solo_client(client_socket)
				break
			elif data.startswith("connect_to_solo"):
				connect_to_solo_client(client_socket)
			elif data.startswith("solo_calibration"):
				solo_calibration(client_socket)
				break
			elif data.startswith("reset_solo_settings"):
				reset_solo_settings_client(client_socket)
				break
			elif data.startswith("get_solo_settings"):
				get_solo_settings_client(client_socket)
				break
			elif data.startswith("set_solo_accel"):
				accel = data[14:]
				set_solo_accel_client(client_socket, float(accel) )
				break
			elif data.startswith("set_solo_decel"):
				decel = data[14:]
				set_solo_decel_client(client_socket, float(decel) )
				break
			elif data.startswith("set_motor_speed_limit"):
				rpm = data[21:]
				set_motor_speed_limit_client(client_socket,float(rpm))
				break
				
			elif data.startswith("stop_rotation"):
				stop_rotation_client(client_socket)
				break
			elif data.startswith("set_target_motor_speed"):
				rpm = data[22:]			
				set_target_motor_speed_client(client_socket, float(rpm))
				break
			elif data.startswith("set_target_load_speed"):
				rpm_load = data[22:]			
				set_target_load_speed_client(client_socket, float(rpm_load))
				break
			elif data.startswith("spy_motor_speed"):
				spy_motor_speed_data(client_socket)
				break
			elif data.startswith("hide_motor_speed"):
				hide_motor_speed_data(client_socket)
				break
			elif data == "start_log_motor":
				start_log_motor_client(client_socket)
			elif data == "stop_log_motor":
				stop_log_motor(client_socket)
				break
			elif data.startswith("set_motor_timestep"):
				dt = float(data[18:])
				set_motor_timestep_client(client_socket, dt)
				break
			
			# Ramp profiles
			elif data.startswith("motor_ramp_updown_const_accel"):
				data_list = data[29:].split(",") # peak_rpm, accel, t_start_delay, t_idle, t_stop_delay
				peak_rpm = float(data_list[0]) # Required parameter
				# TODO: parse optional parameters
				motor_ramp_updown_const_accel(client_socket, peak_rpm, t_start_delay=5., t_idle=20., t_stop_delay=20.)
				break
			
			
				
			# Logging commands
			elif data == "start_log_data":
				start_log_data(client_socket)
				break
			elif data == "stop_log_data":
				stop_log_data(client_socket)
				break
			# Experiment logging commands
			elif data.startswith("start_log_exp"):
				data_list = data[14:].split(",") # label, exp_type, 
				if len(data_list) > 3:
					temp = data_list[3]
				else:
					temp = 0.0
				start_log_exp(client_socket, str.strip(data_list[0]), str.strip(data_list[1]),  float(data_list[2]), temp)
				break
			elif data == "stop_log_exp":
				client_socket.sendall(b"Stopping Experiment Log.\n")
				stop_log_exp(client_socket)
				break
			
			
			
			
				
			# FIXME: (OLD) Motor commands ------------------------------
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
			# ----------------------------------------------------------
			# Experiemnts
				
			
				
			# Fluid experiments
			elif data.startswith("start fluid experiment"):
				client_socket.sendall(b"starting fluid experiment")
				data_list = data[23:].split(",")
			
				start_fluid_rotation(client_socket, str.strip(data_list[0]),str.strip(data_list[1]), float(data_list[2]))
				break
			
			
			
			# Exit commands --------------------------------------------
			#TODO: add other shutdown items here
			elif data == "exit":
				
				shutdown(client_socket)
				client_socket.sendall(b"Exiting Server.\n")
				
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
	global thermocouple_is_running, thermocouple_recording, thermocouple_file_path, timestep_thermocouple, thermocouple, thermocouple2
	global CAL_recording, CAL_is_running, CAL_file_path, timestep_CAL
	global motor_file_path, motor_recording, timestep_motor
	global spy_temp, stime, timestep_melt  
	global temp_read_frame, setpoint_read_frame, t0, temp_crc, ser
	global mySolo # SOLO motor driver instance
	global spy_motor_flag, gear_ratio, rpm_limit
	
	global exper_folder, melt_running, experiment_rpm_setpoint
	
	#overall setup
	is_running = True
	melt_running = False
	
	# Temporary data folder (when not running experiments)
	exper_folder = "/home/pi/Data" # default temporary data folder when not running experiment
	
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

	# Loop start time and timestep
	stime =time.perf_counter()
	timestep_thermocouple = 0.5
	timestep_motor = 0.5
	timestep_melt = 0.5
	timestep_CAL = 0.5
	
	# Logic flags for running loops
	thermocouple_is_running = True
	thermocouple_recording = False
	CAL_recording = False
	motor_recording = False
	spy_temp = False
	thermocouple_file_path = "thermo_log.txt"
	motor_file_path = "motor_log.txt"
	CAL_file_path = "CAL_log.txt"
	

	# Motor setup
	spy_motor_flag = False
	gear_ratio = 23.76 # Gear ratio
	rpm_limit = 200*gear_ratio # Maximum allowed speed (motor)
	# Note: this will fail if no power to motor
	try:
		mySolo = solo.SoloMotorControllerUart("/dev/ttyACM0", 0, solo.UartBaudRate.RATE_937500)
	except:
		print("Warning: No connection to SOLO. Check power.")
	
	
	#cal controller setup
	# Set the serial hexadecimal message to request temperature and setpoint data
	temp_read_frame =     [0x01,0x03,0x00,0x1C,0x00,0x01,0x45,0xCC] #request frame for temperature
	setpoint_read_frame = [0x01,0x03,0x00,0x7F,0x00,0x01,0xB5,0xD2] #request frame for setpoint temperature
	CAL_is_running = True

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
