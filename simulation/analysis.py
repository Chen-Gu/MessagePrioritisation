#!/usr/bin/env python

from __future__ import print_function

import pandas as pd
import numpy as np

import os
import math
from collections import Counter
import matplotlib.pyplot as plt
import queue

from decimal import Decimal

MIN_MESSAGE_THRESHOLD = 20

VERIFY_PER_SEC = 176.7453299687368
SEC_PER_VERIFY = 1.0 / VERIFY_PER_SEC

def getSpeedUtility(s):
	u = 1.0/(1+math.exp(-0.25*s+5.5))

	assert 0 <= u <= 1
	return u

def getHeadingUtility(h):
	h = min(math.degrees(h), 180)

	u = h / 180

	try:
		assert 0 <= u <= 1
	except AssertionError:
		print(h, math.degrees(h), u)
		raise
	return u

def getDistanceUtility(d):
	u = 1.0/(1+math.exp(0.5*d-5))

	assert 0 <= u <= 1
	return u

def getAccelerationUtility(a):
	max_utility_at = 5 # m/s

	a = min(abs(a), max_utility_at)

	u = a / max_utility_at

	try:
		assert 0 <= u <= 1
	except AssertionError:
		print(a, u)
		raise
	return u

UTILITY_MAP = {
	"Speed": getSpeedUtility,
	"Heading": getHeadingUtility,
	"Distance": getDistanceUtility,
	"Acceleration": getAccelerationUtility,
}

def CalculateTotalUtility(x):
	weights = {
		"Speed": 0.25,
		"Heading": 0.25,
		"Distance": 0.25,
		"Acceleration": 0.25,
	}

	return sum(UTILITY_MAP[k](x[k]) * v for (k, v) in weights.items())

# Calculate the number of messages per second based on the message received or sent
def calculateMessagesPerSecond(df):
	times = np.floor(df["Time"])
	
	return dict(Counter(times))

def calculateAverageNeighbourhoodSize(df):
	df = df.copy()

	df["Time"] = np.floor(df["Time"])

	df = df[["Time", "CurrentVehicleID", "ReceivedVehicleID"]]

	print(df)

	gdf = df.groupby(["Time"])

	print(gdf)

	result = {}

	for name, grp in gdf:
		#print("===", name, "===")
		#print(grp)

		gdf2 = grp.groupby(["CurrentVehicleID"])["ReceivedVehicleID"].nunique()

		#print(gdf2)

		#print()
		#print()

		result[name] = gdf2.mean()

	return result

# Calculate the number of cars per second based on the car's ID from message sent.
def calculateVehiclePerSecond(df):
	times = np.floor(df["Time"])

	result = {}

	for time in times.unique():
		ndf = df[(time <= df["Time"]) & (df["Time"] < time + 1)]

		result[int(time)] = len(set(ndf["CurrentVehicleID"].values.tolist()) | set(ndf["ReceivedVehicleID"].values.tolist()))

	return result

def drawVehicleUtility(rcvd, ident):
	fig, ax = plt.subplots()
	i = 0
	marker = ['o', 's', 'x', '^', '+']

	df = rcvd[rcvd["CurrentVehicleID"] == ident]

	gdf = df.groupby(["ReceivedVehicleID"])

	for name, group in gdf:
		x_time = group["Time"].values.tolist()
		y_utility = group["Utility"].values.tolist()

		#skip drawing lines from vehicles that few messages are received 
		if len(x_time) < MIN_MESSAGE_THRESHOLD:
			continue

		ax.plot(x_time, y_utility, marker="{0}".format(marker[i%len(marker)]), markersize=5, label="Vehicle {0}".format(i+1))
		i = i+1

	ax.set_xlabel('Time (Seconds)')
	ax.set_ylabel('Utility')
  
	ax.legend(prop={'size': 9}, loc='upper right')
	fig.savefig("vehicle_utility/utility_{}.pdf".format(ident))

	del fig
	del ax

def drawVehicleTimeToVerify(rcvd, ident):
	fig, ax = plt.subplots()

	df = rcvd[rcvd["CurrentVehicleID"] == ident].copy()

	current_time = None

	pqueue = queue.PriorityQueue()
	time_to_verify = {}

	#print(df)

	for index, row in df.iterrows():

		current_item = (row["Utility"], index, row)

		while not pqueue.empty() and current_time <= row["Time"]:

			item = pqueue.get()

			(item_utility, item_index, item_row) = item

			current_time += SEC_PER_VERIFY

			time_to_verify[item_index] = (current_time - item_row["Time"]) #/ SEC_PER_VERIFY

			assert time_to_verify[item_index] >= 0 #SEC_PER_VERIFY

			#print(item_index, time_to_verify[item_index])

		if pqueue.empty() and (current_time is None or row["Time"] > current_time):
			current_time = row["Time"]

		pqueue.put(current_item)

		#print("TIME:", current_time, "----", "QSIZE", pqueue.qsize())

	while not pqueue.empty():
		item = pqueue.get()

		(item_utility, item_index, item_row) = item

		current_time += SEC_PER_VERIFY

		time_to_verify[item_index] = (current_time - item_row["Time"]) #/ SEC_PER_VERIFY

	xs = list(sorted(time_to_verify))
	ys = [time_to_verify[x] for x in xs]

	df["TTV"] = pd.Series(ys, xs)

	ax.plot(df["Time"].values, df["TTV"].values, marker='o', markersize=5, label="ttv")

	ax.set_xlabel('Time (Seconds)')
	ax.set_ylabel('Time to Verify (Seconds)')
  
	ax.legend(prop={'size': 9}, loc='upper right')
	fig.savefig("vehicle_utility/ttv_{}.pdf".format(ident))

	del fig
	del ax

def drawMessageAndVehiclePerSecond(sent, rcvd):
	fig, ax = plt.subplots()
	fig2, ax2 = plt.subplots()

	ms = calculateMessagesPerSecond(sent)
	m = calculateMessagesPerSecond(rcvd)
	v = calculateVehiclePerSecond(rcvd)

	ans = calculateAverageNeighbourhoodSize(rcvd)

	x_time, y_vehicle = zip(*v.items())
	x_time2, y_message = zip(*m.items())
	x_time3, y_message_sent = zip(*ms.items())
	neigh_xs, neigh_ys = zip(*ans.items())

	ax.plot(x_time2, y_message, linestyle='-', label = "The number of messages received") 
	ax.plot(x_time3, y_message_sent, linestyle='-', label = "The number of messages sent")
	  
	ax.set_xlabel('Time (Seconds)')
	ax.axis([0, 500, 0, 6000])

	ax.legend(prop={'size': 9}, loc='upper right')
	fig.savefig("sentAndReceived.pdf")

	#ax2 = ax.twinx()
	#ax2._get_lines.prop_cycler = ax._get_lines.prop_cycler
	ax2.plot(x_time, y_vehicle, linestyle='-', label = "The number of vehicles")
	ax2.plot(neigh_xs, neigh_ys, linestyle='-.', label = "The average neighbourhood size")

	ax2.set_xlabel('Time (Seconds)')
	ax2.axis([0, 500, 0, 350])

	ax2.legend(prop={'size': 9}, loc='upper right')
	fig2.savefig("vehiclesAndNeighbour.pdf")

	del fig
	del fig2
	del ax
	del ax2

def main():
	print("Opening results files...")

	rcvd = pd.read_csv("results_received.txt", sep='|')
	sent = pd.read_csv("results_sent.txt", sep='|')

	drawMessageAndVehiclePerSecond(sent, rcvd)

	rcvd["Utility"] = rcvd.apply(CalculateTotalUtility, axis=1)

	os.makedirs("vehicle_utility", exist_ok=True)

	all_vids = sorted(set(rcvd["CurrentVehicleID"].values.tolist()))
	for vid in all_vids:
		drawVehicleUtility(rcvd, vid)
		drawVehicleTimeToVerify(rcvd, vid)


if __name__ == "__main__":
	main()
