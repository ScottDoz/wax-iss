import pandas as pd
import glob
import os
import matplotlib.pyplot as plt


# Base directory
label = "TMI_Tests"
prefix = "Melt"

session_file_path = "/home/pi/Data/" + label

# Get list of folders starting with prefix (Cast, Melt, Fluid)
list_of_folders = glob.glob(os.path.join(session_file_path, prefix+"*"))

# Get latest file
exper_folder = max(list_of_folders, key=os.path.getctime)
print(exper_folder)


# Get files
motor_file_path = os.path.join(exper_folder, "motor_log.csv")
cal_file_path = os.path.join(exper_folder, "CAL_log.csv")


gear_ratio = 23.76 # Gear ratio
	
# Read data
dfm = pd.read_csv(motor_file_path) # Motor data
dfcal = pd.read_csv(cal_file_path) # CAL data

# Plot
fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(5,8), sharex=True)

# Motor speed
axs[0].plot(dfm.time_s, dfm.ref_motor_speed/gear_ratio, '--r', label='Ref load speed')
axs[0].plot(dfm.time_s, dfm.load_speed,'-k', label='Load speed')
axs[0].legend()
axs[0].set_ylabel("Speed (RPM)")
#axs[0].set_xlabel("Time (s)")

# Motor torque
axs[1].plot(dfm.time_s, dfm.load_torque, '-k', label='Load torque')
axs[1].set_ylabel("Load Torque (N.m)")
#axs[1].set_xlabel("Time (s)")

# Temperature
axs[2].plot(dfcal.time_s, dfcal.Setpoint, '--r', label='Setpoint')
axs[2].plot(dfcal.time_s, dfcal.Temp, '-k', label='Temp')
axs[2].set_ylim([-1, 100.]) 
axs[2].set_ylabel("Temperature (C)")
axs[2].set_xlabel("Time (s)")

plt.show()
