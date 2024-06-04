#include <SPI.h>

#define SS 15
#define RST 2
#define DIO 4
#define NF 1024 // number of samples

int counter = 0;
int sent[NF];
char message[50];
unsigned long t1;
unsigned long t2;
char location[50]; // Allocate enough space for the formatted string
const int pin = 13;
int n = 0; 
float lat[4] = {38.7366, 38.7367, 38.7368, 38.7369};
float lng[4] = {-9.13722, -9.1372, -9.1373, -9.1374};
int dB[4] = {10, 100, 1000, 10000};


void setup() {
  pinMode(pin, INPUT); 
  Serial.begin(9600);
}

void loop() {
  // Convert float to string using dtostrf
  char latBuffer[10];
  char lngBuffer[10];
  dtostrf(lat[n], 8, 4, latBuffer);
  dtostrf(lng[n], 8, 4, lngBuffer);

  // Format the location string
  snprintf(location, sizeof(location), "position:Lat:%s, Lng:%s", latBuffer, lngBuffer);

  // Check if the pin is high
  if (digitalRead(pin) && n < 4) {
    // Perform actions if the pin is high
    Serial.println("start");

    // Send the location data
    Serial.println(location);

    // Send other data if needed
    for (int i = 0; i < NF / 4; i++) {
      sprintf(message, "S: %d %d %d %d", dB[n], dB[n]/10, dB[n]/10, dB[n]/10);
      Serial.println(message);
      counter += 4;
    }
    Serial.println("finish");
    n += 1;
  }
}
