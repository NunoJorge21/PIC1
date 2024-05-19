#include <LoRa.h>
#include <SPI.h>

#define SS 15
#define RST 2
#define DIO 4
#define NF 1024 //number of samples

int counter = 0;
int sent[NF];
char message[50];
unsigned long t1;
unsigned long t2;

// Function to initialize LoRa
void LoRaInit() {
  LoRa.setPins(SS, RST, DIO);
  if (!LoRa.begin(433E6)) {
    Serial.print("ERROR. Couldn't start LoRa.");
    while (1);
  }

  LoRa.setSpreadingFactor(7);       // Set spreading factor to SF7
  LoRa.setSignalBandwidth(500E3);   // Set signal bandwidth to 500 kHz
  LoRa.setCodingRate4(5);           // Set coding rate to CR4/5
}

// Function to check if the message matches the "S: num num num num" pattern
bool isValidMessage(const char* msg) {
  // Check for "start" or "finish" messages
  if (strcmp(msg, "start") == 0 || strcmp(msg, "finish") == 0) {
    return true;
  }
  
  // Check for the "S:" prefix
  if (strncmp(msg, "S:", 2) != 0) {
    return false;
  }
  // Move the pointer to the start of the numbers
  msg += 5;

  // Loop through each of the four groups
  for (int i = 0; i < 4; i++) {
    // Skip any leading spaces
    while (*msg == ' ') msg++;

    // There must be at least one digit
    if (!isdigit(*msg)) {
      return false;
    }

    // Check the rest of the digits in the number
    while (isdigit(*msg)) {
      msg++;
    }

    // Skip any trailing spaces or end of the string
    if (i < 3) {
      if (*msg != ' ') {
        return false;
      }
      msg++;
    }
  }
  
  // Ensure the message ends after the four groups of digits
  return *msg == '\0';
}

//Sends data through LoRa
void LoRaSend(){
  char msg[50];
  strcpy(msg,"received");
  Serial.println("Sending data");

  if(LoRa.beginPacket()){
    LoRa.print(msg);
    Serial.println(msg);//debug
    LoRa.endPacket();
  }
  if(LoRa.beginPacket()){
    LoRa.print(msg);
    Serial.println(msg);//debug
    LoRa.endPacket();
  }
  if(LoRa.beginPacket()){
    LoRa.print(msg);
    Serial.println(msg);//debug
    LoRa.endPacket();
  }
  else{
    Serial.print("ERROR. Couldn't send data through LoRa.");
    while(1);
  }
  delay(20);
}

void setup() {
  Serial.begin(9600);
  LoRaInit();
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    int index = 0;
    while (LoRa.available() && index < sizeof(message) - 1) {
      message[index++] = (char)LoRa.read();  
    }
    message[index] = '\0';
    if(strcmp(message, "start")==0){
      counter = 0;
      Serial.println("starting to read");
      while(counter < NF){ 
        int packetSize = LoRa.parsePacket();
        if (packetSize) {
          int index = 0;
          while (LoRa.available() && index < sizeof(message) - 1) {
            message[index++] = (char)LoRa.read();  
          }
          message[index] = '\0';

          if (!isValidMessage(message)) {
            sprintf(message, "S: %d %d %d %d", 0, 0, 0, 0);
          }
          if (strcmp(message, "start") != 0 && strcmp(message, "finish") != 0){
            sscanf(message, "S: %d %d %d %d", &sent[counter], &sent[counter+1], &sent[counter+2], &sent[counter+3]);
            counter=counter+4;
          }
          Serial.println(counter);
        }
      }
      delay(1000);
      LoRaSend();
      
      int i = 0;
      counter = 0;
      Serial.println("start");
      while(i < NF/4){
        //Serial.println(sent[i]);
        sprintf(message, "S: %d %d %d %d", sent[counter], sent[counter+1], sent[counter+2], sent[counter+3]);
        //Serial.println(message);
        counter = counter+4;
        i++;
      }
      Serial.println("finish");
    }
  }
  
  
}
