import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt


# Base directory
label = "TMI_Tests"
prefix = "Fluid"

session_file_path = "/home/pi/Data/" + label

# Get list of folders starting with prefix (Cast, Melt, Fluid)
list_of_folders = glob.glob(os.path.join(session_file_path, prefix+"*"))

# Get latest file
exper_folder = max(list_of_folders, key=os.path.getctime)
print(exper_folder)


# Get files
motor_file_path = os.path.join(exper_folder, "motor_log.csv")
cal_file_path = os.path.join(exper_folder, "CAL_log.csv")

# Motor parameters
gear_ratio = 23.76 # Gear ratio
kt = 5.9e-3 # Motor torque constant (N.m/A) 5.9 mN.m/A = 5.9e-3 N.m/A for Faulhaber 2264 BP4

# Scaling functions
def motor_to_load(m):
	return m*gear_ratio
	
def load_to_motor(l):
	return l/gear_ratio
	
# Read data
dfm = pd.read_csv(motor_file_path) # Motor data
dfcal = pd.read_csv(cal_file_path) # CAL data

# Compute load-side parameters
dfm['load_speed'] = dfm.motor_speed/gear_ratio # Load speed (RPM)
dfm['motor_torque'] = dfm.motor_iq*kt          # Motor torque (N.m)
dfm['load_torque'] = dfm.motor_torque*gear_ratio # Load torque (N.m)

# Compute acceleration and jerk
dfm['load_accel'] = np.gradient(dfm.load_speed, dfm.time_s) # Load accel (RPM/s)
dfm['load_jerk'] = np.gradient(dfm.load_accel, dfm.time_s) # Load jerk (RPM/s/s)
dfm['motor_accel'] = np.gradient(dfm.motor_speed, dfm.time_s) # Load accel (RPM/s)
dfm['motor_jerk'] = np.gradient(dfm.motor_accel, dfm.time_s) # Load jerk (RPM/s/s)

# Plot
fig, axs = plt.subplots(nrows=5, ncols=1, figsize=(5,8), sharex=True, layout='constrained')

# Motor speed
axs[0].plot(dfm.time_s, dfm.ref_motor_speed/gear_ratio, '--r', label='Ref speed')
axs[0].plot(dfm.time_s, dfm.load_speed,'-k', label='Meas. speed')
axs[0].legend()
axs[0].set_ylabel("Load Speed (RPM)")
ax2 = axs[0].secondary_yaxis('right', functions=(motor_to_load,load_to_motor), color='red')
ax2.set_ylabel("Motor Speed (RPM)", color='red')

#axs[0].set_xlabel("Time (s)")

# Motor Accel
axs[1].plot(dfm.time_s, dfm.load_accel,'-k', label='Load accel')
axs[1].legend()
axs[1].set_ylabel("Load Accel (RPM/s)")
ax2 = axs[1].secondary_yaxis('right', functions=(motor_to_load,load_to_motor), color='red')
ax2.set_ylabel("Motor Accel (RPM/s)", color='red')

# Jerk
axs[2].plot(dfm.time_s, dfm.load_jerk,'-k', label='Load jerk')
axs[2].legend()
axs[2].set_ylabel("Load Jerk (RPM/s/s)")
ax2 = axs[2].secondary_yaxis('right', functions=(motor_to_load,load_to_motor), color='red')
ax2.set_ylabel("Motor Jerk (RPM/s/s)", color='red')

# Motor torque
axs[3].plot(dfm.time_s, dfm.load_torque, '-k', label='Load torque')
axs[3].set_ylabel("Load Torque (N.m)")
ax2 = axs[3].secondary_yaxis('right', functions=(load_to_motor,motor_to_load), color='red')
ax2.set_ylabel("Motor Torque (N.m)", color='red')
#axs[3].set_xlabel("Time (s)")

# Temperature
axs[4].plot(dfcal.time_s, dfcal.Setpoint, '--r', label='Setpoint')
axs[4].plot(dfcal.time_s, dfcal.Temp, '-k', label='Temp')
axs[4].set_ylim([-1, 100.]) 
axs[4].set_ylabel("Temperature (C)")
axs[4].set_xlabel("Time (s)")

plt.show()
