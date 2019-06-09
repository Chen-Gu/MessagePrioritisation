import math
from collections import Counter
import matplotlib.pyplot as plt

MIN_MESSAGE_THRESHOLD = 20
MONITOR_VEHICLE_ID = 117

def getSpeedUtility(s):
	return 1/(1+math.exp(-0.15*s+5))

def getDirectionUtility(h):
	return 0.0055 * h

def getDistanceUtility(d):
	return 1/(1+math.exp(0.5*d-5))

def getAccelerationUtility(a):
	return 0.05 * a

#equal weights
def CalculateTotalUtility(s, h, d, a):
	return 0.25* (s+h+d+a)

# Calculate the number of messages per second based on the message sent 
def calculateMessageSentPerSecond(timeList):
	time = []
	for i in timeList:
		time.append(math.floor(i))
	
	return dict(Counter(time))

# Calculate the number of messages per second based on the message received 
def calculateMessageReceivedPerSecond(timeList):
	time = []
	for i in timeList:
		time.append(math.floor(i))
	
	return dict(Counter(time))

# Calculate the number of cars per second based on the car's ID from message sent.
def calculateVehiclePerSecond(timeList, myVehicleList, receivedVehicleList):
	time = []
	newList = []
	last = 0
	lastItemList = []
	timeVehicleList = []
	for i in timeList:
		time.append(math.floor(i))

	for i in list(zip(time, myVehicleList, receivedVehicleList)):
		if i[0] == last:
			del newList[-1]
			newList.append(list(set(i+lastItemList)))
			lastItemList = tuple(set(i+lastItemList))
		else:
			newList.append(i)
			lastItemList = i
		last = i[0]

	for i in newList:
		for m in i:
			if isinstance(m, float):
				d = {}
				d[m] = len(i)-1
				timeVehicleList.append(d)

	#print(timeVehicleList)
	return timeVehicleList

# Calculate vehicles that sent messages to current vehicle
def calculateVehicleCommunication(monitorVehicleID):
	vehicleInfoList =[]
	with open("results_received.txt", "r") as results:
		next(results)
		for line in results:
			token = line.split('|')
			if monitorVehicleID == int(token[1]):
				vehicleInfo= []
				vehicleInfo.append(float(token[0]))
				vehicleInfo.append(int(token[2]))
				
				vehicleInfo.append(CalculateTotalUtility(getSpeedUtility(float(token[3])), 
					getDirectionUtility(float(token[4])),
					getDistanceUtility(float(token[5])),
					getAccelerationUtility(float(token[6]))))
				vehicleInfoList.append(vehicleInfo)

	#print(vehicleInfoList)
	return vehicleInfoList


def drawVehicleUtility(l):
	vehicleDic = {}
	for i in l:
		if i[1] not in vehicleDic:
			key = i[1]
			del i[1]
			vehicleDic[key] = []
			vehicleDic[key].append(i)
		else:
			key = i[1]
			del i[1]
			vehicleDic[key].append(i)

	for i in vehicleDic: 
		vehicleDic[i] = list(zip(*vehicleDic[i]))

	for i in vehicleDic:
		x_time = vehicleDic[i][0]
		y_utility = vehicleDic[i][1]

		#skip drawing lines from vehicles that few messages are received 
		if len(x_time) < MIN_MESSAGE_THRESHOLD:
			continue		
		plt.plot(x_time, y_utility, marker='o', markerfacecolor='blue', markersize=5)

	plt.xlabel('Time (Second)')
	plt.ylabel('Utility')
  
	plt.legend()
	plt.show()

def drawMessageAndVehiclePerSecond(ms, m, v):
	x_time = []
	y_vehicle = []

	x_time2 = []
	y_message = []

	x_time3 = []
	y_message_sent = []

	for i in v:
		x_time.append(i.keys()[0])
		y_vehicle.append(i.values()[0])

	for i in ms.keys():
		x_time3.append(i)

	for i in ms.values():
		y_message_sent.append(i)

	for i in m.keys():
		x_time2.append(i)

	for i in m.values():
		y_message.append(i)
 
	plt.plot(x_time, y_vehicle, linestyle='-.', label = "The number of vehicles")
	plt.plot(x_time2, y_message, linestyle='-', label = "The number of messages received") 
	plt.plot(x_time3, y_message_sent, linestyle='--', label = "The number of messages sent")
  
	plt.xlabel('Time (Second)')
	plt.axis([0, 250, 0, 500])
  
	plt.legend(prop={'size': 9})
	plt.show()

with open("results_received.txt", "r") as results, open("results_sent.txt", "r") as results_sent:
	next(results)
	timel = []
	myVehiclel = []
	receivedVehiclel = []
	for line in results:
		token = line.split('|')
		timel.append(float(token[0]))
		myVehiclel.append(int(token[1]))
		receivedVehiclel.append(int(token[2]))

	next(results_sent)
	timel_sent  =[]
	for line2 in results_sent:
		token1 = line2.split('|')
		timel_sent.append(float(token1[0]))

	#calculateMessageReceivedPerSecond(timel)
	#calculateVehiclePerSecond(timel, myVehiclel, receivedVehiclel)

	drawMessageAndVehiclePerSecond(calculateMessageSentPerSecond(timel_sent), calculateMessageReceivedPerSecond(timel), calculateVehiclePerSecond(timel, myVehiclel, receivedVehiclel))

	drawVehicleUtility(calculateVehicleCommunication(MONITOR_VEHICLE_ID))

