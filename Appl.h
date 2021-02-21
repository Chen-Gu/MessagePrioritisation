#ifndef APPL_H_
#define APPL_H_

#include "/home/veins/src/veins/src/veins/modules/application/ieee80211p/DemoBaseApplLayer.h"
#include "/home/veins/src/veins/src/veins/modules/mobility/traci/TraCIMobility.h"
#include "/home/veins/src/veins/src/veins/modules/mobility/traci/TraCICommandInterface.h"
#include "/home/veins/src/veins/src/veins/veins.h"

#include <iostream>
#include <fstream>

using namespace veins;

class Appl : public veins::DemoBaseApplLayer {
    public:
        virtual void initialize(int stage);
        virtual void receiveSignal(cComponent* source, simsignal_t signalID, cObject* obj, cObject* details);
        virtual void finish();

        enum {
            T_CheckCamGen_EVT = 3,
        };

    protected:
        simtime_t T_GenCam_DCC;
        simtime_t T_CheckCamGen;

        cMessage* T_CheckCamGen_timer;

        bool stateChanged;

        simtime_t lastSent; // the last time this sent a message
        double lastSpeed;   // the last-time speed of a car
        double lastHeading;
        Coord lastPosition;
        double CurrAcceleration;

        virtual void onWSM(BaseFrame1609_4* frame);
        virtual void handlePositionUpdate(cObject* obj);
        virtual void handleSelfMsg(cMessage *msg);

    protected:
        bool shouldSendCAM();
        void considerSendCAM();
};

#endif /* APPL_H_ */
