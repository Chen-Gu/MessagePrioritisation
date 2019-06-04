#include "Appl.h"

#include <stdlib.h>
#include <math.h>
#include "ApplMessage_m.h"

#include <iostream>
#include <fstream>

bool emptyFile = false;

using Veins::TraCIMobilityAccess;
using Veins::AnnotationManagerAccess;

Define_Module(Appl);

void Appl::initialize(int stage)
{
    DemoBaseApplLayer::initialize(stage);
    std::ofstream emp;

    if (stage == 0) 
    {
        //setup veins pointers
        mobility = TraCIMobilityAccess().get(getParentModule());
        traci = mobility->getCommandInterface();
        traciVehicle = mobility->getVehicleCommandInterface();
        lastSent = simTime();
    }

    if (emptyFile == false)
    {
        emp.open("results.txt", std::ofstream::out | std::ofstream::trunc);
        emp << "Time|CurrentVehicleID|ReceivedVehicleID|Speed|Heading|Distance|Acceleration"<<std::endl;
        emp.close();
        emptyFile = true;
    }
}

void Appl::receiveSignal(cComponent* source, simsignal_t signalID, cObject* obj, cObject* details) {
    Enter_Method_Silent();
    if (signalID == Veins::BaseMobility::mobilityStateChangedSignal) {
        handlePositionUpdate(obj);
    }
}

double calculateDistance (Coord mylocation, Coord received)
{
    double lon1 = mylocation.x;
    double lat1 = mylocation.y;
    double lon2 = received.x;
    double lat2 = received.y;

    return sqrt((lon1-lon2)*(lon1-lon2)+(lat1-lat2)*(lat1-lat2));
}

void Appl::onWSM(BaseFrame1609_4* frame)
{
    ApplMessage* wsm = check_and_cast<ApplMessage*>(frame);
    double distance = 0;
    double myHeading = 0;
    double receivedVehicleHeading = 0;

    myHeading = 180*(atan2(mobility->getCurrentDirection().y, mobility->getCurrentDirection().x))/3.14;
    receivedVehicleHeading = 180*(atan2(wsm->getDirection().y, wsm->getDirection().x))/3.14;

    std::ofstream output;

    if (output.is_open() == false)
    {
        output.open ("results.txt", std::fstream::app);
    }

    distance = calculateDistance(mobility->getPositionAt(simTime()), wsm->getLocation());
    Coord mylocation = mobility->getPositionAt(simTime());

    output  << simTime() <<"|"
            << myId <<"|"
            << wsm->getSenderAddress() <<"|"
            << wsm->getSpeed() <<"|"
            //<<", direction: "<<wsm->getDirection()
            << abs(myHeading - receivedVehicleHeading) << "|"
            //", location: "<<wsm->getLocation() << "(" 
            << distance << "|"
            << wsm->getAcceleration() <<"\n";
}

void Appl::handlePositionUpdate(cObject* obj) {
    DemoBaseApplLayer::handlePositionUpdate(obj);

    if (simTime()-lastSent >= CAM_INTER)
    {
        ApplMessage* wsm = new ApplMessage();

        wsm->setSenderAddress(myId);
        wsm->setSpeed(mobility->getSpeed());
        wsm->setDirection(mobility->getCurrentDirection());
        wsm->setLocation(mobility->getPositionAt(simTime()));

        //Calculate the acceleration
        CurrAcceleration = (mobility->getSpeed() - lastSpeed)/0.2;

        wsm->setAcceleration(CurrAcceleration);

        populateWSM(wsm);
        sendDown(wsm);
        lastSent = simTime();
        lastSpeed = mobility->getSpeed();
    }
}
