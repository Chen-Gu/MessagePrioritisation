
#include "Appl.h"

#include <stdlib.h>
#include "ApplMessage_m.h"

using Veins::TraCIMobilityAccess;
using Veins::AnnotationManagerAccess;

Define_Module(Appl);

void Appl::initialize(int stage)
{
    DemoBaseApplLayer::initialize(stage);
    if (stage == 0) {
            //setup veins pointers
            mobility = TraCIMobilityAccess().get(getParentModule());
            traci = mobility->getCommandInterface();
            traciVehicle = mobility->getVehicleCommandInterface();
            lastSent = simTime();
        }
}

void Appl::receiveSignal(cComponent* source, simsignal_t signalID, cObject* obj, cObject* details) {
    Enter_Method_Silent();
    if (signalID == Veins::BaseMobility::mobilityStateChangedSignal) {
        handlePositionUpdate(obj);
    }
}

void Appl::onWSM(BaseFrame1609_4* frame)
{
    ApplMessage* wsm = check_and_cast<ApplMessage*>(frame);

    EV << "["<<myId<<"]"<<"Receive message from vehicle [" << wsm->getSenderAddress() <<"]" <<
       " with speed: "<<wsm->getSpeed() <<"m/s" <<
       ", direction: "<<wsm->getDirection() <<
       ", location: "<<wsm->getLocation() <<
       ", acceleration: "<<wsm->getAcceleration() <<"\n";
}

void Appl::handlePositionUpdate(cObject* obj) {
    DemoBaseApplLayer::handlePositionUpdate(obj);

    if (simTime()-lastSent >= 1)
    {
        ApplMessage* wsm = new ApplMessage();

        wsm->setSenderAddress(myId);
        wsm->setSpeed(mobility->getSpeed());
        wsm->setDirection(mobility->getCurrentDirection());
        wsm->setLocation(mobility->getPositionAt(simTime()));
        wsm->setAcceleration(traciVehicle->getAccel());

        //EV << "Speed is: "<< wsm->getSpeed()<<"\n";
        //EV << "getCurrentDirection: " << wsm->getDirection()<<"\n";
        //EV << "Position: " << wsm->getLocation()<<"\n";
        //EV << "Acceleration is: "<< wsm->getAcceleration()<<"\n";

        populateWSM(wsm);
        sendDown(wsm);
        lastSent = simTime();
        //EV << "["<<myId<<"]"<<"Handle the position\n";
    }
}
