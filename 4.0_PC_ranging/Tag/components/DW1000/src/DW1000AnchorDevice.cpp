
#include "DW1000AnchorDevice.h"
#include "DW1000.h"

DW1000AnchorDevice::DW1000AnchorDevice() {
	randomShortAddress();
}

DW1000AnchorDevice::DW1000AnchorDevice(byte deviceAddress[]) {
	memcpy(_shortAddress, deviceAddress, 2);
}



void DW1000AnchorDevice::setRXPPollAck(float RXPower) { RXPPollAck = round(abs(RXPower)*100); }
void DW1000AnchorDevice::setFPPPollAck(float FPPower) { FPPPollAck = round(abs(FPPower)*100); }

int16_t DW1000AnchorDevice::getRXPPollAck() { return RXPPollAck; }
int16_t DW1000AnchorDevice::getFPPPollAck() { return FPPPollAck; }

byte* DW1000AnchorDevice::getByteShortAddress() {
	return _shortAddress;
}

boolean DW1000AnchorDevice::isShortAddressEqual(DW1000AnchorDevice* device) {
	return memcmp(this->getByteShortAddress(), device->getByteShortAddress(), 2) == 0;
}

void DW1000AnchorDevice::randomShortAddress() {
	_shortAddress[0] = random(0, 256);
	_shortAddress[1] = random(0, 256);
}

void DW1000AnchorDevice::setRefresh() { _refreshed = true; }
void DW1000AnchorDevice::resetRefresh() { _refreshed = false; }
boolean DW1000AnchorDevice::getRefresh() { return _refreshed; }

