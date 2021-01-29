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

#*************************************************************************
# *************************** Experiment Parameters ********************
#*************************************************************************
sR = 900
sC = 0 # loop counter
quit = False
#Force_all = [] # collect all data in this variable
raw_data = ni.np.array([[0,0,0,0,0,0],[0,0,0,0,0,0]])
numTrials = 3

#*************************************************************************
#************************** Get user input *******************************
#*************************************************************************
currentTrial = input("Start from trial number: ")
groupID = raw_input("Group ID: ")
#*************************************************************************
#*********************** National Instruments details ********************
#*************************************************************************
task1 = ni.CreateNewTask("Dev1", sR)
task2 = ni.CreateNewTask("Dev3", sR)
task3 = ni.CreateNewTask("Dev4", sR)
task4 = ni.CreateNewTask("Dev5", sR)
task5 = ni.CreateNewTask("Dev6", sR)
task6 = ni.CreateNewTask("Dev10", sR)

#****************************** Main Loop ********************************
tic = ni.time.time()
toc = 0
cnt = 0
ft_bias_probe = ni.np.zeros(6)
ft_bias_plate1 = ni.np.zeros(6)
ft_bias_plate2 = ni.np.zeros(6)
ft_bias_plate3 = ni.np.zeros(6)
ft_bias_plate4 = ni.np.zeros(6)
ft_bias_plate5 = ni.np.zeros(6)
ft_bias_plate6 = ni.np.zeros(6)

print "Calibrating bias for 1s, please do not touch the ft sensor..."
while toc < 1.0:

	offsetForcePlate = ni.np.array(ni.init_readForce(task1,cal.S1,toc))
	ft_bias_plate1 += offsetForcePlate
	offsetForcePlate = ni.np.array(ni.init_readForce(task2,cal.S2,toc))
	ft_bias_plate2 += offsetForcePlate
	offsetForcePlate = ni.np.array(ni.init_readForce(task3,cal.S3,toc))
	ft_bias_plate3 += offsetForcePlate
	offsetForcePlate = ni.np.array(ni.init_readForce(task4,cal.S4,toc))
	ft_bias_plate4 += offsetForcePlate
	offsetForcePlate = ni.np.array(ni.init_readForce(task5,cal.S5,toc))
	ft_bias_plate5 += offsetForcePlate
	offsetForcePlate = ni.np.array(ni.init_readForce(task6,cal.S6,toc))
	ft_bias_plate6 += offsetForcePlate

	cnt = cnt+1
	toc = ni.time.time() - tic

ft_bias_plate1 /= cnt
ft_bias_plate2 /= cnt
ft_bias_plate3 /= cnt
ft_bias_plate4 /= cnt
ft_bias_plate5 /= cnt
ft_bias_plate6 /= cnt

print "Calibration done."

# raw_input('Enter to start ...')
for tr in range (currentTrial,numTrials):
	
	# print "Waiting to receive experiment info ..."
	# expInfo = ReadExperiment(sock2)
	# print expInfo

	# Al's Matlab staircase goes here and spits out the conditions and trial numbers 
	# fname = raw_input("File name: ")
	fname = "ConditionInfo_"
	# dataFolder = "C:/Users/Hulk/Documents/Projects/SixATI_Touch/Data/"
	dataFolder = "D:/OneDrive/Documents/Projects/MultiForceRecorder/Data/"
	fileName = "Trial_" + str(tr) + ".json"

	f4 = dataFolder + fname + "ID" + "_" + str(groupID) + "_Tr_" + str(tr) + ".json"

	# raw_input("Enter when ready ...")
	ni.beepSound()
	print "Recording trial: " + str(tr)


	probeForce, posData, frc_time, pos_time, time_elapsed = [],[],[],[],[]
	plateForce1,plateForce2,plateForce3,plateForce4,plateForce5,plateForce6 = [],[],[],[],[],[]

	sampleRate_frc = sR # this number should be the same as sR defined above 
	sampleRate_pos = 200.0 # this number should be the same as set in Qualisys 

	frc_frac = 1.0/sampleRate_frc
	pos_frac = 1.0/sampleRate_pos

	trialDuration = 0.1 # seconds
	sC_frc = 0
	sC_pos = 0

	toc = 0
	tic = ni.time.time()
	
	# Main Thread runs experiment 
	while toc < trialDuration:
		toc = ni.time.time()-tic 
		try: 
			if toc > (sC_frc * frc_frac):
				plateForce1.append(ni.readForce(task1,cal.S1,ni.time.time(),ft_bias_plate1)) 
				plateForce2.append(ni.readForce(task2,cal.S2,ni.time.time(),ft_bias_plate2)) 
				plateForce3.append(ni.readForce(task3,cal.S3,ni.time.time(),ft_bias_plate3)) 
				plateForce4.append(ni.readForce(task4,cal.S4,ni.time.time(),ft_bias_plate4)) 
				plateForce5.append(ni.readForce(task5,cal.S5,ni.time.time(),ft_bias_plate5)) 
				plateForce6.append(ni.readForce(task6,cal.S6,ni.time.time(),ft_bias_plate6)) 

				sC_frc += 1
				frc_time.append(ni.time.time())

			time_elapsed.append(ni.time.time())		

		except Exception as e:
			print e

	print "Total force samples collected:", sC_frc, " samples"
	print "Time elapsed", toc, " seconds"
	print "Observed Force Frequency", sC_frc/toc, " Hz"

	task1.stop()
	task2.stop()
	task2.stop()
	task4.stop()
	task5.stop()
	task6.stop()
	# Plot data here after every trial to check validity and ask for user response 
 

	fpDat_4 = []
	# New way to convert data into a pandas data frame then save it as a json file 
	fpDat_1 = ni.np.asarray(plateForce1)
	fpDat_2 = ni.np.asarray(plateForce2)
	fpDat_3 = ni.np.asarray(plateForce3)
	fpDat_4 = ni.np.asarray(plateForce4)
	fpDat_5 = ni.np.asarray(plateForce5)
	fpDat_6 = ni.np.asarray(plateForce6)
	timeDat = ni.np.asarray(frc_time)
	trialNum = ni.np.repeat(str(tr),len(timeDat),axis=None)
	groupIDx = ni.np.repeat(groupID,len(timeDat),axis=None)

	# Transfer to the "niati.py" library module in the future 
	tmpResampled = list(zip(fpDat_1,fpDat_2,fpDat_3,fpDat_4,fpDat_5,fpDat_6,timeDat))
	tmpRes = ni.pd.DataFrame(tmpResampled,columns=['FT1','FT2','FT3','FT4','FT5','FT6','Time'])
	tmpRes.insert(0, "Participant_ID", groupIDx , True) # Add participant id to dataframe
	tmpRes.insert(0, "Trial", trialNum , True) # Add trial number to the dataframe 

	print tmpRes
	print "\n Type: " , type(tmpResampled) , " Shape: ", len(tmpResampled) , "\n"

	# Save to file 
	outfile = open(f4, "w")
	jsonText = tmpRes.to_json(orient="columns")
	# jsonFile = json.dumps(jsonText, indent=4)  
	outfile.writelines(jsonText)
	outfile.close()

	contFlag = input("Press (1) for next trial or press zero (0) to stop: ")
	if contFlag == 0:
		break	

## Cleanup tasks
task1.clear()
task2.clear()
task3.clear()
task4.clear()
task5.clear()
task6.clear()
print "Force sensor task objects cleaned up."