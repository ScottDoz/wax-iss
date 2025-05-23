import adafruit_max31865
import time
import board
import busio
import digitalio



#settings
spi=busio.SPI(board.SCLK,board.MOSI,board.MISO)

# Thermocouple 1 (GPIO 5)
#allocate cs pin and set direction
cs = digitalio.DigitalInOut(board.D5) # board.D5
cs.direction = digitalio.Direction.OUTPUT
#create thermocouple object
thermocouple = adafruit_max31865.MAX31865(spi,cs)
#thermocouple = adafruit_max31865.MAX31865(spi,cs,wires=2,rtd_nominal=100.0, ref_resistor=100.0)
#thermocouple = adafruit_max31865.MAX31865(spi,cs,wires=2,rtd_nominal=100.0, ref_resistor=430.0)

# Thermocouple 2 (GPIO 6)
#allocate cs pin and set direction
cs2 = digitalio.DigitalInOut(board.D6) # board.D5
cs2.direction = digitalio.Direction.OUTPUT
#create thermocouple object
thermocouple2 = adafruit_max31865.MAX31865(spi,cs2)


# Change thermocouple type
#thermocouple._set_thermocouple_type(adafruit_max31856.ThermocoupleType.T)
'''
    - ``ThermocoupleType.B``
    - ``ThermocoupleType.E``
    - ``ThermocoupleType.J``
    - ``ThermocoupleType.K``
    - ``ThermocoupleType.N``
    - ``ThermocoupleType.R``
    - ``ThermocoupleType.S``
    - ``ThermocoupleType.T``
'''


stime=time.perf_counter()

while True:
	# Read thermocouple 1
	temp=thermocouple.temperature
	res=thermocouple.resistance
	# Read thermocouple 2
	temp2=thermocouple2.temperature
	res2=thermocouple2.resistance
	#print(temp)
	t=(time.perf_counter()-stime)
	print("Time: {:.2f} s | Temp1: {:.2f} Res1 {:.2f} | Temp2: {:.2f} Res2: {:.2f}".format(t,temp,res,temp2,res2))
	time.sleep(0.1)

