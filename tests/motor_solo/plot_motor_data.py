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
#                          Plot Data
# ######################################################################

# Motor parameters
gear_ratio = 23.76 # Gear ratio
kt = 5.9e-3 # Motor torque constant (N.m/A) 5.9 mN.m/A = 5.9e-3 N.m/A for Faulhaber 2264 BP4


# Read data
# time_s,load_speed,motor_speed,ref_motor_speed,iq,motor_torque,load_torque
dfm = pd.read_csv('motor_log.csv') # Motor data

# Compute acceleration and jerk
dfm['load_accel'] = np.gradient(dfm.load_speed, dfm.time_s) # Load accel (RPM/s)
dfm['load_jerk'] = np.gradient(dfm.load_accel, dfm.time_s) # Load jerk (RPM/s/s)

dfm['motor_accel'] = np.gradient(dfm.motor_speed, dfm.time_s) # Load accel (RPM/s)
dfm['motor_jerk'] = np.gradient(dfm.motor_accel, dfm.time_s) # Load jerk (RPM/s/s)

# Plot
fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(8,8), sharex=True)
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
#axs[1,0].plot([time[0], time[-1]], [stCurve_maxAccel, stCurve_maxAccel] , '--r', label='Max accel')
axs[1,0].plot(dfm.time_s, dfm.motor_accel,'-k', label='Motor accel')
axs[1,0].legend()
axs[1,0].set_ylabel("Accel (RPM/s)")

# Acceleration
#axs[2,0].plot([time[0], time[-1]], [stCurve_maxJerk, stCurve_maxJerk], '--r', label='Max jerk')
axs[2,0].plot(dfm.time_s, dfm.motor_jerk,'-k', label='Motor jerk')
axs[2,0].legend()
axs[2,0].set_ylabel("Jerk (RPM/s/s)")

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

# Acceleration
#axs[2,1].plot([time[0], time[-1]], [stCurve_maxJerk/gear_ratio, stCurve_maxJerk/gear_ratio], '--r', label='Max jerk')
axs[2,1].plot(dfm.time_s, dfm.load_jerk,'-k', label='Load jerk')
axs[2,1].legend()
axs[2,1].set_ylabel("Jerk (RPM/s/s)")


# Motor torque
#axs[1].plot(dfm.time_s, dfm.load_torque, '-k', label='Load torque')
#axs[1].set_ylabel("Load Torque (N.m)")
#axs[1].set_xlabel("Time (s)")

plt.show()

