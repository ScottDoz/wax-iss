from camera_module import *

#initialize camera object

#picam2 = Picamera2()
#encoder = H264Encoder(bitrate=1000000)  # Assume encoder is initialized elsewhere
#output_file = "Video/output_video.h264"
#is_recording = False
#is_running = True  # Add this global flag to control the server loop
#rotation = False



if __name__ == "__main__":
	picam2 = Picamera2()
	encoder = H264Encoder(bitrate=1000000)
	output_file = "Video/output_video.h264"
	is_recording = False
	is_running = True
	rotation = False
	server_program(picam2, encoder, output_file, is_running, is_recording, rotation)
