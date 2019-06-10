#!/usr/bin/env python

from __future__ import print_function

import pandas as pd
import numpy as np

import os
import math
from collections import Counter
import matplotlib.pyplot as plt

MIN_MESSAGE_THRESHOLD = 20

def getSpeedUtility(s):
	return 1/(1+math.exp(-0.15*s+5))

def getDirectionUtility(h):
	return 0.0055 * h

def getDistanceUtility(d):
	return 1/(1+math.exp(0.5*d-5))

def getAccelerationUtility(a):
	return 0.05 * a

UTILITY_MAP = {
	"Speed": getSpeedUtility,
	"Direction": getDirectionUtility,
	"Distance": getDistanceUtility,
	"Acceleration": getAccelerationUtility,
}

def CalculateTotalUtility(x):
	weights = {
		"Speed": 0.25,
		"Direction": 0.25,
		"Distance": 0.25,
		"Acceleration": 0.25,
	}

	return sum(UTILITY_MAP[k](x[k]) * v for (k, v) in weights.items())

# Calculate the number of messages per second based on the message received or sent
def calculateMessagesPerSecond(df):
	times = np.floor(df["Time"])
	
	return dict(Counter(times))

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

	df = rcvd[rcvd["CurrentVehicleID"] == ident]

	gdf = df.groupby(["ReceivedVehicleID"])

	for name, group in gdf:
		x_time = group["Time"].values.tolist()
		y_utility = group["Utility"].values.tolist()

		#skip drawing lines from vehicles that few messages are received 
		if len(x_time) < MIN_MESSAGE_THRESHOLD:
			continue

		ax.plot(x_time, y_utility, marker='o', markersize=5, label=name)

	ax.set_xlabel('Time (Seconds)')
	ax.set_ylabel('Utility')
  
	fig.legend()
	fig.savefig("vehicle_utility/utility_{}.pdf".format(ident))

	del fig
	del ax

def drawMessageAndVehiclePerSecond(ms, m, v):
	fig, ax = plt.subplots()

	x_time = list(v.keys())
	y_vehicle = list(v.values())

	x_time2 = list(m.keys())
	y_message = list(m.values())

	x_time3 = list(ms.keys())
	y_message_sent = list(ms.values())
 
	ax.plot(x_time, y_vehicle, linestyle='-.', label = "The number of vehicles")
	ax.plot(x_time2, y_message, linestyle='-', label = "The number of messages received") 
	ax.plot(x_time3, y_message_sent, linestyle='--', label = "The number of messages sent")
  
	ax.set_xlabel('Time (Seconds)')
	ax.axis([0, 250, 0, 500])
  
	fig.legend(prop={'size': 9})
	fig.savefig("mandvpers.pdf")

	del fig
	del ax

def main():
	print("Opening results files...")

	rcvd = pd.read_csv("results_received.txt", sep='|')
	sent = pd.read_csv("results_sent.txt", sep='|')

	drawMessageAndVehiclePerSecond(
		calculateMessagesPerSecond(sent),
		calculateMessagesPerSecond(rcvd),
		calculateVehiclePerSecond(rcvd)
	)

	rcvd["Utility"] = rcvd.apply(CalculateTotalUtility, axis=1)

	os.makedirs("vehicle_utility", exist_ok=True)

	all_vids = sorted(set(rcvd["CurrentVehicleID"].values.tolist()))
	for vid in all_vids:
		drawVehicleUtility(rcvd, vid)


if __name__ == "__main__":
	main()
