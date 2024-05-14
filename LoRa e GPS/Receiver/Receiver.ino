#include <LoRa.h>
#include <SPI.h>

#define SS 15
#define RST 2
#define DIO 4

char message[50];

//Starts LoRa protocol
void LoRaInit(){

  LoRa.setPins(SS, RST, DIO);
  if (!LoRa.begin(433E6)) {
    Serial.print("ERROR. Couldn't start LoRa.");
    while (1);
  }

  LoRa.setSpreadingFactor(7);       // Set spreading factor to the lowest available (SF6)
  LoRa.setSignalBandwidth(500E3);     // Set signal bandwidth to the widest available (500 kHz)
  LoRa.setCodingRate4(5);           // Set coding rate to the lowest available (CR4/5)
}

void setup() {

  Serial.begin(9600);
  
  LoRaInit();

}

void loop() {
  char received;
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    message[0] = '\0';
    while(LoRa.available()){
      received = (char)LoRa.read();
      strncat(message,&received,1);
    }
    
    Serial.println(message);
  }
  

}
