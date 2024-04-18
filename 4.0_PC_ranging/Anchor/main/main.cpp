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

char ESP_long_adrr[24] =  "A0:10:00:00:00:00:00:00";

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

bool executeSendUDP = false;


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

void sendUDPMessage(void *param) {
  for(;;){

    vTaskDelay(pdMS_TO_TICKS(10));

     if (executeSendUDP) {
      executeSendUDP = false;
      
      // Send UDP message to the specified IP address and port
      udp.beginPacket(pcIpAddress, pcPort);
      getData();
      byte send[data_LEN];
      memcpy(send, data, data_LEN);

      uint8_t delay = DW1000Ranging.getReplyDelayTimeMS();
      vTaskDelay(pdMS_TO_TICKS(delay));

      Serial.print("Sending message num: "); Serial.print(message_num);
      Serial.print(", with delay "); Serial.print(delay);Serial.print(" ms ");
      Serial.print(", length "); Serial.print(data_LEN);Serial.print(" byte ");
      Serial.print(", intercepted "); Serial.print((data_LEN-46)/12);Serial.println(" anchor messages");
      
      udp.write(send, data_LEN);
      udp.endPacket();
      
      message_num++;
      
    }
  }

}

void newRange() {
  
  executeSendUDP = true;

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

void getAdressFromMAC(){
  uint8_t mac[6];
  WiFi.macAddress(mac);
  
  // Print MAC address
  Serial.print("MAC Address: ");
  for (int i = 0; i < 6; ++i) {
    Serial.print(mac[i], HEX);
    if (i < 5) Serial.print(":");
    
  }

  switch (mac[5]) {
    case 0xd4:
        sprintf(ESP_long_adrr, "A1:11:%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
        break;
    case 0xec:
        sprintf(ESP_long_adrr, "A2:12:%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
        break;
    case 0xc8:
        sprintf(ESP_long_adrr, "A3:13:%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
        break;
    case 0xf0:
        sprintf(ESP_long_adrr, "A4:14:%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
        break;
    case 0x5c:
        sprintf(ESP_long_adrr, "A5:15:%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
        break;
    default:
      Serial.println("Unknown device");
      sprintf(ESP_long_adrr, "A0:10:%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
      break;

}



}
void setup() {
  Serial.begin(115200);
  delay(1000);
  //init the configuration

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize UDP
  udp.begin(local_port);  // Local port for UDP communication

  getAdressFromMAC();
  Serial.print(", UWB adress: ");
  Serial.println(ESP_long_adrr);

  xTaskCreate(sendUDPMessage, "WIFI", 2000, NULL, 1, NULL);


  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);

  //init the configuration
  DW1000Ranging.initCommunication(PIN_RST, PIN_SS, PIN_IRQ); //Reset, CS, IRQ pin

  DW1000Ranging.attachNewRange(newRange);
  DW1000Ranging.attachBlinkDevice(newBlink);
  DW1000Ranging.attachInactiveDevice(inactiveDevice);

  DW1000.setAntennaDelay(0);
  
  //we start the module as an anchor
  DW1000Ranging.startAsAnchor(ESP_long_adrr, DW1000.MODE_LONGDATA_RANGE_ACCURACY, false);
  
}



void loop() {
  
  DW1000Ranging.loop();

}



