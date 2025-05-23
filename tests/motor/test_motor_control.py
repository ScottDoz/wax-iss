import time
import pigpio
import rotary_encoder
import matplotlib.pyplot as plt

import numpy as np


# Target rpm
global setpoint
targetrpm = 400 # Target rpm
run_time = 20.  # Total run time
ramp_time = 10. # Ramp up time


#Pins for Motor Driver Inputs
Motor1A = 23 # header 18, wpi 5
Motor1B = 24 # header 16, wpi 4
Motor1E = 12 # header 33, wpi 23
#encA, encB = 26, 16 # these are BCM pins, headers 13 and 15, wPi 2 and 3
encA, encB = 26, 25  # Flight

last_pos, curr_pos = 0, 0
start = 0
LOOP_TIME = .15
G = 6.3
CPR = 16
pwm_range = 500 # 500
prev = 0
ed, ei = 0, 0

# kp, ki, kd = 0.4, 0.1, 0
kp, ki, kd = 0.4, 0.05, 0




setpoint = 0 # intialize to zero

times = []
rpms = []
angles = []
duties = []


def callback(way):
    global curr_pos
    curr_pos += way

def calc_new(prev, rpm):
    global ed, ei
    global setpoint
    e = setpoint - rpm
    outp = prev + e*kp
    outpd = prev + e*kp + ed*kd
    outpid = prev + e*kp + ed*kd + ei*ki
    #print(int(outp), int(outpd), int(outpid))
    ed = e
    ei += e
    return max(min(pwm_range, outpid), 0)    

def setup():
    global pi
    pi = pigpio.pi()
    
    pi.set_PWM_frequency(Motor1E, 19200)
    pi.set_PWM_range(Motor1E, pwm_range)

    decoder = rotary_encoder.decoder(pi, encA, encB, callback) 
    
    
def loop():
    global start, last_pos, decoder, prev, times, rpms, angles, duties

    # reading the encoder data and measuring RPM
    dt, dpos = time.time() - start, curr_pos - last_pos
    if dt > LOOP_TIME:
        
        start, last_pos = time.time(), curr_pos
        rpm = (dpos*60)/(G*CPR*dt)
        times.append(start), rpms.append(rpm), angles.append(curr_pos)
        print("\nrpm = {}".format(rpm))
        time.sleep(.001)
        new = calc_new(prev, rpm)
        duties.append(new)
        print("new duty cycle = {}".format(new))

        pi.set_PWM_dutycycle(Motor1E, new)
        prev = new
    
    pi.write(Motor1A, 0)
    pi.write(Motor1B, 1)
    

    time.sleep(.15)
    
def stop():
    pi.write(Motor1E, 0)

def destroy():
    pi.stop()
    
if __name__=='__main__': # Program start from here
    setup()
    start_time = time.time()
    try:
        while time.time()-start_time<run_time:
            t = time.time()-start_time # Current time
            if t<ramp_time:
                # Linear ramp up
                setpoint = (targetrpm/ramp_time)*t
            else:
                setpoint = targetrpm
            
            loop()
        stop()
        destroy()
        plt.plot([start_time, time.time()], [setpoint, setpoint])
        plt.plot(times, rpms)
        #plt.plot(times, angles)
        #plt.plot(np.array(angles) % (2*np.pi), np.array(duties), '.k')
        plt.show()
    except KeyboardInterrupt:
        destroy()
    
