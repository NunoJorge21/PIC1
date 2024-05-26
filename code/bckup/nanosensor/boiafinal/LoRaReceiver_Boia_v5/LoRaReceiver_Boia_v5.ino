#include <SPI.h>
#include <LoRa.h>

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#define LORASTRINGSIZE 30
char LoRaMessage[LORASTRINGSIZE];
#define SERVER_IP "192.168.1.93"

#ifndef STASSID
//#define STASSID "Atelier-FF"
//#define STAPSK  "FFFFFFFFFF"
#define STASSID "Vodafone-DD"
#define STAPSK  "DDDDDDDDDD"
#endif


char serialSignature[10]="boia";  //signature of this receiver
char LoRaSignature[10]="init";  //to hold received signature
char receivedChar;
int loraTemp;
float f_temp;
String goTemp;
float batVolt;

//String LoRaMessage;
//String LoRaData;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("LoRa Receiver");

  LoRa.setPins(15, 2, 4);

  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }

  Serial.println();
  Serial.println();
  Serial.println();

  WiFi.begin(STASSID, STAPSK);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // received a packet
    Serial.println("----------");
    Serial.print("Received packet!");
  
    Serial.println();
    
    // read packet
    LoRaMessage[0]='\0';
    while (LoRa.available()) {
     receivedChar = (char)LoRa.read();
     strncat(LoRaMessage,&receivedChar,1);
    }  
	Serial.print(LoRaMessage);
  Serial.println();
	// Decode message
	  sscanf(LoRaMessage,"%s %d %f", LoRaSignature, &loraTemp, &batVolt);
  batVolt = batVolt*0.01;
  Serial.print(("battery Voltage =")); Serial.println(batVolt);
  
	Serial.print(("Signature=")); Serial.println(LoRaSignature);
    //Serial.println(strlen(LoRaSignature));
    Serial.print(("Temp(int)=")); Serial.print(loraTemp); Serial.println("ºC");
    // print RSSI of packet
    Serial.print("RSSI: ");
    Serial.println(LoRa.packetRssi());
  //}
  // wait for WiFi connection
  if ((WiFi.status() == WL_CONNECTED)) {

    WiFiClient client;
    HTTPClient http;

    Serial.print("[HTTP] begin...\n");
    // configure traged server and url
    http.begin(client, "http://"SERVER_IP":8080/api/v1/uHNeEifXKgLXoyFJK0Zp/telemetry" ); //HTTP
    http.addHeader("Content-Type", "application/json");

    Serial.print("[HTTP] POST...\n");
    f_temp = (float)loraTemp*0.01;
    Serial.print(f_temp);
    // start connection and send HTTP header and body
    //int httpCode = http.POST("{\"temperature\":25.5}");
    goTemp = "{\"temperature\":";
    goTemp += String(f_temp);
    goTemp += ",\"battery voltage\":";
    goTemp += String(batVolt);
    goTemp += "}";
    Serial.println(goTemp);
    int httpCode = http.POST(goTemp);

    // httpCode will be negative on error
    if (httpCode > 0) {
      // HTTP header has been send and Server response header has been handled
      Serial.printf("[HTTP] POST... code: %d\n", httpCode);

      // file found at server
      if (httpCode == HTTP_CODE_OK) {
        const String& payload = http.getString();
        Serial.println("received payload:\n<<");
        Serial.println(payload);
        Serial.println(">>");
        
      }
    } else {
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
  }  
  }

  //delay(1000);
  
}
