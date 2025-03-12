import nidaqmx
from nidaqmx.constants import AcquisitionType, LoggingMode, LoggingOperation, READ_ALL_AVAILABLE
import time 
import numpy as np
import matplotlib.pyplot as plt
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8899
MESSAGE = b"Hellow!"
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

def CalibrateForce(rawForce,S2):
	fx = np.divide(np.dot(rawForce,np.transpose(S2[0,[0,1,2,3,4,5]])),S2[0,6])
	fy = np.divide(np.dot(rawForce,np.transpose(S2[1,[0,1,2,3,4,5]])),S2[1,6])
	fz = np.divide(np.dot(rawForce,np.transpose(S2[2,[0,1,2,3,4,5]])),S2[2,6])
	tx = np.divide(np.dot(rawForce,np.transpose(S2[3,[0,1,2,3,4,5]])),S2[3,6])
	ty = np.divide(np.dot(rawForce,np.transpose(S2[4,[0,1,2,3,4,5]])),S2[4,6])
	tz = np.divide(np.dot(rawForce,np.transpose(S2[5,[0,1,2,3,4,5]])),S2[5,6])

	forces_cal = [fx, fy, fz, tx, ty, tz]
	return forces_cal


#*********************** Force sensor calibration ************************
# Create calibration for z axis (These values are hand typed for the specific equipment use. Please use specified
# values if a different force-torque sensor is used, see the supplied calibration file that the specific sensor comes with)
S15514 = np.asarray([[0.0312,   0.0776,   -1.8009,  -38.7161,    1.1584,   38.0684,   22.7300], \
						[1.6560,   45.1191,   -0.8398,  -22.4348,   -0.4630,  -22.0653,   22.7300], \
						[22.3292,   -0.4161,   22.2753,    0.3434,   22.7698,    0.1114,   11.7868], \
						[-0.2874,   -0.0087,   38.0849,    0.7525,  -39.2385,   -0.3166,    3.6459], \
						[-43.9207,    0.7330,   22.4165,    0.3298,   23.0408,    0.2020,    3.6459], \
						[1.2901,   22.5031,    0.9025,   21.9048,    0.6125,   22.2444,    3.1484], \
						[0,        0,   	   6.0960,   0,			 0,		   0,		   0]])

S16484 = np.asarray([
						[0.28241,  -0.13714,   1.17546, -38.61107,  -1.45104,  38.93836 , 22.7300084098357],\
						[-3.28831,  45.34583,   1.20929, -22.41186,   0.55131, -22.48435 , 22.7300084098357],\
						[22.51559,   0.40861,  22.56140,   0.75362,  22.34324,   0.73168 , 11.7868333238604],\
						[0.18763,  -0.13501,  39.25437,   1.51803, -38.45637,  -1.38129 , 3.64585766892664],\
						[-44.65971,  -0.86397,  22.13761,   0.85818,  21.62511,   0.65104 , 3.64585766892664],\
						[-1.31238,  23.08110,  -0.97660,  22.42264,  -0.98058,  22.04739 , 3.1484034675519],\
						[0,        0,   	   6.0960,   0,			 0,		   0,		   0]])

S16483 = np.asarray([[-0.7073,   -0.2691,    0.3709 , -38.5947,   -0.6979,   37.7479 ,  22.7300], \
						[-1.6005,   45.2081,   -0.6943,  -22.6254 ,   0.9745 , -21.8092 ,  22.7300], \
						[22.4432,    0.6872 ,  22.5678 ,   0.8257,   22.3852,    1.0115 ,  11.7868], \
						[0.7018 ,  -0.1346,   38.6294  ,  1.5926 , -37.9541  , -1.7441 ,   3.6459], \
						[-45.1274,   -1.1841 ,  22.3349 ,   0.8141,   22.1956,    0.9003 ,   3.6459], \
						[-0.7111,   22.6586,   -0.0178,   22.9260 ,  -0.5666 ,  21.3481 ,   3.1484], \
						[0,        0,   	6.0960, 	0,		  0,		0,		 0]])

S05347 = np.asarray([[0.1568 ,   0.5730 ,   0.2965 , -38.3158 ,  -0.4733  , 39.0906  , 22.7300], \
						[1.0328 ,  43.3303 ,   0.8820 , -21.2713 ,   0.1284 , -23.8151 ,  22.7300], \
						[21.9736 ,  -0.2802 ,  21.1588 ,   0.5205 ,  23.6024  ,  0.1328 ,  11.7868], \
						[-0.7133 ,  -0.0142,   37.4195 ,   1.5479 , -38.7476 ,  -1.0131 ,   3.6459], \
						[-44.4592 ,  -0.3615 ,  18.7278 ,   1.0905,   24.8783  ,  0.3734 ,   3.6459], \
						[1.0906 ,  22.2255 ,  -0.1031 ,  22.2077  , -0.5201 ,  22.2558  ,  3.1484], \
						[0,		  0,	    6.0960,		0,		 0, 		0,		 0]])


S05346 = np.asarray([[-1.76742,  39.51457,   0.90047,  -0.06110,   0.55451, -39.36776, 22.7300084098357],\
						[0.36728, -21.92867,   0.21808,  43.87301,   0.94397, -23.55156, 22.7300084098357],\
						[21.80114,  -0.03462,  22.30035,   0.49316,  22.74034,  -0.41163, 11.7868333238604],\
						[-38.08396,  -0.35036,  -0.27572,   0.10397,  38.09386,  -0.46029, 3.64585766892664],\
						[21.56179,  -0.13572, -45.10742,  -1.54551,  21.19454,   0.25130, 3.64585766892664],\
						[-0.55556,  22.75438,  -0.18012,  21.58710,  -0.66649,  20.57922, 3.1484034675519],\
						[0,		  0,	    6.0960,		0,		 0, 		0,		 0]])

S07623 = np.asarray([ [-0.28640,  -0.51192 ,  0.77879 , 35.52160  ,-0.64844, -35.47104, 14.3514099814838],\
						[-0.86874, -45.41687 ,  0.30396 , 20.26121 ,  0.59983 , 20.88557, 14.3514099814838],\
						[21.77471 ,  0.88531 , 22.37779  , 0.46118 , 22.19267 ,  0.54616, 15.220607086688],\
						[-0.15688 , -0.35225 , 38.49369  , 1.47739, -38.46368 , -0.94547, 1.8011858523043],\
						[-43.80575,  -2.16530,  21.82838 ,  0.56292 , 22.19050 ,  0.80574, 1.8011858523043],\
						[-0.44925, -26.26913 , -0.51028, -24.05659 , -0.52467, -24.39032, 1.12764228871644],\
						[0,        0,   	 4.3434,	0,		 0,			0, 		  		0]])

S11506 = np.asarray([[-0.496660000000000,  -0.051820000000000,   0.921290000000000,  35.645690000000002,  -1.341940000000000, -35.921930000000003,  16.326875402745600], \
					[0.906010000000000, -41.317000000000000,  -0.176790000000000,  20.240610000000000,   0.872910000000000,  20.877949999999998,  16.326875402745600], \
					[17.457380000000001,   0.070960000000000,  19.464089999999999,  -1.015960000000000,  19.566490000000002,  -0.112150000000000,  13.869411432303499], \
					[-0.431720000000000,  -0.729770000000000,  33.724670000000003,  -1.238260000000000, -34.165570000000002,   0.440050000000000,   1.651672784916340], \
					[-35.016159999999999,  -0.139930000000000,  19.147649999999999,  -1.692480000000000,  19.458670000000001,   0.683060000000000,   1.651672784916340], \
					[0.182790000000000, -21.684049999999999,  -0.275770000000000, -20.820660000000000,  -0.578710000000000, -21.132660000000001,   1.149514333214160], \
					[0,                   0,   4.343400000000000,                   0,                   0,                   0,                  0]])








# --- Initialize plot ---
plt.ion()  # Turn on interactive mode

# Number of signals (6 in your case)
num_signals = 6
# Store time-series data (up to some buffer length, e.g., 1000 frames)
buffer_size = 200  # Adjust as needed
data_buffer = np.zeros((num_signals, buffer_size))

# X-axis (time or frame count)
x = np.arange(-buffer_size + 1, 1)

# Create figure and lines
fig, ax = plt.subplots()
lines = [ax.plot(x, data_buffer[i, :], label=f'Signal {i+1}')[0] for i in range(num_signals)]
ax.legend(loc='upper left')
plt.xlabel('Frame (relative)')
plt.ylabel('Amplitude')
plt.title('Real-time 6-channel data')
plt.show()

with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
    task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
    task.ai_channels.add_ai_voltage_chan("Dev1/ai2")
    task.ai_channels.add_ai_voltage_chan("Dev1/ai3")
    task.ai_channels.add_ai_voltage_chan("Dev1/ai4")
    task.ai_channels.add_ai_voltage_chan("Dev1/ai5")
    
    # Get offsets 
    print("Calibrating. Do not touch the device!")
    elapsedTime = 0
    startTime = time.time()
    while(elapsedTime<2.0):
        data = task.read()
        offsets = CalibrateForce(data, S05346)
        elapsedTime=time.time()-startTime


    print("Calibration done. Starting to record data!")
    elapsedTime = 0
    startTime = time.time()
    k = 0 
    while(elapsedTime<10.0):
        data = task.read()

        data_cal = CalibrateForce(data, S05346)

        result = [a - b for a, b in zip(data_cal, offsets)]
        
        Word = str(np.round(result[0],3)) + "," + str(np.round(result[1],3)) + "," + str(np.round(result[2],3)) + "," + str(np.round(result[3],3)) + "," + str(np.round(result[4],3)) + "," + str(np.round(result[5],3)) 
        MESSAGE = Word.encode("utf-8")
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

        # --- Update buffer ---
        data_buffer = np.roll(data_buffer, -1, axis=1)  # Shift left
        data_buffer[:, -1] = result  # Add new data to end

        # --- Update plots ---
        for i, line in enumerate(lines):
            line.set_ydata(data_buffer[i, :])  # Update data
        ax.relim()  # Recompute limits
        ax.autoscale_view()  # Autoscale
        plt.pause(0.001)  # Small pause to update the plot

        elapsedTime=time.time()-startTime
        k = k+1
        print(k)

plt.ioff()  # Turn off interactive mode when done
plt.show()  # Final display