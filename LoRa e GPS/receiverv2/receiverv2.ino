#include <LoRa.h>
#include <SPI.h>

#define SS 15
#define RST 2
#define DIO 4

char message[50];

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

// Function to check if the message matches the "sent: num num num num" pattern
bool isValidMessage(const char* msg) {
  // Check for "start" or "finish" messages
  if (strcmp(msg, "start") == 0 || strcmp(msg, "finish") == 0) {
    return true;
  }
  
  // Check for the "sent:" prefix
  if (strncmp(msg, "sent:", 5) != 0) {
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
    
    if (isValidMessage(message)) {
      Serial.println(message);
    } else {
      //Serial.print("Invalid message received:");
      //Serial.println(message);
      sprintf(message, "sent: %d %d %d %d", 0, 0, 0, 0);
      Serial.println(message);
    }
  }
}
