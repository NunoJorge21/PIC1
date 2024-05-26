#include <TinyGPSPlus.h>

// The TinyGPSPlus object
TinyGPSPlus gps;

void setup() {
  Serial.begin(115200);
  Serial1.begin(9600); // Using Serial1 for RP2040's first hardware serial port


  Serial.println("GPS Module Test");
}

void loop() {
  while (Serial1.available() > 0) {
    char c = Serial1.read();
    //Serial.print(c); // Print the received character
    //if (gps.encode(Serial1.read())) {
    if (gps.encode(c)) {
      displayInfo();
    }
  }

  if (millis() > 5000 && gps.charsProcessed() < 10) {
    Serial.println(F("No GPS detected: check wiring."));
    while (true);
  }
  delay(1000);
}

void displayInfo() {
  Serial.print(F("Location: "));
  if (gps.location.isValid()) {
    Serial.print("Lat: ");
    Serial.print(gps.location.lat(), 6);
    Serial.print(F(","));
    Serial.print("Lng: ");
    Serial.print(gps.location.lng(), 6);
    Serial.println();
  }  
  else {
    Serial.println(F("INVALID"));
  }
}
