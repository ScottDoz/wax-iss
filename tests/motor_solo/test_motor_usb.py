# Title: SoloPy
# Motor Test
# ----------

# Test control of the motor using SOLO mini via usb communication
# Code adapted from example code in SoloPy/examples/raspberry_pi/usb


import SoloPy as solo

import time

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

# Motor Settings
pwmFrequency = 80 # Desired Switching or PWM Frequency at Output
numberOfPoles = 4 # Motor's Number of Poles
currentLimit = 3.5 # Current Limit of the Motor
numberOfEncoderLines = 1024 # Motor's Number of Encoder Lines (PPR pre-quad)
speedControllerKp = 0.2219924 # Speed controller Kp
speedControllerKi = 0.0070648 # Speed controller Ki
speedAccelValue = 5.0 # Speed acceleration value (rev/s/s)
speedDecelValue = 5.0 # Speed deceleration value (rev/s/s)
speedLimit = 700*24 # Speed limit (rpm)
busVoltage = 0 # Battery or Bus Voltage
actualMotorTorque = 0 # Motor Torque feedback
actualMotorSpeed = 0 # Motor speed feedback
actualMotorPosition = 0 # Motor position feedback


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


# run the motor identification to Auto-tune the current controller gains Kp and Ki needed for Torque Loop
# run ID. always after selecting the Motor Type!
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


#print("Begin Speed Test")
# ~ # loop actions
# ~ while True:
    # ~ # set the Direction on C.W.
    # ~ mySolo.set_motor_direction(solo.Direction.CLOCKWISE)
    # ~ # set an arbitrary Positive speed reference[RPM]
    # ~ mySolo.set_speed_reference(24*100)
    # ~ time.sleep(10)
    # ~ actualMotorSpeed, error = mySolo.get_speed_feedback()
    # ~ print("Motor Speed: " + str(actualMotorSpeed))
    # ~ actualMotorTorque, error = mySolo.get_quadrature_current_iq_feedback()
    # ~ print("Measured Iq/Torque[A]: " + str(actualMotorTorque))
    # ~ time.sleep(3)

    # ~ # set the Direction on C.C.W.
    # ~ mySolo.set_motor_direction(solo.Direction.COUNTERCLOCKWISE)
    # ~ # set an arbitrary Positive speed reference[RPM]
    # ~ mySolo.set_speed_reference(24*200)
    # ~ time.sleep(10)
    # ~ actualMotorSpeed, error = mySolo.get_speed_feedback()
    # ~ print("Motor Speed: " + str(actualMotorSpeed))
    # ~ actualMotorTorque, error = mySolo.get_quadrature_current_iq_feedback()
    # ~ print("Measured Iq/Torque[A]: " + str(actualMotorTorque))
    # ~ time.sleep(3)
    
    
print("-------------------\n\n\n")
print("Begin Speed Test")

# Time loop
t0 = time.time() # Start time
change_rotation_rate_flag = True


# Target speed
gear_ratio = 23.76 # Gear ratio
target_speed_shaft = 200. # Load speed
target_speed_motor = target_speed_shaft*gear_ratio # Motor speed

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
    actualMotorSpeed, error = mySolo.get_speed_feedback()
    actualMotorTorque, error = mySolo.get_quadrature_current_iq_feedback()
    print("time: " + str(t) + "s. " + "Motor Speed: " + str(actualMotorSpeed) + " RPM. " + "Measured Iq/Torque[A]: " + str(actualMotorTorque))
    time.sleep(0.1)
    
    if abs(actualMotorSpeed - target_speed_motor) <= 1.0:
        # Achieved target speed. End loop
        print("Achieved target speed")
        break

    if t>20:
        # End loop
        break

# Ramp down
time.sleep(2) # Wait 5 seconds to establish speed

print("Ramping down to 0")
#mySolo.set_motor_direction(solo.Direction.CLOCKWISE)
mySolo.set_motor_direction(solo.Direction.COUNTERCLOCKWISE)
mySolo.set_speed_reference(0)

while True:
    # Get time
    t = time.time() - t0 # Loop time

    # Get the current speed and torque
    actualMotorSpeed, error = mySolo.get_speed_feedback()
    actualMotorTorque, error = mySolo.get_quadrature_current_iq_feedback()
    print("time: " + str(t) + "s. " + "Motor Speed: " + str(actualMotorSpeed) + " RPM. " + "Measured Iq/Torque[A]: " + str(actualMotorTorque))
    time.sleep(0.1)
    
    if abs(actualMotorSpeed) <= 1.0:
        # Achieved target speed. End loop
        print("Motor stopped")
        break

time.sleep(5)

actualMotorSpeed, error = mySolo.get_speed_feedback()
actualMotorTorque, error = mySolo.get_quadrature_current_iq_feedback()
print("time: " + str(t) + "s. " + "Motor Speed: " + str(actualMotorSpeed) + " RPM. " + "Measured Iq/Torque[A]: " + str(actualMotorTorque))
print("End of test")
