# Title: SoloPy
# Motor Test ST-curve
# ----------

# Test control of the motor using SOLO mini via usb communication
# Code adapted from example code in SoloPy/examples/raspberry_pi/usb


import SoloPy as solo
import time
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdb

# ######################################################################
#                          Inputs
# ######################################################################

#mode = 'st_time-based'
mode = 'st_time_optimal'

# Note: time-based curve is much smoother


# Test speed
target_speed_shaft = 200. #200. # Load speed (RPM)


# Time optimal ST-curve parameters
stCurve_maxAccel = 5 # Max accelleration (rev/s/s ???) (RPM/s)
stCurve_maxJerk = 0.5 # Maximum Jerk (rev/s/s/s???) (RPM/s/s)
# *** values look like they are in rev/s/s and rev/s/s/s

# Time-based ST-curve parameters
stCurve_T13 = 3 # Time of Segments 1 and 3 (take-off/landing segment) (s)
stCurve_T2 = 0  # Time of segement 2 (max accel segment) (s)

# Motor Step Response settings
speedAccelValue = 5.0/3. # Speed acceleration value (rev/s/s) 5 == 300 rpm/s
speedDecelValue = 5.0/3. # Speed deceleration value (rev/s/s) 5 == 300 rpm/s
speedLimit = 700*24 # Speed limit (rpm)


# Motor Settings
pwmFrequency = 80 # Desired Switching or PWM Frequency at Output
numberOfPoles = 4 # Motor's Number of Poles
currentLimit = 3.5 # Current Limit of the Motor
numberOfEncoderLines = 1024 # Motor's Number of Encoder Lines (PPR pre-quad)
speedControllerKp = 0.2219924 # Speed controller Kp
speedControllerKi = 0.0070648 # Speed controller Ki
busVoltage = 0 # Battery or Bus Voltage
actualMotorTorque = 0 # Motor Torque feedback
actualMotorSpeed = 0 # Motor speed feedback
actualMotorPosition = 0 # Motor position feedback

# Motor parameters
gear_ratio = 23.76 # Gear ratio
kt = 5.9e-3 # Motor torque constant (N.m/A) 5.9 mN.m/A = 5.9e-3 N.m/A for Faulhaber 2264 BP4


# ######################################################################
#                   Connect to Motor
# ######################################################################

# Instanciate a SOLO object:
# check with SOLO motion terminal that you are able to connect to your device 
# and make sure the port name in the code is the correct one 
mySolo = solo.SoloMotorControllerUart("/dev/ttyACM0", 0, solo.UartBaudRate.RATE_937500)


# wait here till communication is established
print("Trying to Connect To SOLO")
communication_is_working = False
while communication_is_working is False:
    time.sleep(1)
    communication_is_working, error = mySolo.communication_is_working()
print("Communication Established succuessfully!")

# Initial Configuration of the device and the Motor
# Fixed settings
mySolo.set_motor_type(solo.MotorType.BLDC_PMSM)
mySolo.set_motor_poles_counts(numberOfPoles)
mySolo.set_incremental_encoder_lines(numberOfEncoderLines)
# Control mode
mySolo.set_feedback_control_mode(solo.FeedbackControlMode.ENCODERS)
mySolo.set_control_mode(solo.ControlMode.SPEED_MODE)
mySolo.set_command_mode(solo.CommandMode.DIGITAL)
# Variable settings
mySolo.set_output_pwm_frequency_khz(pwmFrequency)
mySolo.set_current_limit(currentLimit)
mySolo.set_speed_controller_kp(speedControllerKp)
mySolo.set_speed_controller_ki(speedControllerKi)
mySolo.set_speed_acceleration_value(speedAccelValue)
mySolo.set_speed_deceleration_value(speedDecelValue)
mySolo.set_speed_limit(speedLimit)


# ST-Curve settings

if mode == 'st_time-based':
    # Use Motion profile 2
    mySolo.set_motion_profile_mode(1)
    mySolo.set_motion_profile_variable1(stCurve_T13)
    mySolo.set_motion_profile_variable2(stCurve_T2)

elif mode == 'st_time_optimal':
    # Use Motion profile 3
    mySolo.set_motion_profile_mode(2)
    mySolo.set_motion_profile_variable1(stCurve_maxAccel)
    mySolo.set_motion_profile_variable2(stCurve_maxJerk)

    


# run the motor identification to Auto-tune the current controller gains Kp and Ki 
# needed for Torque Loop run ID. always after selecting the Motor Type!
# ID. doesn't need to be called everytime, only one time after wiring up the Motor will be enough
# the ID. values will be remembered by SOLO after power recycling
mySolo.motor_parameters_identification(solo.Action.START)
print("Identifying the Motor")
# wait at least for 2sec till ID. is done
time.sleep(2)

# Calibration
mySolo.sensor_calibration(solo.PositionSensorCalibrationAction.INCREMENTAL_ENCODER_START_CALIBRATION)
#print(input_valid,error) 
time.sleep(10)
mySolo.sensor_calibration(solo.PositionSensorCalibrationAction.STOP_CALIBRATION)
mySolo.set_control_mode(solo.ControlMode.SPEED_MODE)
print("ended calibration")

# Setings
print("Motor settings")
print("Output PWM Frequency (khz)", mySolo.get_output_pwm_frequency_khz())
print("Current limit (A)", mySolo.get_current_limit())
print("Motor poles count", mySolo.get_motor_poles_counts())
print("Incremental encoder lines", mySolo.get_incremental_encoder_lines())
print("Speed controller kp", mySolo.get_speed_controller_kp())
print("Speed controller ki", mySolo.get_speed_controller_ki())
print("Speed acceleration value", mySolo.get_speed_acceleration_value()) # Rev/s/s
print("Speed deceleration value", mySolo.get_speed_deceleration_value())
print("encoder_hall_ccw_offset", mySolo.get_encoder_hall_ccw_offset())
print("encoder_hall_cw_offset", mySolo.get_encoder_hall_cw_offset())
print("Board temperature (C)", mySolo.get_board_temperature())
print("Motor resistance (Ohm)", mySolo.get_motor_resistance())
print("Motor inductance (H)", mySolo.get_motor_inductance())
print("Speed limit", mySolo.get_speed_limit())
print("Communication is working", mySolo.communication_is_working())
print("Motion profile mode", mySolo.get_motion_profile_mode())
print("Motion profile variable 1", mySolo.get_motion_profile_variable1())
print("Motion profile variable 2", mySolo.get_motion_profile_variable2())


# ######################################################################
#                          Ramp Up/Down
# ######################################################################

    
print("-------------------\n\n\n")
print("Begin Speed Test")

# Time loop
t0 = time.time() # Start time
change_rotation_rate_flag = True


# Target speed
target_speed_motor = target_speed_shaft*gear_ratio # Motor speed

# Create log file
motor_filename = 'motor_log.csv'
with open(motor_filename, mode='w', newline="") as file:
			 
    # Create csv writer and write header
    writer = csv.writer(file, delimiter=',')
    writer.writerow(["time_s","load_speed","motor_speed","ref_motor_speed","iq","motor_torque","load_torque"])
    
    
    # RAMP UP ----------------------------------------------------------
    
    while True:
        # Get time
        t = time.time() - t0 # Loop time
        
        # Ramp up to speed
        if change_rotation_rate_flag == True:
            # First instance. Set target speed
            print("Ramping up RPM")
            #mySolo.set_motor_direction(solo.Direction.CLOCKWISE)        # Clockwise
            mySolo.set_motor_direction(solo.Direction.COUNTERCLOCKWISE) # Counter clockwise
            mySolo.set_speed_reference(target_speed_motor) #this is motor speed not shaft speed
            change_rotation_rate_flag = False
            
        # Get the current speed and torque
        motor_speed, error = mySolo.get_speed_feedback()
        motor_Iq, error = mySolo.get_quadrature_current_iq_feedback()
        
        # Computations
        load_speed = motor_speed/gear_ratio # Load speed (RPM)
        motor_torque = motor_Iq*kt # Motor torque (N.m)
        load_torque = motor_torque*gear_ratio # Load torque (N.m)
        
        print(f"time: {t:.2f} s. Motor Speed: {motor_speed} RPM. Shaft Speed: {motor_speed/gear_ratio:.2f} RPM. Measured Iq {motor_Iq:.2f} [A]")
        
        # Write to file          
        writer.writerow([round(t,3), round(load_speed,3), round(motor_speed,3), round(target_speed_motor,3), round(motor_Iq,6), round(motor_torque,6), round(load_torque,6)])
        file.flush()
        
        time.sleep(0.1)
        
        
        if abs(motor_speed - target_speed_motor) <= 1.0:
            # Achieved target speed. End loop
            print("Achieved target speed")
            break

        if t>60:
            # End loop
            print('Timeout')
            break

    # Ramp down --------------------------------------------------------
    time.sleep(2) # Wait 5 seconds to establish speed

    print("Ramping down to 0")
    #mySolo.set_motor_direction(solo.Direction.CLOCKWISE)
    mySolo.set_motor_direction(solo.Direction.COUNTERCLOCKWISE)
    mySolo.set_speed_reference(0)

    while True:
        # Get time
        t = time.time() - t0 # Loop time

        # Get the current speed and torque
        motor_speed, error = mySolo.get_speed_feedback()
        motor_Iq, error = mySolo.get_quadrature_current_iq_feedback()
        
        # Computations
        load_speed = motor_speed/gear_ratio # Load speed (RPM)
        motor_torque = motor_Iq*kt # Motor torque (N.m)
        load_torque = motor_torque*gear_ratio # Load torque (N.m)
        
        print(f"time: {t:.2f} s. Motor Speed: {motor_speed} RPM. Shaft Speed: {motor_speed/gear_ratio:.2f} RPM. Measured Iq {motor_Iq:.2f} [A]")
        
        # Write to file        
        writer.writerow([round(t,3), round(load_speed,3), round(motor_speed,3), round(target_speed_motor,3), round(motor_Iq,6), round(motor_torque,6), round(load_torque,6)])
        file.flush()
        
        time.sleep(0.1)
        
        # ~ error_code = mySolo.GetErrorRegister()
        # ~ if error_code !=0:
            # ~ print(f"Error detected! Decimal Code: {error_code}")
        
        if abs(motor_speed) <= 1.0:
            # Achieved target speed. End loop
            print("Motor stopped")
            break
        
        if t>120:
            # End loop
            print('Timeout')
            break

    time.sleep(5)

actualMotorSpeed, error = mySolo.get_speed_feedback()
actualMotorIq, error = mySolo.get_quadrature_current_iq_feedback()
print(f"time: {t:.2f} s. Motor Speed: {actualMotorSpeed} RPM. Shaft Speed: {actualMotorSpeed/gear_ratio:.2f} RPM. Measured Iq {actualMotorIq:.2f} [A]")
print("End of test")
print("Motion profile mode", mySolo.get_motion_profile_mode())
print("Motion profile variable 1", mySolo.get_motion_profile_variable1())
print("Motion profile variable 2", mySolo.get_motion_profile_variable2())

# Close connection
print("Closing solo connection")
mySolo.serial_close()


# ######################################################################
#                          Plot Data
# ######################################################################


# Read data
# time_s,load_speed,motor_speed,ref_motor_speed,iq,motor_torque,load_torque
dfm = pd.read_csv(motor_filename) # Motor data

# Compute acceleration and jerk
dfm['load_accel'] = np.gradient(dfm.load_speed, dfm.time_s) # Load accel (RPM/s)
dfm['load_jerk'] = np.gradient(dfm.load_accel, dfm.time_s) # Load jerk (RPM/s/s)
dfm['motor_accel'] = np.gradient(dfm.motor_speed, dfm.time_s) # Load accel (RPM/s)
dfm['motor_jerk'] = np.gradient(dfm.motor_accel, dfm.time_s) # Load jerk (RPM/s/s)

# Plot
fig, axs = plt.subplots(nrows=4, ncols=2, figsize=(8,8), sharex=True)
time = dfm.time_s.to_numpy()

# Motor Side -------------------------------------------------
axs[0,0].set_title("Motor Side") 
# Speed
axs[0,0].plot(dfm.time_s, dfm.ref_motor_speed, '--r', label='Ref motor speed')
axs[0,0].plot(dfm.time_s, dfm.motor_speed,'-k', label='Motor speed')
axs[0,0].legend()
axs[0,0].set_ylabel("Speed (RPM)")
#axs[0,0].set_xlabel("Time (s)")

# Acceleration
axs[1,0].plot(dfm.time_s, dfm.motor_accel,'-k', label='Motor accel')
axs[1,0].legend()
axs[1,0].set_ylabel("Accel (RPM/s)")
if mode == 'st_time_optimal':
    axs[1,0].plot([time[0], time[-1]], [stCurve_maxAccel*60, stCurve_maxAccel*60] , '--r', label='Max accel')


# Jerk
axs[2,0].plot(dfm.time_s, dfm.motor_jerk,'-k', label='Motor jerk')
axs[2,0].legend()
axs[2,0].set_ylabel("Jerk (RPM/s/s)")
if mode == 'st_time_optimal':
    axs[2,0].plot([time[0], time[-1]], [stCurve_maxJerk*60, stCurve_maxJerk*60], '--r', label='Max jerk')


# Torque
axs[3,0].plot(dfm.time_s, dfm.motor_torque, '-k', label='Motor torque')
axs[3,0].set_ylabel("Torque (N.m)")
axs[3,0].set_xlabel("Time (s)")

# Load Side -------------------------------------------------
axs[0,1].set_title("Load Side") 

# Speed
axs[0,1].plot(dfm.time_s, dfm.ref_motor_speed/gear_ratio, '--r', label='Ref load speed')
axs[0,1].plot(dfm.time_s, dfm.load_speed,'-k', label='Load speed')
axs[0,1].legend()
axs[0,1].set_ylabel("Speed (RPM)")
#axs[0,1].set_xlabel("Time (s)")

# Acceleration
#axs[1,1].plot([time[0], time[-1]], [stCurve_maxAccel/gear_ratio, stCurve_maxAccel/gear_ratio] , '--r', label='Max accel')
axs[1,1].plot(dfm.time_s, dfm.load_accel,'-k', label='Load accel')
axs[1,1].legend()
axs[1,1].set_ylabel("Accel (RPM/s)")

# Jerk
#axs[2,1].plot([time[0], time[-1]], [stCurve_maxJerk/gear_ratio, stCurve_maxJerk/gear_ratio], '--r', label='Max jerk')
axs[2,1].plot(dfm.time_s, dfm.load_jerk,'-k', label='Load jerk')
axs[2,1].legend()
axs[2,1].set_ylabel("Jerk (RPM/s/s)")

# Torque
axs[3,1].plot(dfm.time_s, dfm.load_torque, '-k', label='Load torque')
axs[3,1].set_ylabel("Torque (N.m)")
axs[3,1].set_xlabel("Time (s)")

plt.show()

