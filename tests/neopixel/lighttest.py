import board
import neopixel
import time
import busio
import digitalio
import sys

# Setup pixels
pixel_pin = board.D18
ORDER = neopixel.GRBW # Chagne to match LED's color order
num_pixels = 24
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.05, auto_write=False, pixel_order=ORDER)

# Turn lights on
pixels.fill((0,0,0, 255))
pixels.show()
time.sleep(5)

# Turn lights off
pixels.fill((0,0,0, 0))
pixels.show()
