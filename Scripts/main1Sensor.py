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
#	TODO: 
#		>> Make sure the aticalibration.py file contains the correct calibration values 
# 		>> (DONE)=> Think about a different output format. Current one is too tedious / perhaps use pandas with json? 
#*************************************************************************
#************************ Load libraries *********************************
#*************************************************************************
from datetime import datetime
import niati as ni
import aticalibration as cal
import json 
import time

#*************************************************************************
#************************** Get user input *******************************
#*************************************************************************
groupID = 123 #input("Group ID number: ")
trialNum = 123 #input("Number of trials: ")
currentTrial = 1 #input("Start from trial number: ")
condition = 123 #input("Condition: ")
trialDur = 30 #input("Trial duration: ")

#*************************************************************************
# *************************** Experiment Parameters ********************
#*************************************************************************
deviceID = "Dev1"
sR = 1000
sC = 0 # loop counter
quit = False
#Force_all = [] # collect all data in this variable
raw_data = ni.np.array([[0,0,0,0,0,0],[0,0,0,0,0,0]])
numTrials = trialNum

#*************************************************************************
#*********************** National Instruments details ********************
#*************************************************************************
task1 = ni.CreateNewTask(deviceID, sR)


#****************************** Main Loop ********************************
tic = ni.time.time()
toc = 0
cnt = 0
ft_bias_probe = ni.np.zeros(6)
ft_bias_plate1 = ni.np.zeros(6)

print ("Calibrating bias for 1s, please do not touch the ft sensor...")
while toc < 1.0:

	offsetForcePlate = ni.np.array(ni.init_readForce(task1,cal.S05346,toc))
	ft_bias_plate1 += offsetForcePlate

	cnt = cnt+1
	toc = ni.time.time() - tic

ft_bias_plate1 /= cnt

print ("Calibration done.")

# raw_input('Enter to start ...')
for tr in range (currentTrial,numTrials):
	
	#*************************************************************************
	#*********************** National Instruments details ********************
	#*************************************************************************
	task1 = ni.CreateNewTask(deviceID, sR)

	tic = ni.time.time()
	toc = 0
	cnt = 0
	ft_bias_probe = ni.np.zeros(6)
	ft_bias_plate1 = ni.np.zeros(6)
	while toc < 0.15:

		offsetForcePlate = ni.np.array(ni.init_readForce(task1,cal.S05346,toc))
		ft_bias_plate1 += offsetForcePlate

		cnt = cnt+1
		toc = ni.time.time() - tic

	ft_bias_plate1 /= cnt

	# print "Waiting to receive experiment info ..."
	# expInfo = ReadExperiment(sock2)
	# print expInfo

	# Al's Matlab staircase goes here and spits out the conditions and trial numbers 
	# fname = raw_input("File name: ")
	fname = "ConditionInfo_"
	dataFolder = "D:/Projects/MultiForceRecorder/Data"
	# dataFolder = "D:/OneDrive/Documents/Projects/MultiForceRecorder/Data/"
	fileName = "Trial_" + str(tr) + ".json"

	f4 = dataFolder + fname + "ID" + "_" + str(groupID) + "_Condition_" + str(condition) + "_Tr_" + str(tr) + ".json"

	# raw_input("Enter when ready ...")
	ni.beepSound(1000)
	print ("Recording trial: " + str(tr))


	probeForce, posData, frc_time, pos_time, time_elapsed = [],[],[],[],[]
	plateForce1,plateForce2,plateForce3,plateForce4,plateForce5,plateForce6 = [],[],[],[],[],[]

	sampleRate_frc = sR # this number should be the same as sR defined above 
	sampleRate_pos = 200.0 # this number should be the same as set in Qualisys 

	frc_frac = 1.0/sampleRate_frc
	pos_frac = 1.0/sampleRate_pos

	trialDuration = trialDur # seconds
	sC_frc = 0
	sC_pos = 0

	toc = 0
	toc1 = 0 
	tic = time.clock()
	tic1 = time.clock()
	
	# Main Thread runs experiment 
	while toc < trialDuration:
		toc = time.clock()-tic
		toc1 = time.clock()-tic1
		try: 
			if toc1 > 0.001:
				plateForce1.append(ni.readForce(task1,cal.S05346,ni.time.clock(),ft_bias_plate1)) 

				sC_frc += 1
				frc_time.append(toc)
				tic1 = time.clock()

			time_elapsed.append(ni.time.time())		

		except Exception as e:
			print (e)

	print ("Total force samples collected:", sC_frc, " samples")
	print ("Time elapsed", toc, " seconds")
	print ("Observed Force Frequency", sC_frc/toc, " Hz")

	task1.stop()

	# Plot data here after every trial to check validity and ask for user response 
 

	fpDat_4 = []
	# New way to convert data into a pandas data frame then save it as a json file 
	fpDat_1 = ni.np.asarray(plateForce1)

	timeDat = ni.np.asarray(frc_time)
	trialNum = ni.np.repeat(str(tr),len(timeDat),axis=None)
	groupIDx = ni.np.repeat(groupID,len(timeDat),axis=None)

	# Transfer to the "niati.py" library module in the future 
	tmpResampled = list(zip(fpDat_1,timeDat))
	tmpRes = ni.pd.DataFrame(tmpResampled,columns=['FT1','Time'])
	tmpRes.insert(0, "Group_ID", groupIDx , True) # Add participant id to dataframe
	tmpRes.insert(0, "Trial", trialNum , True) # Add trial number to the dataframe 

	# print tmpRes
	# print "\n Type: " , type(tmpResampled) , " Shape: ", len(tmpResampled) , "\n"

	# Plotting
	#ni.plt(fpDat_1)
	print (ni.np.shape(fpDat_1))
	#ni.plt.plot(fpDat_1[:,0],label = "x")
	#ni.plt.plot(fpDat_1[:,1],label = "y")
	ni.plt.plot(fpDat_1[:,2],label = "z")
	ni.plt.legend()
	ni.plt.show()

	# Save to file 
	outfile = open(f4, "w")
	jsonText = tmpRes.to_json(orient="columns") # to_csv
	# jsonFile = json.dumps(jsonText, indent=4)  
	outfile.writelines(jsonText)
	outfile.close()

	contFlag = input("Press (1) for next trial or press zero (0) to stop: ")
	if contFlag == 0:
		break	

	## Cleanup tasks
	task1.clear()

	del task1

	print ("Force sensor task objects cleaned up.")
