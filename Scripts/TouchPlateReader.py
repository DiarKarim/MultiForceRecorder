#*************************************************************************
#************************** PG Touch Plate Jan 2021 by Diar Karim ********************
#*************************************************************************
# This script runs an experiment (for details see experimental variables below)
# This script will do the following:
#
#	1. Load necessary libraries and define user functions
#	2. Get user input
#	3. Set experimental paramters
#	4. Prepare recording devices (National Instruments and ATI force/torque sensors)
#	5. Run experimental loop until completion
#	6. Clean up program
#	0. Optional network communications parameters have been commented out for future use with MATLAB/others
#
#	Author: Diar Karim
#	Contact: diarkarim@gmail.com
# 	Version: 1.0
#	Date: 28/01/2021
#
#*************************************************************************
#************************ Load libraries *********************************
#*************************************************************************
from datetime import datetime
import time
import daqmx
import matplotlib.pyplot as plt
import socket
import numpy as np
import sys
import winsound
from threading import thread

# import nidaqmx
# from plot_data_stream import PlotDataStream
#from thread import start_new_thread

#*************************************************************************
#*********************** Communication details ***************************
#*************************************************************************
# Create UDP stuff

# Create socket object to connect and send data through
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

ipAddr = '0.0.0.0'
port1 = 5033
address = (ipAddr,port1)
sock.bind(address) # UDP

port2 = 5055
address2 = (ipAddr,port2)
sock2.bind(address2) # UDP 

#*************************************************************************
#************************** Define user functions ************************
#*************************************************************************

def init_readForce(tsk1,S2,times,bias=np.zeros(6)):
	data  = tsk1.read()
	data_cal = np.array(CalibrateForce(data[0][0],S2)) - bias

	return data_cal

def readForce(tsk1,S2,times,sock,addr,bias=np.zeros(6)):
	data  = tsk1.read()
	data_cal = np.array(CalibrateForce(data[0][0],S2)) - bias

	data_out = None
	for d in data_cal[:3]:

		if data_out is None:
			data_out = str(d)
		else:
			data_out += ", " + str(d)
	# Send via UDP
	# print data_out + ', ' + str(times)

	data_out = data_out + ', %lf\n'%(times,)
	# sock.sendto(data_out, addr)

	return data_cal

def CalibrateForce(rawForce,S2):
	fx = np.divide(np.dot(rawForce,np.transpose(S2[0,[0,1,2,3,4,5]])),S2[0,6])
	fy = np.divide(np.dot(rawForce,np.transpose(S2[1,[0,1,2,3,4,5]])),S2[1,6])
	fz = np.divide(np.dot(rawForce,np.transpose(S2[2,[0,1,2,3,4,5]])),S2[2,6])
	tx = np.divide(np.dot(rawForce,np.transpose(S2[3,[0,1,2,3,4,5]])),S2[3,6])
	ty = np.divide(np.dot(rawForce,np.transpose(S2[4,[0,1,2,3,4,5]])),S2[4,6])
	tz = np.divide(np.dot(rawForce,np.transpose(S2[5,[0,1,2,3,4,5]])),S2[5,6])

	forces_cal = [fx, fy, fz, tx, ty, tz]
	return forces_cal

def beepSound():
	frequency = 1000  # Set Frequency in Hertz
	duration = 100  # Set Duration To 1000 ms == 1 second
	winsound.Beep(frequency, duration)

def ReadPosition(sock):
	pos_data, pos_addr_rec = sock.recvfrom(1024)
	# print pos_data
	return np.array((pos_data.split(', '))).astype(float)

def ReadExperiment(sock):
	expData, exp_addr_rec = sock.recvfrom(512)
	# print expData 
	# return np.array((expData.split(', '))).astype(int)
	return expData

def SaveData(txWriter1,data):
		#txWriter1.write(str(data.save) + "\n") # format to a better way
		# print type(data)
		# print data.shape
		np.savetxt(txWriter1, data, delimiter='\t')

def SaveText(txWriter1,data):
		#txWriter1.write(str(data.save) + "\n") # format to a better way
		# print type(data)
		# print data.shape
		# np.savetxt(txWriter1, data)
		txWriter1.write(str(data.save) + "\n") # format to a better way

#*************************************************************************
#************************** Get user input *******************************
#*************************************************************************
# f3 = open("C:/Users/AbdlkarD/Dropbox/Project_06_CatPinch/CatPin_2018/CatPin_2018_Python/CatPin_18_Data/" + fname + "drop_info_.txt","w")

#*************************************************************************
# *************************** Experiment Parameters ********************
#*************************************************************************
sR = 900
sC = 0 # loop counter
quit = False
#Force_all = [] # collect all data in this variable
raw_data = np.array([[0,0,0,0,0,0],[0,0,0,0,0,0]])
numTrials = 3
currentTrial = input("Start from trial number: ")
#*************************************************************************
#*********************** National Instruments details ********************
#*************************************************************************

# Create a channel object
try: 
	task = daqmx.tasks.Task()
	time.sleep(1)

	MAX_CHANNELS = 6
	for channel_idx in range(MAX_CHANNELS):
		channel = daqmx.channels.AnalogInputVoltageChannel()
		channel.physical_channel = "Dev5/ai%d"%(channel_idx,) # Probe ATI F/T sensor
		channel.name = "analog input %d"%(channel_idx,)
		task.add_channel(channel)
	task.configure_sample_clock(sample_rate=sR,samples_per_channel=1)
except Exception:
	task.stop()
	task.clear()
	pass

#*********************** Force sensor calibration ************************
# Create calibration for z axis (These values are hand typed for the specific equipment use. Please use specified
# values if a different force-torque sensor is used, see the supplied calibration file that the specific sensor comes with)
S2_plate = np.asarray([[-0.496660000000000,  -0.051820000000000,   0.921290000000000,  35.645690000000002,  -1.341940000000000, -35.921930000000003,  16.326875402745600], \
	[0.906010000000000, -41.317000000000000,  -0.176790000000000,  20.240610000000000,   0.872910000000000,  20.877949999999998,  16.326875402745600], \
	[17.457380000000001,   0.070960000000000,  19.464089999999999,  -1.015960000000000,  19.566490000000002,  -0.112150000000000,  13.869411432303499], \
	[-0.431720000000000,  -0.729770000000000,  33.724670000000003,  -1.238260000000000, -34.165570000000002,   0.440050000000000,   1.651672784916340], \
	[-35.016159999999999,  -0.139930000000000,  19.147649999999999,  -1.692480000000000,  19.458670000000001,   0.683060000000000,   1.651672784916340], \
	[0.182790000000000, -21.684049999999999,  -0.275770000000000, -20.820660000000000,  -0.578710000000000, -21.132660000000001,   1.149514333214160], \
	[0,                   0,   4.343400000000000,                   0,                   0,                   0,                  0]])

#****************************** Main Loop ********************************

tic = time.time()
toc = 0
cnt = 0
ft_bias_probe = np.zeros(6)
ft_bias_plate = np.zeros(6)

print "Calibrating bias for 1s, please do not touch the ft sensor..."
while toc < 1.0:

	offsetForcePlate = np.array(init_readForce(task,S2_plate,toc))
	ft_bias_plate += offsetForcePlate

	cnt = cnt+1
	toc = time.time() - tic

ft_bias_plate /= cnt

print "Calibration done."

# raw_input('Enter to start ...')

# numStimuli = 4
# numTrials = 128
# numReps = 8
# numConditions = 4
# numActions = 2 

# fineStimuli = np.asarray([100, 220, 290, 320]) # standard 330
# coarseStimuli = np.asarray([1160, 1360, 1520, 1720]) # standard 1120

# textStimuli = np.asarray(fineStimuli, coarseStimuli)


for tr in range (currentTrial,numTrials):
	
	print "Waiting to receive experiment info ..."
	expInfo = ReadExperiment(sock2)
	print expInfo

	# Al's Matlab staircase goes here and spits out the conditions and trial numbers 
	# fname = raw_input("File name: ")
	fname = expInfo
	f3 = "C:/Users/Hulk-10902/Desktop/Al_Ageing_Touch_project/Al_Data/" + fname + "Trial_" + str(tr) + "expInfo.txt"
	file1 = open(f3,'w')
	file1.write(expInfo) 
	file1.close()
	# SaveText(f3,expInfo)

	# fname = Al's code output 

	f1 = "C:/Users/Hulk-10902/Desktop/Al_Ageing_Touch_project/Al_Data/" + expInfo + "Tr" + str(tr) + "_Plate_.txt"
	f2 = "C:/Users/Hulk-10902/Desktop/Al_Ageing_Touch_project/Al_Data/" + expInfo + "Tr" + str(tr) + "_Position_.txt"
	f4 = "C:/Users/Hulk-10902/Desktop/Al_Ageing_Touch_project/Al_Data/" + expInfo + "Tr" + str(tr) + "force_time.txt"
	f5 = "C:/Users/Hulk-10902/Desktop/Al_Ageing_Touch_project/Al_Data/" + expInfo + "Tr" + str(tr) + "position_time.txt"

	# raw_input("Enter when ready ...")
	beepSound()

	probeForce, plateForce, posData, frc_time, pos_time, time_elapsed = [],[],[],[],[],[]

	sampleRate_frc = sR # this number should be the same as sR defined above 
	sampleRate_pos = 200.0 # this number should be the same as set in Qualisys 

	frc_frac = 1.0/sampleRate_frc
	pos_frac = 1.0/sampleRate_pos

	trialDuration = 10.0 # seconds
	sC_frc = 0
	sC_pos = 0

	toc = 0
	tic = time.time()
	
	# Main Thread runs experiment 
	while toc < trialDuration:
		toc = time.time()-tic 
		try: 
			if toc > (sC_frc * frc_frac):
				plateForce.append(readForce(task,S2_plate,time.time(),sock,address,ft_bias_plate))
				sC_frc += 1
				frc_time.append(time.time())

			if toc > (sC_pos * pos_frac):
				posData.append(ReadPosition(sock))
				# print "Pos: " + str(posData)
				sC_pos += 1
				pos_time.append(time.time())

			time_elapsed.append(time.time())		

			# print "Collecting data..."
		except Exception as e:
			print e
			# print "Not working..."

	print "Total force samples collected:", sC_frc, " samples"
	print "Total position samples collected:", sC_pos, " samples"
	print "Time elapsed", toc, " seconds"
	print "Observed Force Frequency", sC_frc/toc, " Hz"
	print "Observed Position Frequency", sC_pos/toc, " Hz"
	task.stop()

	# Plot data here after every trial to check validity and ask for user response 
	# Responding for participant 


	SaveData(f1,np.asarray(plateForce))
	SaveData(f2,np.asarray(posData))
	# SaveData(f3,np.asarray(time_elapsed))
	SaveData(f4,np.asarray(frc_time))
	SaveData(f5,np.asarray(pos_time))


## Cleanup tasks
# try: 
# 	task.stop()
task.clear()
# except: 
print "Force sensor task objects cleaned up."