from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from libcamera import controls

import time
import pdb

#action = 'record'
action = 'preview'


# Create camera instance
camera = Picamera2()
camera.rotation = 90 # rotate camera

print("Available camera sensor modes:")
for mode in camera.sensor_modes:
	print(f"Mode: {mode}")
# Get modes
#Mode 0: {'format': SRGGB10_CSI2P, 'unpacked': 'SRGGB10', 'bit_depth': 10, 'size': (1536, 864), 'fps': 120.13, 'crop_limits': (768, 432, 3072, 1728), 'exposure_limits': (9, None)}
#Mode 1: {'format': SRGGB10_CSI2P, 'unpacked': 'SRGGB10', 'bit_depth': 10, 'size': (2304, 1296), 'fps': 56.03, 'crop_limits': (0, 0, 4608, 2592), 'exposure_limits': (13, 77208384, None)}
#Mode 2: {'format': SRGGB10_CSI2P, 'unpacked': 'SRGGB10', 'bit_depth': 10, 'size': (4608, 2592), 'fps': 14.35, 'crop_limits': (0, 0, 4608, 2592), 'exposure_limits': (26, 112015443, None)}


# Configure camera
camera_config = camera.create_preview_configuration()
#video_config = camera.create_video_configuration(main={'size':(1920,1080)}) # Works
#video_config = camera.create_video_configuration(main={'size':(1920,1080)} ) # Max FOV???

#video_config = camera.create_video_configuration(raw={"size":(2304,1296)},main={'size':(1920,1080)})
#video_config = camera.create_video_configuration(raw={"size":(4608, 2592)},main={'size':(1920,1080)})
#video_config = camera.create_video_configuration(main={'size':(4608, 2592)}) # Full res, unsufficient buffer
#camera.configure(video_config)



# New method
full_mode = next(
	m for m in camera.sensor_modes
	if m["size"] == (4608, 2592)
)



# Old method
mode = camera.sensor_modes[2] # (4608, 2592) wide field
video_config = camera.create_video_configuration(
	#raw = {"format": mode['format'], "size":mode['size']},
	#main = { "size":mode['size']},
	main={'size':(1920,1080)}, # (4608, 2592)
	lores={"size":(640,360)},
	display="lores",
	buffer_count=2,
	raw=mode, 
)
camera.configure(video_config)

if action.lower() == 'preview':
	camera.start_preview(Preview.QTGL)

encoder = H264Encoder(10000000) # Max support is 1920x1080
# Start preview
# video_output = FfmpegOutput("video.mp4")
print("Starting video preview + recording")
camera.start() # Start the camera
camera.start_recording(encoder,'test.h264')

# Check camera controls
print("\nCamera controls")
for key, value in camera.camera_controls.items():
	print(key,value)
	
	
# Manual focus
# Tube Length = 20 cm
# Minimum = 2.857 (LensPosition=30) ~ start of tube
# End of tube: 22.5 cm
focus_distance = 3.0 # Focus distance in cm
print("\nManual focus" )
print(f"Focus distance: {focus_distance} (cm)" )
print(f"LensPosition = 1/focus_dist[m]: {1/(focus_distance/100)}" )
camera.set_controls({"AfMode":controls.AfModeEnum.Manual })
camera.set_controls({"LensPosition":1/(focus_distance/100)})
time.sleep(1)

# Enable continuous autofocus
#camera.set_controls({"AfMode":controls.AfModeEnum.Continuous })
count = 0
while count<30:
	md = camera.capture_metadata()
	print('AfState:', md['AfState'])
	print('LensPosition: ', md['LensPosition'])
	print(f"FocusDistance: {(1/md['LensPosition'])*100} [cm]")
	time.sleep(1)
	count += 1



# Print focus settings
print("\nCamera metadata t=0")
metadata = camera.capture_metadata()
for k,v in metadata.items():
	print(k,v)
# ~ for key in metadata:
	# ~ if "Af" in key or "Lens" in key:
		# ~ print(key, metadata[key])

time.sleep(10)
print("\nCamera metadata t=10s")
metadata = camera.capture_metadata()
for k,v in metadata.items():
	print(k,v)


# Metadata settings
# AfState: 0:Idle, 1:Scanning, 2:Focused, 3:Fail # Current setting 0:Idle



time.sleep(30)
camera.stop_recording()
print("Finished recording")
camera.stop()
