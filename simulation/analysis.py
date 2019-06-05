import math
from collections import Counter
import matplotlib.pyplot as plt

# Calculate the number of messages per second based on the message sent 
def calculateMessagePerSecond(timeList):
	time = []
	for i in timeList:
		time.append(math.floor(i))
	
	return dict(Counter(time))
	#print(dict(Counter(time)))

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

def drawMessageAndVehiclePerSecond(m, v):
	x_time = []
	y_vehicle = []

	x_time2 = []
	y_message = []
	for i in v:
		x_time.append(i.keys()[0])
		y_vehicle.append(i.values()[0])

	for i in m.keys():
		x_time2.append(i)

	for i in m.values():
		y_message.append(i)
	
	#print(x_time)
	#print(y_vehicle)
 
	plt.plot(x_time, y_vehicle, linestyle='dashed', label = "The number of vehicles")
	plt.plot(x_time2, y_message, label = "The number of messages") 
  
	plt.xlabel('Time (Second)') 
  
	plt.legend()
	plt.show()

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
	#calculateVehiclePerSecond(timel, myVehiclel, receivedVehiclel)

	drawCarPerSecond(calculateMessagePerSecond(timel), calculateVehiclePerSecond(timel, myVehiclel, receivedVehiclel))

