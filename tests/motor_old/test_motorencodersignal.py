# Plot the encA and encB signals

import pigpio
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

pi = pigpio.pi()
#encA, encB = 26, 16 # Lab settings
encA, encB = 26, 25 # Flight version 16, 26

pi.set_pull_up_down(encA, pigpio.PUD_UP)
pi.set_pull_up_down(encB, pigpio.PUD_UP)


# Initialize data
x_data = []
A_data, B_data = [], []
t0 = time.time()

# Create the figure and axis
fig, ax = plt.subplots()
lineA, = ax.plot([],[],label='encA',lw=2)
lineB, = ax.plot([],[],label='encB',lw=2)

# Function to initialize the plot
def init():
	ax.set_xlim(0,10)
	ax.set_ylim(-0.2,1.5)
	ax.set_xlabel("Time (s)")
	ax.set_ylabel("Signal")
	ax.legend()
	return lineA,lineB,


# Function to update the plot
def update(frame):
	# Read the signal
	t = time.time() - t0 # Current time
	A,B = pi.read(encA), pi.read(encB) # Read encoder signal
	print(f"ENC A: {A}, ENC B: {B}")
	# Append to list
	x_data.append(t)
	A_data.append(A)
	B_data.append(B)
	
	# Update the line data
	lineA.set_data(x_data,A_data)
	lineB.set_data(x_data,B_data)
	
	# Adjust axes
	if t>10:
		ax.set_xlim(t-10, t)
		#ax.set_xticks(range(int(t-10), int(t)+1, 2)) # Update tick positions
	
	return lineA,lineB,

# Setup animation
ani = animation.FuncAnimation(
	fig, update, init_func=init, blit=False, interval=100 # Update every 100 ms
)

# Display the plot
plt.show()
	
