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

import SoloPy as solo

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
		client_socket.sendall(f"Updated thermocouple_timestep = {str(timestep_thermocouple)}".encode('utf-8'))
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
	global thermocouple_recording, thermocouple_file_path,stime, timestep_thermocouple, thermocouple, thermocouple2, exper_file

	try:
		thermocouple_file_path = os.path.join(exper_folder, os.path.basename("thermo_log.txt"))
		file = open(thermocouple_file_path, "w")
		thermocouple_recording = True
		try:
			client_socket.sendall(f"Starting thermocouple log. Timestep = {timestep_thermocouple}".encode('utf-8'))
		except:
			pass
		
		# Time loop
		while thermocouple_recording:
			temp = thermocouple.temperature
			temp2 = thermocouple2.temperature
			t = (time.perf_counter()-stime)
			file.write("Time {:.2f} s Temp1: {:.2f} Temp2: {:.2f}\n".format(t,temp,temp2))
			file.flush()
			time.sleep(timestep_thermocouple)
		print("closed file")
	except Exception as e:
                client_socket.sendall(f"Error in starting log: {str(e)}\n".encode('utf-8'))
	finally:
		file.close()

def start_log_thermocouple():
	''' Log thermocouple temprature data to a txt file '''
	global thermocouple_recording, thermocouple_file_path,stime, timestep_thermocouple, thermocouple, thermocouple2, exper_file

	try:
		thermocouple_file_path = os.path.join(exper_folder, os.path.basename("thermo_log.txt"))
		file = open(thermocouple_file_path, "w")
		thermocouple_recording = True
		print("Starting thermocouple log. Timestep = {}".format(timestep_thermocouple))
		
		# Time loop
		while thermocouple_recording:
			temp = thermocouple.temperature
			temp2 = thermocouple2.temperature
			t = (time.perf_counter()-stime)
			file.write("Time {:.2f} s Temp1: {:.2f} Temp2: {:.2f}\n".format(t,temp,temp2))
			file.flush()
			time.sleep(timestep_thermocouple)
		print("closed file")
	except Exception as e:
                print("Error in starting log: " + e)
	finally:
		file.close()

def stop_log_thermocouple(client_socket):
	''' Stop logging thermocouple data to file '''
	global thermocouple_recording,picam2
	
	if thermocouple_recording == False:
		client_socket.sendall(b"Alread stopped thermo log\n")
		return
	try:
		thermocouple_recording = False
		client_socket.sendall(b"Stopping thermo log")
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
		client_socket.sendall(f"Updated timestep_CAL = {str(timestep_CAL)}".encode('utf-8'))
	except Exception as e:
		client_socket.sendall(f"Error in updating timestep: {str(e)}\n".encode('utf-8'))


def start_log_CAL_client(client_socket):
	''' Log CAL temperature controller ata to a txt file '''
	global CAL_recording, CAL_file_path, stime, timestep_CAL, exper_file

	try:
		CAL_file_path = os.path.join(exper_folder, os.path.basename("CAL_log.txt"))
		file = open(CAL_file_path, "w")
		CAL_recording = True
		try:
			client_socket.sendall(f"Starting CAL log. Timestep = {timestep_CAL}".encode('utf-8'))
		except:
			pass
		
		# Time loop
		while CAL_recording:
			temp_cal, setpoint = get_temp_and_setpoint(sleep_time = 0.05) # Read data
			t = (time.perf_counter()-stime)
			file.write("Time {:.2f} s Temp: {:.2f} Setpoint: {:.2f}\n".format(t,temp_cal,setpoint))
			file.flush()
			time.sleep(timestep_CAL)
		print("closed file")
	except Exception as e:
                client_socket.sendall(f"Error in starting log: {str(e)}\n".encode('utf-8'))
	finally:
		file.close()

def stop_log_CAL(client_socket):
	''' Stop logging CAL data to file '''
	global CAL_recording, picam2
	
	if CAL_recording == False:
		client_socket.sendall(b"Alread stopped CAL log\n")
		return
	try:
		CAL_recording = False
		client_socket.sendall(b"Stopping CAL log")
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
	global motor_recording, motor_file_path, stime, timestep_motor, exper_file

	try:
		motor_file_path = os.path.join(exper_folder, os.path.basename("motor_log.txt"))
		file = open(motor_file_path, "w")
		motor_recording = True
		try:
			client_socket.sendall(f"Starting motor log. Timestep = {timestep_motor}".encode('utf-8'))
		except:
			pass
		
		# Time loop
		while motor_recording:
			# Get the current speed and torque
			actualMotorSpeed, error = mySolo.get_speed_feedback()
			rpm_setpoint, error = mySolo.get_speed_reference()
			#rpm_setpoint = 0.0
			t = (time.perf_counter()-stime)
			# Write to file
			file.write("Time {:.2f} s Shaft speed: {:.2f}, Motor speed: {:.2f}, Ref motor speed: {:.2f}\n".format(t,actualMotorSpeed/gear_ratio, actualMotorSpeed, rpm_setpoint))
			file.flush()
			# Timestep
			time.sleep(timestep_motor)
			
		print("closed file")
	except Exception as e:
                client_socket.sendall(f"Error in starting log: {str(e)}\n".encode('utf-8'))
	finally:
		file.close()

def start_log_motor():
	''' Log motor data to a txt file '''
	global mySolo
	global motor_recording, motor_file_path, stime, timestep_motor, exper_file

	try:
		motor_file_path = os.path.join(exper_folder, os.path.basename("motor_log.txt"))
		file = open(motor_file_path, "w")
		motor_recording = True
		print("Starting motor log. Timestep = {}".format(timestep_motor))
		
		# Time loop
		while motor_recording:
			# Get the current speed and torque
			actualMotorSpeed, error = mySolo.get_speed_feedback()
			rpm_setpoint, error = mySolo.get_speed_reference()
			#rpm_setpoint = 0.0
			t = (time.perf_counter()-stime)
			# Write to file
			file.write("Time {:.2f} s Shaft speed: {:.2f}, Motor speed: {:.2f}, Ref motor speed: {:.2f}\n".format(t,actualMotorSpeed/gear_ratio, actualMotorSpeed, rpm_setpoint))
			file.flush()
			# Timestep
			time.sleep(timestep_motor)
			
		print("closed file")
	except Exception as e:
                print("Error in starting log: " + e)
	finally:
		file.close()

def stop_log_motor(client_socket):
	''' Stop logging motor data to file '''
	global motor_recording
	
	if motor_recording == False:
		client_socket.sendall(b"Alread stopped motor log\n")
		return
	try:
		motor_recording = False
		#client_socket.sendall(b"Stopping motor log")
	except Exception as e:
		client_socket.sendall(f"Error in stopping motor log: {str(e)}\n".encode('utf-8'))

def set_motor_timestep_client(client_socket, dt):
	global timestep_motor
	try:
		#index = data.find(" ")
		#new_timestep = data[index+1:]
		timestep_motor = float(dt)
		client_socket.sendall(f"Updated timestep_motor = {str(timestep_motor)}".encode('utf-8'))
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


# ######################################################################
# LOGGING 
# ######################################################################

def start_log_data(client_socket):
	''' Start logging of data to file. Thermometer, CAL, motor '''
	
	# Log data from components in separate threads
	# 1. Thermocouple
	# 2. Motor
	# 3. CAL
	
	# Sequence of commands
	set_thermocouple_timestep_client(client_socket, 0.1)
	set_motor_timestep_client(client_socket, 0.1)
	set_CAL_timestep_client(client_socket, 0.1)

	
	# Run data logs in separate theads
	t1 = threading.Thread(
		target=start_log_thermocouple_client,
		args=(client_socket,),
		daemon=True
	)
	
	t2 = threading.Thread(
		target=start_log_CAL_client,
		args=(client_socket,),
		daemon=True
	)
	
	t3 = threading.Thread(
		target=start_log_motor_client,
		args=(client_socket,),
		daemon=True
	)
	
	# Start the threads
	t1.start()
	t2.start()
	t3.start()
	
	
	return 

def stop_log_data(client_socket):
	''' Stop logging data '''
	
	# Run commands in separate threads
	t1 = threading.Thread(
		target=stop_log_thermocouple,
		args=(client_socket,),
		daemon=True
	)
	
	t2 = threading.Thread(
		target=stop_log_CAL,
		args=(client_socket,),
		daemon=True
	)
	
	t3 = threading.Thread(
		target=stop_log_motor,
		args=(client_socket,),
		daemon=True
	)
	
	# Start the threads
	t1.start()
	t2.start()
	t3.start()
	
	return

# ######################################################################		
# Melt Experiments
# ######################################################################


# Melting experiment commands
def start_melt(client_socket, label, rpm_set, temp_setpoint):
	'''
	Start Melt Experiment
	- Creates folder for storing videos and data logs
	- Starts video recording, turns on lights, sets setpoint temperature
	- Starts timeloop to read and log tempertures, motor speeds
	'''
	global melt_running
	global exper_folder, thermocouple_recording, motor_recording
	global mySolo 
	
	melt_running = True
	print_rotation = True
	
	# Create the experiment folder
	try:
		exper_folder = create_folder(client_socket, "Melt", label, rpm_set, temp_setpoint) 
	except:
		print("Error creating folder")
	
	# Start camera recording
	try:
		start_recording(client_socket)
	except:
		print("Error starting camera")
	
	# Turn on lights
	light_set_color([250,250,250])
	
	# Set the cal controller setpoint
	set_setpoint(temp_setpoint)
	
	# Set up the data log
	data_file_path = os.path.join(exper_folder, os.path.basename("melt_data.csv"))
	file = open(data_file_path, "w")
	file.write("Time, Temp, Temp_CAL, Temp_setpoint, RPM, RPM_setpoint\n") #write the header
	client_socket.sendall(b"Starting log:") # Print to terminal
	thermocouple_recording = True
	timestep_thermocouple = 1.
	timestep_motor = 1.
	timestep_CAL = 1.
	
	# Set up motor
	# Make sure to run these before starting melt experiemnt
	#instantiate_solo_client(client_socket)
	#reset_solo_settings_client(client_socket)
	set_target_load_speed_client(client_socket, rpm_set) # Set the load speed. Starts motor running.
	motor_recording = True
	
	
	# Main time loop
	# TODO: See if can create seperate parallel loops in different functions
	try:
		# Initialize loop
		LOOP_TIME = .15
		stime =time.perf_counter() # Start time
		#t_prev =  (time.perf_counter()-stime)
		
		while melt_running:
			# Get current time
			t = (time.perf_counter()-stime)
			
			# Read thermocouple temperature
			temp = thermocouple.temperature
			# Read CAL controller temperature and setpoint
			temp_cal, setpoint = get_temp_and_setpoint(sleep_time = 0.05)
			
			# Get the current speed and torque
			actualMotorSpeed, error = mySolo.get_speed_feedback() # Will take some time to read
			motorTargetSpeed, error = mySolo.get_speed_reference() # Get the current speed reference
			rpm = actualMotorSpeed
			if print_rotation:
				print(f"Motor RPM: {actualMotorSpeed}")
			

			# Write data to log file
			file.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.4f}\n".format(t,temp,temp_cal,setpoint, actualMotorSpeed, motorTargetSpeed))
			file.flush()
			
			# Sleep
			t_1 = (time.perf_counter()-stime) #get current time again
			time.sleep(1-t_1 % 1) # sleep until time top of next second 
			#time.sleep(1) # Sleep 1 sec
			
		# End time loop
		set_target_load_speed_client(client_socket, 0) # Set the load speed. Starts motor running.
		while True:
			# Wait untill motor has stopped.

			# Get current time
			t = (time.perf_counter()-stime)
			
			# Read thermocouple temperature
			temp = thermocouple.temperature
			# Read CAL controller temperature and setpoint
			temp_cal, setpoint = get_temp_and_setpoint(sleep_time = 0.05)
			
			# Get the current speed and torque
			actualMotorSpeed, error = mySolo.get_speed_feedback() # Will take some time to read
			motorTargetSpeed, error = mySolo.get_speed_reference() # Get the current speed reference
			rpm = actualMotorSpeed
			if print_rotation:
				print(f"Motor RPM: {actualMotorSpeed}")
			

			# Write data to log file
			file.write("{:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.4f}, {:.4f}\n".format(t,temp,temp_cal,setpoint, actualMotorSpeed, motorTargetSpeed))
			file.flush()
			
			# Sleep
			t_1 = (time.perf_counter()-stime) #get current time again
			time.sleep(1-t_1 % 1) # sleep until time top of next second 
			#time.sleep(1) # Sleep 1 sec
			
			if abs(actualMotorSpeed) <= 1.0:
				# Achieved target speed. End loop
				print("Motor stopped")
				break
		
		
	except Exception as e:
                client_socket.sendall(f"Error in starting log: {str(e)}\n".encode('utf-8'))
	finally:
		file.close()
		print("closed file")
		
		
def stop_melt_client(client_socket):
	global melt_running, thermocouple_is_running, camera_is_running, light_is_running, CAL_is_running, camera_is_recording
	try:
		
		#stop_camera()
		#stop_motors()
		#TODO: Review ordering of turning lights and camera off.
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
		CAL_is_running = False	
		#print("DEBUG: stop_melt_client: end of stop_melt_client")
		#print("DEBUG: melt_running, light_is_running, thermocouple_is_running, CAL_is_running")
		#print(melt_running)
	except Exception as e:
		client_socket.sendall(f"Error in stopping melt: {str(e)}\n".encode('utf-8'))
		
def stop_melt():
	global melt_running, thermocouple_is_running,camera_is_running, light_is_running, CAL_is_running
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
		CAL_is_running = False	
	except Exception as e:
		pass
		#client_socket.sendall(f"Error in stopping melt: {str(e)}\n".encode('utf-8'))


#casting experiment

def start_cast(client_socket, label, rpm_set, temp_setpoint):
	global melt_running
	global exper_folder, thermocouple_recording, motor_recording, curr_pos, rpm_setpoint, pwm_range, melt_running, experiment_rpm_setpoint
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
	motor_recording = True
	timestep_thermocouple = 1.
	timestep_melt = 1.
	timestep_motor = 1.
	timestep_CAL = 1.
	
	
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
	global exper_folder, thermocouple_recording, motor_recording, curr_pos, rpm_setpoint, pwm_range, melt_running, experiment_rpm_setpoint
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
	motor_recording = True
	timestep_thermocouple = 1.
	timestep_motor = 1.
	timestep_CAL = 1.
	
	
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
				
			# Logging commands
			elif data == "start_log_data":
				start_log_data(client_socket)
				break
			elif data == "stop_log_data":
				stop_log_data(client_socket)
				break
			
			
			# Exit commands
			#TODO: add other shutdown items here
			elif data == "exit":
				
				shutdown(client_socket)
				client_socket.sendall(b"Exiting Server.\n")
				
				break
			
			# Start melt commend
			elif data.startswith("start melt"):
				data_list = data[11:].split(",")
				start_melt(client_socket, str.strip(data_list[0]),float(data_list[1]), float(data_list[2]))
				#client_socket.sendall(b"starting melt.\n") #FIXME: something wrong with this printout
				break
			elif data == "stop melt":
				client_socket.sendall(b"Stopping Melt.\n")
				stop_melt_client(client_socket)
				
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
				
			# Start casting
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
