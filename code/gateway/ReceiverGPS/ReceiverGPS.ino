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
char location[30];

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

bool isNumeric(const char* str) {
    if (strlen(str) == 0) return false;

    int i = 0;
    if (str[0] == '-') {
        if (strlen(str) == 1) return false;
        i = 1;
    }

    for (; str[i] != '\0'; i++) {
        if (!isdigit(str[i])) return false;
    }

    return true;
}

char* isValidMessage(char message[]) {
    static char result[100];  // Static to ensure the returned pointer remains valid after function returns
    double lat, lng;

    if (sscanf(message, "Lat: %lf, Lng: %lf", &lat, &lng) == 2) {
        strcpy(location, message);
        strcpy(message, "start");
        return message;
    }

    char numbers[100];  // Adjust size as needed
    strncpy(numbers, message + 3, sizeof(numbers) - 1);
    numbers[sizeof(numbers) - 1] = '\0';

    int values[4] = {0, 0, 0, 0};
    int valueIndex = 0;
    bool invalid = false;

    char* token = strtok(numbers, " ");
    while (token != NULL && valueIndex < 4) {
        if (isNumeric(token)) {
            values[valueIndex] = atoi(token);
        } else {
            values[valueIndex] = 0;
            invalid = true;
        }
        valueIndex++;
        token = strtok(NULL, " ");
    }

    snprintf(result, sizeof(result), "S: %d %d %d %d", values[0], values[1], values[2], values[3]);
    return result;
}

//Sends data through LoRa
void LoRaSend(){
  char msg[50];
  strcpy(msg,"received");
  Serial.println("Sending data");

  if(LoRa.beginPacket()){
    LoRa.print(msg);
    //Serial.println(msg);//debug
    LoRa.endPacket();
  }
  if(LoRa.beginPacket()){
    LoRa.print(msg);
    //Serial.println(msg);//debug
    LoRa.endPacket();
  }
  if(LoRa.beginPacket()){
    LoRa.print(msg);
    //Serial.println(msg);//debug
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
          
          strcpy(message , isValidMessage(message));
          

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
      Serial.print("position:");
      Serial.println(location);
      while(i < NF/4){
        sprintf(message, "S: %d %d %d %d", sent[counter], sent[counter+1], sent[counter+2], sent[counter+3]);
        Serial.println(message);
        counter = counter+4;
        i++;
      }
      Serial.println("finish");
    }
  }
  
  
}
