from picamera2 import Picamera2, Preview
import time
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

# Create camera instance
camera = Picamera2()
camera.rotation = 90 # rotate camera

for mode in camera.sensor_modes:
	print(f"Mode: {mode}")

# Configure camera
camera_config = camera.create_preview_configuration()
video_config = camera.create_video_configuration(main={'size':(1920,1080)}) # Works
#video_config = camera.create_video_configuration(raw={"size":(2304,1296)},main={'size':(1920,1080)})
#video_config = camera.create_video_configuration(raw={"size":(4608, 2592)},main={'size':(1920,1080)})
#video_config = camera.create_video_configuration(main={'size':(4608, 2592)}) # Full res, unsufficient buffer
camera.configure(video_config)

# Get modes
#Mode 0: {'format': SRGGB10_CSI2P, 'unpacked': 'SRGGB10', 'bit_depth': 10, 'size': (1536, 864), 'fps': 120.13, 'crop_limits': (768, 432, 3072, 1728), 'exposure_limits': (9, None)}
#Mode 1: {'format': SRGGB10_CSI2P, 'unpacked': 'SRGGB10', 'bit_depth': 10, 'size': (2304, 1296), 'fps': 56.03, 'crop_limits': (0, 0, 4608, 2592), 'exposure_limits': (13, 77208384, None)}
#Mode 2: {'format': SRGGB10_CSI2P, 'unpacked': 'SRGGB10', 'bit_depth': 10, 'size': (4608, 2592), 'fps': 14.35, 'crop_limits': (0, 0, 4608, 2592), 'exposure_limits': (26, 112015443, None)}
#mode = camera.sensor_modes[1]
#video_config = camera.create_video_configuration(
#	raw = {"format": mode['format'], "size":mode['size']},
#	main = {"format": "RGB888", "size":mode['size']},
#)
#camera.configure(video_config)


try:
	camera.start_preview(Preview.QTGL)
except:
	print("Resolution too high for preview video")


encoder = H264Encoder(10000000) # Max support is 1920x1080

# Start preview
# video_output = FfmpegOutput("video.mp4")
print("Starting video preview + recording")
camera.start() # Start the camera
camera.start_recording(encoder,'test.h264')
time.sleep(10)
camera.stop_recording()
print("Finished recording")
camera.stop()
