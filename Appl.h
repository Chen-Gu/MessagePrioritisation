#ifndef APPL_H_
#define APPL_H_

#define CAM_INTER 0.2

#include "/home/veins/src/veins/src/veins/modules/application/ieee80211p/DemoBaseApplLayer.h"
#include "/home/veins/src/veins/src/veins/modules/mobility/traci/TraCIMobility.h"
#include "/home/veins/src/veins/src/veins/modules/mobility/traci/TraCICommandInterface.h"

#include<iostream>
#include<fstream>

using namespace Veins;

using Veins::TraCIMobility;
using Veins::TraCICommandInterface;
//using Veins::AnnotationManager; //add for annotations

class Appl : public DemoBaseApplLayer {
    public:
        virtual void initialize(int stage);
        virtual void receiveSignal(cComponent* source, simsignal_t signalID, cObject* obj, cObject* details);
    protected:
        TraCIMobility* mobility;
        TraCICommandInterface* traci;
        TraCICommandInterface::Vehicle* traciVehicle;

        simtime_t lastSent; // the last time this sent a message
        double lastSpeed;   // the last-time speed of a car
        Coord lastDirection; 
        Coord lastPosition;
        
        double CurrAcceleration;

        virtual void onWSM(BaseFrame1609_4* frame);
        virtual void handlePositionUpdate(cObject* obj);
};

#endif /* APPL_H_ */
