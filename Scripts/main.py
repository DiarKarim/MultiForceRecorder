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
#************************** Get user input *******************************
#*************************************************************************
ptx1 = input("Participant 1 ID number: ")
ptx2 = input("Participant 2 ID number: ")
ptx3 = input("Participant 3 ID number: ")

groupID = input("Group ID number: ")
blockID = input("Block number: ")
trialNum = input("Number of trials: ")
currentTrial = input("Start from trial number: ")
condition = input("Condition: ")

trialDur = 10 #input("Trial duration: ")

#*************************************************************************
# *************************** Experiment Parameters ********************
#*************************************************************************
sR = 900
sC = 0 # loop counter
quit = False
#Force_all = [] # collect all data in this variable
raw_data = ni.np.array([[0,0,0,0,0,0],[0,0,0,0,0,0]])
numTrials = trialNum

#*************************************************************************
#*********************** National Instruments details ********************
#*************************************************************************
task1 = ni.CreateNewTask("Dev7", sR)
task2 = ni.CreateNewTask("Dev3", sR)
task3 = ni.CreateNewTask("Dev8", sR)
# task4 = ni.CreateNewTask("Dev5", sR)
# task5 = ni.CreateNewTask("Dev6", sR)
# task6 = ni.CreateNewTask("Dev10", sR)

#****************************** Main Loop ********************************
tic = ni.time.time()
toc = 0
cnt = 0
# ft_bias_probe = ni.np.zeros(6)
ft_bias_plate1 = ni.np.zeros(6)
ft_bias_plate2 = ni.np.zeros(6)
ft_bias_plate3 = ni.np.zeros(6)
# ft_bias_plate4 = ni.np.zeros(6)
# ft_bias_plate5 = ni.np.zeros(6)
# ft_bias_plate6 = ni.np.zeros(6)

print "Calibrating bias for 1s, please do not touch the ft sensor..."
while toc < 1.0:

	offsetForcePlate = ni.np.array(ni.init_readForce(task1,cal.S15514,toc))
	ft_bias_plate1 += offsetForcePlate
	offsetForcePlate = ni.np.array(ni.init_readForce(task2,cal.S16483,toc))
	ft_bias_plate2 += offsetForcePlate
	offsetForcePlate = ni.np.array(ni.init_readForce(task3,cal.S16484,toc))
	ft_bias_plate3 += offsetForcePlate
	# offsetForcePlate = ni.np.array(ni.init_readForce(task4,cal.S05347,toc))
	# ft_bias_plate4 += offsetForcePlate
	# offsetForcePlate = ni.np.array(ni.init_readForce(task5,cal.S05346,toc))
	# ft_bias_plate5 += offsetForcePlate
	# offsetForcePlate = ni.np.array(ni.init_readForce(task6,cal.S6,toc))
	# ft_bias_plate6 += offsetForcePlate

	cnt = cnt+1
	toc = ni.time.time() - tic

ft_bias_plate1 /= cnt
ft_bias_plate2 /= cnt
ft_bias_plate3 /= cnt
# ft_bias_plate4 /= cnt
# ft_bias_plate5 /= cnt
# ft_bias_plate6 /= cnt

print "Calibration done."

stationDeviceID = ['Dev7','Dev3','Dev8']
stationCounter = 1

# raw_input('Enter to start ...')
for tr in range (currentTrial,numTrials):
	
	#*************************************************************************
	#*********************** National Instruments details ********************
	#*************************************************************************
	task1 = ni.CreateNewTask("Dev7", sR)
	task2 = ni.CreateNewTask("Dev3", sR)
	task3 = ni.CreateNewTask("Dev8", sR)
	# task4 = ni.CreateNewTask("Dev5", sR)
	# task5 = ni.CreateNewTask("Dev6", sR)
	# task6 = ni.CreateNewTask("Dev10", sR)

	# print "Waiting to receive experiment info ..."
	# expInfo = ReadExperiment(sock2)
	# print expInfo

	# Al's Matlab staircase goes here and spits out the conditions and trial numbers 
	# fname = raw_input("File name: ")
	fname = "ConditionInfo_"
	dataFolder = "D:/Projects/MultiForceRecorder/Data/"
	# dataFolder = "D:/OneDrive/Documents/Projects/MultiForceRecorder/Data/"

	if groupID % 18 == 0:
		groupID = groupID + 1

	if blockID % 6 == 0 & blockID <= 3:
		blockID = blockID + 1
	else:
		blockID = 1 

	fileName1 = dataFolder + "ParticipantID_" + str(ptx1) +  "_GroupID_" + str(groupID) + "_BlockID_" + str(blockID) + "_Condition_" + condition + "_Trial_" + str(tr) + ".json"
	fileName2 = dataFolder + "ParticipantID_" + str(ptx2) +  "_GroupID_" + str(groupID) + "_BlockID_" + str(blockID) + "_Condition_" + condition + "_Trial_" + str(tr) + ".json"
	fileName3 = dataFolder + "ParticipantID_" + str(ptx3) +  "_GroupID_" + str(groupID) + "_BlockID_" + str(blockID) + "_Condition_" + condition + "_Trial_" + str(tr) + ".json"

	# f4 = dataFolder + fname + "ID" + "_" + str(groupID) + "_Condition_" + str(condition) + "_Tr_" + str(tr) + ".json"

	# raw_input("Enter when ready ...")
	ni.beepSound()
	print "Recording trial: " + str(tr)


	probeForce, posData, frc_time, pos_time, time_elapsed = [],[],[],[],[]
	plateForce1,plateForce2,plateForce3 = [],[],[]
	# plateForce1,plateForce2,plateForce3,plateForce4,plateForce5,plateForce6 = [],[],[],[],[],[]

	sampleRate_frc = sR # this number should be the same as sR defined above 
	sampleRate_pos = 200.0 # this number should be the same as set in Qualisys 

	frc_frac = 1.0/sampleRate_frc
	pos_frac = 1.0/sampleRate_pos

	trialDuration = trialDur # seconds
	sC_frc = 0
	sC_pos = 0

	toc = 0
	tic = ni.time.time()
	
	# Main Thread runs experiment 
	while toc < trialDuration:
		toc = ni.time.time()-tic 
		try: 
			if toc > (sC_frc * frc_frac):
				plateForce1.append(ni.readForce(task1,cal.S15514,ni.time.time(),ft_bias_plate1)) 
				plateForce2.append(ni.readForce(task2,cal.S16483,ni.time.time(),ft_bias_plate2)) 
				plateForce3.append(ni.readForce(task3,cal.S16484,ni.time.time(),ft_bias_plate3)) 
				# plateForce4.append(ni.readForce(task4,cal.S05347,ni.time.time(),ft_bias_plate4)) 
				# plateForce5.append(ni.readForce(task5,cal.S05346,ni.time.time(),ft_bias_plate5)) 
				# plateForce6.append(ni.readForce(task6,cal.S6,ni.time.time(),ft_bias_plate6)) 

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
	# task4.stop()
	# task5.stop()
	# task6.stop()
	# Plot data here after every trial to check validity and ask for user response 
 

	fpDat_4 = []
	# New way to convert data into a pandas data frame then save it as a json file 

	print "BlockID: " + str(blockID) + "\n"
	if blockID == 1:
		fpDat_1 = ni.np.asarray(plateForce1)
		fpDat_2 = ni.np.asarray(plateForce2)
		fpDat_3 = ni.np.asarray(plateForce3)
	if blockID == 2:
		fpDat_1 = ni.np.asarray(plateForce2)
		fpDat_2 = ni.np.asarray(plateForce3)
		fpDat_3 = ni.np.asarray(plateForce1)
	if blockID == 3:
		fpDat_1 = ni.np.asarray(plateForce3)
		fpDat_2 = ni.np.asarray(plateForce1)
		fpDat_3 = ni.np.asarray(plateForce2)

	timeDat = ni.np.asarray(frc_time)
	trialNum = ni.np.repeat(str(tr),len(timeDat),axis=None)
	groupIDx = ni.np.repeat(groupID,len(timeDat),axis=None)

	# Transfer to the "niati.py" library module in the future 
	tmpResampled1 = list(zip(fpDat_1,timeDat)) # fpDat_4,fpDat_5,fpDat_6
	tmpResampled2 = list(zip(fpDat_2,timeDat)) # fpDat_4,fpDat_5,fpDat_6
	tmpResampled3 = list(zip(fpDat_3,timeDat)) # fpDat_4,fpDat_5,fpDat_6

	tmpRes1 = ni.pd.DataFrame(tmpResampled1,columns=['FT1','Time']) # ,'FT4','FT5','FT6'
	tmpRes1.insert(0, "Trial", trialNum , True) # Add trial number to the dataframe 
	tmpRes1.insert(0, "Group_ID", groupIDx , True) # Add participant id to dataframe

	tmpRes2 = ni.pd.DataFrame(tmpResampled2,columns=['FT2','Time']) # ,'FT4','FT5','FT6'
	tmpRes2.insert(0, "Trial", trialNum , True) # Add trial number to the dataframe 
	tmpRes2.insert(0, "Group_ID", groupIDx , True) # Add participant id to dataframe

	tmpRes3 = ni.pd.DataFrame(tmpResampled3,columns=['FT3','Time']) # ,'FT4','FT5','FT6'
	tmpRes3.insert(0, "Trial", trialNum , True) # Add trial number to the dataframe 
	tmpRes3.insert(0, "Group_ID", groupIDx , True) # Add participant id to dataframe
	# print tmpRes
	# print "\n Type: " , type(tmpResampled) , " Shape: ", len(tmpResampled) , "\n"

	# Save to file 
	outfile1 = open(fileName1, "w")
	jsonText1 = tmpRes1.to_json(orient="columns")
	outfile1.writelines(jsonText1)
	outfile1.close()

	outfile2 = open(fileName2, "w")
	jsonText2 = tmpRes2.to_json(orient="columns")
	outfile2.writelines(jsonText2)
	outfile2.close()

	outfile3 = open(fileName3, "w")
	jsonText3 = tmpRes3.to_json(orient="columns")
	outfile3.writelines(jsonText3)
	outfile3.close()
	# jsonFile = json.dumps(jsonText, indent=4)  

	contFlag = input("Press (1) for next trial or press zero (0) to stop: ")
	if contFlag == 0:
		break	

	## Cleanup tasks
	task1.clear()
	task2.clear()
	task3.clear()
	# task4.clear()
	# task5.clear()
	# task6.clear()

	del task1
	del task2 
	del task3
	# del task4 
	# del task5
	# del task6

	print "Force sensor task objects cleaned up."