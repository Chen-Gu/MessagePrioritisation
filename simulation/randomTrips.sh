#!/bin/sh

# https://sumo.dlr.de/wiki/Tools/Trip
# -b t0 -e t1 -p ((t1 - t0) / n)

START=0
END=100

#VEHICLES=100
#PERIOD=$( echo "(($END - $START) / $VEHICLES)" | bc )
#echo $PERIOD

PERIOD=0.1

./randomTrips.py \
	--net-file piccadilly.net.xml \
	--begin $START --end $END \
	--length \
	--period $PERIOD

./randomTrips.py \
	--net-file piccadilly.net.xml \
	--route-file piccadilly.rou.xml \
	--begin $START --end $END \
	--length \
	--period $PERIOD
