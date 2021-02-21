#include "Appl.h"

#include <stdlib.h>
#include <math.h>
#include "ApplMessage_m.h"

#include <math.h>

// from: https://stackoverflow.com/questions/14920675/is-there-a-function-in-c-language-to-calculate-degrees-radians
#define degToRad(angleInDegrees) ((angleInDegrees) * M_PI / 180.0)
#define radToDeg(angleInRadians) ((angleInRadians) * 180.0 / M_PI)

using veins::TraCIMobilityAccess;
using veins::AnnotationManagerAccess;

Define_Module(Appl);

static std::ofstream sent_log, rcvd_log;

void Appl::initialize(int stage)
{
    DemoBaseApplLayer::initialize(stage);

    if (stage == 0)
    {
        T_GenCam_DCC = par("T_GenCam_DCC");
        T_CheckCamGen = par("T_CheckCamGen");

        T_CheckCamGen_timer = new cMessage("T_CheckGenCam Timer", T_CheckCamGen_EVT);
        scheduleAt(simTime() + T_GenCam_DCC, T_CheckCamGen_timer);

        stateChanged = false;
        lastSent = simTime();
        lastSpeed = 0;

        if (!rcvd_log.is_open())
        {
            rcvd_log.open("results_received.txt", std::ofstream::out | std::ofstream::trunc);
            rcvd_log << "Time|CurrentVehicleID|ReceivedVehicleID|Speed|Heading|Distance|Acceleration"<<std::endl;
        }

        if (!sent_log.is_open())
        {
            sent_log.open("results_sent.txt", std::ofstream::out | std::ofstream::trunc);
            sent_log << "Time|CurrentVehicleID|Speed|Heading|Distance|Acceleration"<<std::endl;
        }
    }
}

void Appl::finish()
{
    cancelAndDelete(T_CheckCamGen_timer);
}

void Appl::handleSelfMsg(cMessage *msg) {
    DemoBaseApplLayer::handleSelfMsg(msg);

    if (msg == T_CheckCamGen_timer) {
        considerSendCAM();

        scheduleAt(simTime() + T_GenCam_DCC, T_CheckCamGen_timer);
    }
}

void Appl::receiveSignal(cComponent* source, simsignal_t signalID, cObject* obj, cObject* details) {
    Enter_Method_Silent();
    if (signalID == veins::BaseMobility::mobilityStateChangedSignal) {
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
    veins::ApplMessage* wsm = check_and_cast<veins::ApplMessage*>(frame);

    findHost()->getDisplayString().setTagArg("i", 1, "green");

    const double myHeading = mobility->getHeading().getRad();
    const double receivedVehicleHeading = wsm->getHeading();

    double distance = calculateDistance(mobility->getPositionAt(simTime()), wsm->getLocation());
    Coord mylocation = mobility->getPositionAt(simTime());

    rcvd_log<< simTime() <<"|"
            << myId <<"|"
            << wsm->getSenderAddress() <<"|"
            << wsm->getSpeed() <<"|"
            << abs(myHeading - receivedVehicleHeading) << "|"
            << distance << "|"
            << wsm->getAcceleration() << std::endl;
}

void Appl::handlePositionUpdate(cObject* obj) {
    DemoBaseApplLayer::handlePositionUpdate(obj);

    simtime_t currentTime = simTime();
    double currentSpeed = mobility->getSpeed();
    Coord currentposition = mobility->getPositionAt(currentTime);

    const double currH = mobility->getHeading().getRad();

    stateChanged = stateChanged ||
        abs(currentSpeed - lastSpeed) >= 1.0 ||
        abs(currH - lastHeading) > degToRad(4.0) ||
        calculateDistance(currentposition, lastPosition) > 5.0;
}

bool Appl::shouldSendCAM() {
    return stateChanged || simTime() - lastSent >= T_GenCam_DCC;
}

void Appl::considerSendCAM() {
    if (shouldSendCAM()) {
        simtime_t currentTime = simTime();
        double currentSpeed = mobility->getSpeed();
        double currentHeading = mobility->getHeading().getRad();
        Coord currentposition = mobility->getPositionAt(currentTime);

        veins::ApplMessage* wsm = new veins::ApplMessage();

        wsm->setSenderAddress(myId);
        wsm->setSpeed(currentSpeed);
        wsm->setHeading(currentHeading);
        wsm->setLocation(currentposition);

        //Calculate the acceleration
        if (currentTime - lastSent <= 0)
            CurrAcceleration = NAN;
        else
            CurrAcceleration = (currentSpeed - lastSpeed)/(currentTime - lastSent);

        wsm->setAcceleration(CurrAcceleration);

        populateWSM(wsm);
        sendDown(wsm);

        sent_log << currentTime <<"|"
            << myId <<"|"
            << currentSpeed <<"|"
            << currentHeading << "|"
            << currentposition << "|"
            << CurrAcceleration << std::endl;

        lastSent = currentTime;
        lastSpeed = currentSpeed;
        lastHeading = currentHeading;
        lastPosition = currentposition;
        stateChanged = false;
    }
}
