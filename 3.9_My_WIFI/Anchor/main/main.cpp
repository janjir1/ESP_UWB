/**
 * 
 * @todo
 *  - move strings to flash (less RAM consumption)
 *  - fix deprecated convertation form string to char* startAsAnchor
 *  - give example description
 */
#include <SPI.h>
#include "DW1000Ranging.h"

#include <WiFi.h>
#include <WiFiUdp.h>

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23


#include <WiFi.h>
#include <WiFiUdp.h>

const char *ssid = "Totally not hidden wifi";        // Replace with your WiFi SSID
const char *password = "12346789";  // Replace with your WiFi password
const char *pcIpAddress = "192.168.1.107";  // Replace with your PC's IP address
const int pcPort = 3333;  // Replace with the desired port number

WiFiUDP udp;

void setup() {
   Serial.begin(115200);
  delay(1000);
  //init the configuration
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);


  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize UDP
  udp.begin(1234);  // Local port for UDP communication
}

void sendUDPMessage(const char *message) {
  // Send UDP message to the specified IP address and port
  udp.beginPacket(pcIpAddress, pcPort);
  udp.printf("Time since boot: %lu", millis()/10);
  udp.endPacket();
}

void loop() {
  // Send a UDP message to the PC
  sendUDPMessage("asd");

  delay(10);  // Wait for a second
}


