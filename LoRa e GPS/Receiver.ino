#include <LoRa.h>

#define NF 5000 

//Starts LoRa protocol
void LoRaInit(){
  if (!LoRa.begin(433E6)) {
    Serial.print("ERROR. Couldn't start LoRa.");
    while (1);
  }

  setSpreadingFactor(6);       // Set spreading factor to the lowest available (SF6)
  setSignalBandwidth(500);     // Set signal bandwidth to the widest available (500 kHz)
  setCodingRate4(5);           // Set coding rate to the lowest available (CR4/5)
}

void SendToComputer(float* data){
  Serial.println("start");
  for(int i = 0; i <= NF+2; i++ ){
    Serial.println(data[i]);
  } 
  Serial.println("finish");
}

void setup() {

  Serial.begin(9600);

  LoRaInit();

}

void loop() {
  
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    Serial.print("Received packet!");
    float data[NF+2];
    LoRa.readBytes((byte*) data, sizeof(data));

    SendToComputer(data);
    Serial.print("Completed my task");
  }

}
