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
import niati as ni
import aticalibration as cal
import json 

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
raw_data = ni.np.array([[0,0,0,0,0,0],[0,0,0,0,0,0]])
numTrials = 3
currentTrial = input("Start from trial number: ")
#*************************************************************************
#*********************** National Instruments details ********************
#*************************************************************************

task = ni.CreateNewTask("Dev5", sR)

#****************************** Main Loop ********************************

tic = ni.time.time()
toc = 0
cnt = 0
ft_bias_probe = ni.np.zeros(6)
ft_bias_plate = ni.np.zeros(6)

print "Calibrating bias for 1s, please do not touch the ft sensor..."
while toc < 1.0:

	offsetForcePlate = ni.np.array(ni.init_readForce(task,cal.S1,toc))
	ft_bias_plate += offsetForcePlate

	cnt = cnt+1
	toc = ni.time.time() - tic

ft_bias_plate /= cnt
print "Calibration done."

# raw_input('Enter to start ...')
for tr in range (currentTrial,numTrials):
	
	# print "Waiting to receive experiment info ..."
	# expInfo = ReadExperiment(sock2)
	# print expInfo

	# Al's Matlab staircase goes here and spits out the conditions and trial numbers 
	# fname = raw_input("File name: ")
	fname = "expInfo"
	dataFolder = "C:/Users/Hulk/Documents/Projects/SixATI_Touch/Data/"
	fileName = "Trial_" + str(tr) + ".json"
	f3 = dataFolder + fname + "Trial_" + str(tr) + ".txt"
	file1 = open(f3,'w')
	file1.write(fname) 
	file1.close()
	# SaveText(f3,expInfo)

	# fname = Al's code output 

	f1 = dataFolder + fname + "Tr" + str(tr) + "_Plate_.txt"
	# f2 = dataFolder + expInfo + "Tr" + str(tr) + "_Position_.txt"
	f4 = dataFolder + fname + "Tr" + str(tr) + "force_time.txt"
	# f5 = dataFolder + expInfo + "Tr" + str(tr) + "position_time.txt"

	# raw_input("Enter when ready ...")
	ni.beepSound()
	print "Recording trial: " + str(tr)


	probeForce, plateForce, posData, frc_time, pos_time, time_elapsed = [],[],[],[],[],[]

	sampleRate_frc = sR # this number should be the same as sR defined above 
	sampleRate_pos = 200.0 # this number should be the same as set in Qualisys 

	frc_frac = 1.0/sampleRate_frc
	pos_frac = 1.0/sampleRate_pos

	trialDuration = 2.5 # seconds
	sC_frc = 0
	sC_pos = 0

	toc = 0
	tic = ni.time.time()
	
	# Main Thread runs experiment 
	while toc < trialDuration:
		toc = ni.time.time()-tic 
		try: 
			if toc > (sC_frc * frc_frac):
				plateForce.append(ni.readForce(task,cal.S1,ni.time.time(),ft_bias_plate)) #sock,address
				sC_frc += 1
				frc_time.append(ni.time.time())



			time_elapsed.append(ni.time.time())		

		except Exception as e:
			print e

	print "Total force samples collected:", sC_frc, " samples"
	print "Time elapsed", toc, " seconds"
	print "Observed Force Frequency", sC_frc/toc, " Hz"

	task.stop()

	# Plot data here after every trial to check validity and ask for user response 
	# Responding for participant 




	ni.SaveData(f1,ni.np.asarray(plateForce))
	ni.SaveData(f4,ni.np.asarray(frc_time))

	contFlag = input("Press (1) for next trial or press zero (0) to stop: ...")
	if contFlag == 0:
		break	

## Cleanup tasks
task.clear()
print "Force sensor task objects cleaned up."