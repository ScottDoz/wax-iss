import pigpio

def check_pin(pin):
	
	pi = pigpio.pi()
	pi.set_mode(pin, pigpio.OUTPUT)
	pi.write(pin,1)
	print("GPIO " + str(pin) + " high:", pi.read(pin))
	pi.write(pin,0)
	print("GPIO " + str(pin) + " low:", pi.read(pin))
	
	return


print("\nRTD Sensors (cylinder): GPIO 5")
check_pin(5)

print("\nRTD Sensors (box wall): GPIO 6")
check_pin(6)

print("\nLED: GPIO 18")
check_pin(18)




