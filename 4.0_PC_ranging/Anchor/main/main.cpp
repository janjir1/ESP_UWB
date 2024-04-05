#include <SPI.h>
#include "DW1000Ranging.h"

#include <WiFi.h>
#include <WiFiUdp.h>

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23
#define DW_CS 4

// connection pins
const uint8_t PIN_RST = 27; // reset pin
const uint8_t PIN_IRQ = 34; // irq pin
const uint8_t PIN_SS = 4;   // spi select pin

char *ESP_long_adrr =  "A3:13:5B:D5:A9:9A:E2:9C";

const char *ssid = "ESP_UWB";        // Replace with your WiFi SSID
const char *password = "12346789";  // Replace with your WiFi password
const char *pcIpAddress = "192.168.137.1";  // Replace with your PC's IP address
const uint16_t local_port = 1234;

const int pcPort = 3334;  // Replace with the desired port number


#define timestamp_LEN 5
#define int_LEN 2

WiFiUDP udp;

int data_LEN = 102;
static byte data[102];

uint16_t message_num = 0;


void getData() {

  int i = 0;  

  memcpy(data, DW1000Ranging.getCurrentShortAddress(), 2);
  i+=2;
  //data[i] = message_num;
  memcpy(data + i, &message_num, 2);
  i+=int_LEN;

  byte TagData[42];
  DW1000Ranging.getTagInfo(TagData);
  memcpy(data + i, TagData, 42);
  i+=42;

  byte AnchorData[56];
  int AnchorDataSize;
  DW1000Ranging.getAnchorInfo(AnchorData, AnchorDataSize);

  memcpy(data + i, AnchorData, 56);
  data_LEN = 46+AnchorDataSize;
  


}

void sendUDPMessage() {
  // Send UDP message to the specified IP address and port
  udp.beginPacket(pcIpAddress, pcPort);
  getData();
  byte send[data_LEN];
  memcpy(send, data, data_LEN);
  Serial.println(data_LEN);
  
  udp.write(send, data_LEN);
  udp.endPacket();
  message_num++;
}

void newRange() {
  Serial.print("Sending message num: "); Serial.println(message_num);
  sendUDPMessage();
  //DW1000Ranging.visualizeDatas(data);

}

void newBlink(DW1000Device* device) {
  Serial.print("blink; 1 device added ! -> ");
  Serial.print(" short:");
  Serial.println(device->getShortAddress(), HEX);
}

void inactiveDevice(DW1000Device* device) {
  Serial.print("delete inactive device: ");
  Serial.println(device->getShortAddress(), HEX);
}


void setup() {
  Serial.begin(115200);
  delay(1000);
  //init the configuration
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);

  //init the configuration
  DW1000Ranging.initCommunication(PIN_RST, PIN_SS, PIN_IRQ); //Reset, CS, IRQ pin

  DW1000Ranging.attachNewRange(newRange);
  DW1000Ranging.attachBlinkDevice(newBlink);
  DW1000Ranging.attachInactiveDevice(inactiveDevice);

  DW1000.setAntennaDelay(0);
  
  //we start the module as an anchor
  DW1000Ranging.startAsAnchor(ESP_long_adrr, DW1000.MODE_LONGDATA_RANGE_ACCURACY, false);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize UDP
  udp.begin(local_port);  // Local port for UDP communication

}

void loop() {
  
  DW1000Ranging.loop();
  delay(1);

}



