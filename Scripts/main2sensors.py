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
ptx1 = input("Participant 1 ID number: ")
#ptx2 = input("Participant 2 ID number: ")
#ptx3 = input("Participant 3 ID number: ")

#groupID = input("Group ID number: ")
#blockID = input("Block number: ")
trialNum = 49
currentTrial = input("Start from trial number: ")
condition = input("Condition (smooth/rough): ")
condition2 = input("Condition (dry/wet/liquid): ")

trialDur = 30 #input("Trial duration: ")

#*************************************************************************
# *************************** Experiment Parameters ********************
#*************************************************************************
sR = 1000
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
#task3 = ni.CreateNewTask("Dev8", sR)
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
#ft_bias_plate3 = ni.np.zeros(6)
# ft_bias_plate4 = ni.np.zeros(6)
# ft_bias_plate5 = ni.np.zeros(6)
# ft_bias_plate6 = ni.np.zeros(6)


def IdleLoop(pauseTime):
	toc = 0
	tic = time.perf_counter()
	print('Idling for ', pauseTime, 'seconds...')
	while toc < pauseTime:
		toc = time.perf_counter()-tic
		# try: 
		# 	plateForce1b.append(ni.readForce(task1,cal.S15514,ni.time.perf_counter(),ft_bias_plate1)) 
		# 	plateForce2b.append(ni.readForce(task2,cal.S16483,ni.time.perf_counter(),ft_bias_plate2)) 
		# except Exception as e:
		# 	print (e)


stationDeviceID = ['Dev7','Dev3']
stationCounter = 1

# raw_input('Enter to start ...')
for tr in range (int(currentTrial),int(numTrials)):

	if tr == 1 or tr == 13 or tr == 25 or tr == 37:

		task1 = ni.CreateNewTask("Dev7", sR)
		task2 = ni.CreateNewTask("Dev3", sR)

		tic = time.time()
		toc = 0
		cnt = 0
		
		ft_bias_plate1 = ni.np.zeros(6)
		ft_bias_plate2 = ni.np.zeros(6)

		print ("Calibrating bias for 1s, please do not touch the ft sensor...")

		while toc < 1.0:


			offsetForcePlate = ni.np.array(ni.init_readForce(task1,cal.S15514,toc))
			ft_bias_plate1 += offsetForcePlate
			offsetForcePlate = ni.np.array(ni.init_readForce(task2,cal.S16483,toc))
			ft_bias_plate2 += offsetForcePlate
		
			cnt = cnt+1
			toc = time.time() - tic

		ft_bias_plate1 /= cnt
		ft_bias_plate2 /= cnt


	#*************************************************************************
	#*********************** National Instruments details ********************
	#*************************************************************************

	dataFolder = "D:/Projects/MultiForceRecorder/Data/"

	# if groupID % 18 == 0:
	# 	groupID = groupID + 1

	# if blockID % 6 == 0 & blockID <= 3:
	# 	blockID = blockID + 1
	# else:
	# 	blockID = 1 

	fileName1a = dataFolder + str(ptx1)  + "_" + condition + "_" + condition2 + "_Trial_" + str(tr) + "_t1" +".csv" # or csv
	fileName1b = dataFolder + str(ptx1)  + "_" + condition + "_" + condition2 + "_Trial_" + str(tr) + "_t2" +".csv" # or csv

	fileName2a = dataFolder + str(ptx1)  + "_" + condition + "_" + condition2 + "_Trial_" + str(tr) + "_t1" +".csv" # or csv
	fileName2b = dataFolder + str(ptx1)  + "_" + condition + "_" + condition2 + "_Trial_" + str(tr) + "_t2" +".csv" # or csv

	#fileName2 = dataFolder + "ParticipantID_" + str(ptx2) +  "_GroupID_" + str(groupID) + "_BlockID_" + str(blockID) + "_Condition_" + condition + "_Trial_" + str(tr) + ".json"
	#fileName3 = dataFolder + "ParticipantID_" + str(ptx3) +  "_GroupID_" + str(groupID) + "_BlockID_" + str(blockID) + "_Condition_" + condition + "_Trial_" + str(tr) + ".json"

	# f4 = dataFolder + fname + "ID" + "_" + str(groupID) + "_Condition_" + str(condition) + "_Tr_" + str(tr) + ".json"

	# raw_input("Enter when ready ...")



	probeForce, posData, frc_time_a,frc_time_b, pos_time, time_elapsed = [],[],[],[],[],[]
	plateForce1a,plateForce1b, plateForce2a, plateForce2b = [],[],[],[]
	# plateForce1,plateForce2,plateForce3,plateForce4,plateForce5,plateForce6 = [],[],[],[],[],[]

	sampleRate_frc = sR # this number should be the same as sR defined above 
	sampleRate_pos = 200.0 # this number should be the same as set in Qualisys 

	frc_frac = 1.0/sampleRate_frc
	pos_frac = 1.0/sampleRate_pos

	trialDuration = trialDur # seconds
	sC_frc = 0


	# record first contact	trialDuration = trialDur # seconds

	task1 = ni.CreateNewTask("Dev7", sR)
	task2 = ni.CreateNewTask("Dev3", sR)


	ni.beepSound(500)
	IdleLoop(1.5)
	ni.beepSound(1000)
	print ("\nRecording trial: " + str(tr) + " --- First contact")

	toc = 0
	toc1 = 0 
	tic = time.perf_counter()
	tic1 = time.perf_counter()
	#toc = time.perf_counter()-tic

	# Main Thread runs experiment 
	while toc < trialDuration:
		toc = time.perf_counter()-tic
		toc1 = time.perf_counter()-tic1
		try: 
			if toc1 > 0.001:
				plateForce1a.append(ni.readForce(task1,cal.S15514,ni.time.perf_counter(),ft_bias_plate1)) 
				plateForce2a.append(ni.readForce(task2,cal.S16483,ni.time.perf_counter(),ft_bias_plate2)) 
				#plateForce3.append(ni.readForce(task3,cal.S16484,ni.time.time(),ft_bias_plate3)) 
				# plateForce4.append(ni.readForce(task4,cal.S05347,ni.time.time(),ft_bias_plate4)) 
				# plateForce5.append(ni.readForce(task5,cal.S05346,ni.time.time(),ft_bias_plate5)) 
				# plateForce6.append(ni.readForce(task6,cal.S6,ni.time.time(),ft_bias_plate6)) 

				sC_frc += 1
				frc_time_a.append(toc)
				tic1 = time.perf_counter()

		except Exception as e:
			print (e)


	task1.stop()
	task2.stop()


	task1 = ni.CreateNewTask("Dev7", sR)
	task2 = ni.CreateNewTask("Dev3", sR)


	ni.beepSound(500)
	IdleLoop(1.5)
	ni.beepSound(1000)
	print ("Recording trial: " + str(tr) + " --- Second contact")

	sC_frc = 0

	toc = 0
	toc1 = 0 
	tic = time.perf_counter()
	tic1 = time.perf_counter()

	while toc < trialDuration:
		toc = time.perf_counter()-tic
		toc1 = time.perf_counter()-tic1
		try: 
			if toc1 > 0.001:
				plateForce1b.append(ni.readForce(task1,cal.S15514,ni.time.perf_counter(),ft_bias_plate1)) 
				plateForce2b.append(ni.readForce(task2,cal.S16483,ni.time.perf_counter(),ft_bias_plate2))  

				sC_frc += 1
				frc_time_b.append(toc)
				tic1 = time.perf_counter()

		except Exception as e:
			print (e)

	

	print ("Total force samples collected:", sC_frc, " samples")
	print ("Time elapsed", toc, " seconds")
	print ("Observed Force Frequency", sC_frc/toc, " Hz")

	task1.stop()
	task2.stop()
 
	# New way to convert data into a pandas data frame then save it as a json file 

	# print "BlockID: " + str(blockID) + "\n"
	# if blockID == 1:
	# 	fpDat_1 = ni.np.asarray(plateForce1)
	# 	fpDat_2 = ni.np.asarray(plateForce2)
	# 	fpDat_3 = ni.np.asarray(plateForce3)
	# if blockID == 2:
	# 	fpDat_1 = ni.np.asarray(plateForce2)
	# 	fpDat_2 = ni.np.asarray(plateForce3)
	# 	fpDat_3 = ni.np.asarray(plateForce1)
	# if blockID == 3:
	ni.np.set_printoptions(suppress = True)
	fpDat_1a = ni.np.asarray(plateForce1a)
	fpDat_1b = ni.np.asarray(plateForce1b)

	fpDat_2a = ni.np.asarray(plateForce2a)
	fpDat_2b = ni.np.asarray(plateForce2b)

		#fpDat_3 = ni.np.asarray(plateForce2)
	timeDat_a = ni.np.asarray(frc_time_a)
	timeDat_b = ni.np.asarray(frc_time_b)

	trialNum_a = ni.np.repeat(str(tr),len(timeDat_a),axis=None)
	trialNum_b = ni.np.repeat(str(tr),len(timeDat_b),axis=None)

	#groupIDx = ni.np.repeat(groupID,len(timeDat),axis=None)

	# Transfer to the "niati.py" library module in the future 
	tmpResampled1a = list(fpDat_1a)
	tmpResampled1b = list(fpDat_1b)

	tmpResampled2a = list(fpDat_2a) 
	tmpResampled2b = list(fpDat_2b)

	tmpRes1a = ni.pd.DataFrame(tmpResampled1a,columns=['FT_x','FT_y','FT_z','FT_tx','FT_ty','FT_tz']) # ,'FT4','FT5','FT6'
	tmpRes1a.insert(0, "Trial", trialNum_a , True) # Add trial number to the dataframe 
	tmpRes1a.insert(7, "Time", timeDat_a, True) # Add time to dataframe

	tmpRes1b = ni.pd.DataFrame(tmpResampled1b,columns=['FT_x','FT_y','FT_z','FT_tx','FT_ty','FT_tz']) # ,'FT4','FT5','FT6'
	tmpRes1b.insert(0, "Trial", trialNum_b , True)
	tmpRes1b.insert(7, "Time", timeDat_b, True) # Add time to dataframe

	tmpRes2a = ni.pd.DataFrame(tmpResampled2a,columns=['FT_x','FT_y','FT_z','FT_tx','FT_ty','FT_tz']) # ,'FT4','FT5','FT6'
	tmpRes2a.insert(0, "Trial", trialNum_a , True) # Add trial number to the dataframe 
	tmpRes2a.insert(7, "Time", timeDat_a, True) # Add time to dataframe

	tmpRes2b = ni.pd.DataFrame(tmpResampled2b,columns=['FT_x','FT_y','FT_z','FT_tx','FT_ty','FT_tz']) # ,'FT4','FT5','FT6'
	tmpRes2b.insert(0, "Trial", trialNum_b , True)
	tmpRes2b.insert(7, "Time", timeDat_b, True) # Add time to dataframe

	# Save to file 

	if tr <= 6:
		outfile1a = open(fileName1a, "w")
		csvText1a = tmpRes1a.to_csv(index=False)
		outfile1a.writelines(csvText1a)
		outfile1a.close()

		outfile1b = open(fileName1b, "w")
		csvText1b = tmpRes1b.to_csv(index=False)
		outfile1b.writelines(csvText1b)
		outfile1b.close()

	elif tr > 6 and tr <= 12:	
		outfile2a = open(fileName2a, "w")
		csvText2a = tmpRes2a.to_csv(index=False)
		outfile2a.writelines(csvText2a)
		outfile2a.close()

		outfile2b = open(fileName2b, "w")
		csvText2b = tmpRes2b.to_csv(index=False)
		outfile2b.writelines(csvText2b)
		outfile2b.close()
	elif tr > 12 and tr <= 18:	
		outfile1a = open(fileName1a, "w")
		csvText1a = tmpRes1a.to_csv(index=False)
		outfile1a.writelines(csvText1a)
		outfile1a.close()

		outfile1b = open(fileName1b, "w")
		csvText1b = tmpRes1b.to_csv(index=False)
		outfile1b.writelines(csvText1b)
		outfile1b.close()

	elif tr > 18 and tr <= 24:
		outfile2a = open(fileName2a, "w")
		csvText2a = tmpRes2a.to_csv(index=False)
		outfile2a.writelines(csvText2a)
		outfile2a.close()

		outfile2b = open(fileName2b, "w")
		csvText2b = tmpRes2b.to_csv(index=False)
		outfile2b.writelines(csvText2b)
		outfile2b.close()

	elif tr > 24 and tr <= 30:
		outfile1a = open(fileName1a, "w")
		csvText1a = tmpRes1a.to_csv(index=False)
		outfile1a.writelines(csvText1a)
		outfile1a.close()

		outfile1b = open(fileName1b, "w")
		csvText1b = tmpRes1b.to_csv(index=False)
		outfile1b.writelines(csvText1b)
		outfile1b.close()

	elif tr > 30 and tr <= 36:
		outfile2a = open(fileName2a, "w")
		csvText2a = tmpRes2a.to_csv(index=False)
		outfile2a.writelines(csvText2a)
		outfile2a.close()

		outfile2b = open(fileName2b, "w")
		csvText2b = tmpRes2b.to_csv(index=False)
		outfile2b.writelines(csvText2b)
		outfile2b.close()

	elif tr > 36 and tr <= 42:
		outfile1a = open(fileName1a, "w")
		csvText1a = tmpRes1a.to_csv(index=False)
		outfile1a.writelines(csvText1a)
		outfile1a.close()

		outfile1b = open(fileName1b, "w")
		csvText1b = tmpRes1b.to_csv(index=False)
		outfile1b.writelines(csvText1b)
		outfile1b.close()

	elif tr > 42 and tr <= 48:
		outfile2a = open(fileName2a, "w")
		csvText2a = tmpRes2a.to_csv(index=False)
		outfile2a.writelines(csvText2a)
		outfile2a.close()

		outfile2b = open(fileName2b, "w")
		csvText2b = tmpRes2b.to_csv(index=False)
		outfile2b.writelines(csvText2b)
		outfile2b.close()

	#outfile3 = open(fileName3, "w")
	#jsonText3 = tmpRes3.to_json(orient="columns")
	#outfile3.writelines(jsonText3)
	#outfile3.close()
	# jsonFile = json.dumps(jsonText, indent=4)  

	contFlag = input("Press (1) for next trial or press zero (0) to stop: ")
	if contFlag == 0:
		break


	
	## Cleanup tasks
	task1.clear()
	task2.clear()
	#task3.clear()
	# task4.clear()
	# task5.clear()
	# task6.clear()

	del task1
	del task2 
	#del task3
	# del task4 
	# del task5
	# del task6

	print ("Force sensor task objects cleaned up.")

