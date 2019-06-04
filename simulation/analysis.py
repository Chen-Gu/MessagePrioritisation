import math
from collections import Counter

# Calculate the number of messages per second based on the message sent 
def calculateMessagePerSecond(timeList):
	time = []
	for i in timeList:
		time.append(math.floor(i))
	Counter(time)
	print(Counter(time))

# Calculate the number of cars per second based on the car's ID from message sent.
def calculateCarPerSecond(timeList, myVehicleList, receivedVehicleList):
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
		else:
			newList.append(i)
		last = i[0]
		lastItemList = i
	#print(newList)
	for i in newList:
		for m in i:
			if isinstance(m, float):
				d = {}
				d[m] = len(i)-1
				timeVehicleList.append(d)

	#print(timeVehicleList)
	return timeVehicleList


with open("results.txt", "r") as results:
	next(results)
	timel = []
	myVehiclel = []
	receivedVehiclel = []
	for line in results:
		token = line.split('|')
		timel.append(float(token[0]))
		myVehiclel.append(int(token[1]))
		receivedVehiclel.append(int(token[2]))
		
	#calculateMessagePerSecond(timel)
	calculateCarPerSecond(timel, myVehiclel, receivedVehiclel)