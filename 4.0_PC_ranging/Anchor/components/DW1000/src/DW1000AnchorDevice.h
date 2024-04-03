
#ifndef DW1000ANCHORDEVICE_H
#define DW1000ANCHORDEVICE_H

#include "DW1000Time.h"

class DW1000AnchorDevice {
    public:
        DW1000AnchorDevice();
        DW1000AnchorDevice(byte deviceAddress[]);
        void setRXPPollAck(float power);
        void setFPPPollAck(float power);

        void setRefresh();
        void resetRefresh();
        boolean getRefresh();

        int16_t getRXPPollAck();
        int16_t getFPPPollAck();

        byte* getByteShortAddress();
        boolean isShortAddressEqual(DW1000AnchorDevice* device);

        DW1000Time timePollAckReceived;

        int16_t RXPPollAck;
        int16_t FPPPollAck;

private:
	//device ID
	byte         _shortAddress[2];
    boolean _refreshed = false;
    void randomShortAddress();

};

#endif