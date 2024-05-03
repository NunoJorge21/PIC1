#include <OneWire.h> 
#include <DallasTemperature.h>

// Now for the radio libraries
#include <SPI.h>
#include <LoRa.h>


/********************************************************************/
// Data wire is plugged into pin 2 on the Arduino 
#define ONE_WIRE_BUS 0 
/********************************************************************/
// Setup a oneWire instance to communicate with any OneWire devices  
// (not just Maxim/Dallas temperature ICs) 
OneWire myWire(ONE_WIRE_BUS);
/********************************************************************/
// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature mySensor1(&myWire);
float temperature1;

//RF24 radio(9, 10); // CE, CSN

int counter = 0;
float batVolt;
char str_batVolt[6];

//const byte address[6] = "00001";
char str_temperature1[6];
char text[30];

//Analog read battery volatage
const int adc = A0;  // This creates a constant integer in memory that stores the analog pin

void setup() 
{
      // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("Dallas Temperature IC Control Library Demo");
  mySensor1.begin();

  Serial.println("LoRa Sender");

  //LoRa.setPins(ss, reset, dio0);
  LoRa.setPins(15, 2, 4);

  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
}
  

  
void loop() {

  Serial.print("Sending packet: ");
  Serial.println(counter);

  // call sensors.requestTemperatures() to issue a global temperature 
  // request to all devices on the bus 
  /********************************************************************/
  Serial.print(" Requesting temperatures...\n");
  mySensor1.requestTemperatures(); // Send the command to get temperature readings 
  Serial.println("DONE");
  /********************************************************************/
  Serial.print("Temperature is: \n"); 
  temperature1 = mySensor1.getTempCByIndex(0);
  Serial.print("Read temp = "); Serial.print(temperature1);
  // You can have more than one DS18B20 on the same bus.  
  // 0 refers to the first IC on the wire 
  Serial.println(" ºC");
  
  dtostrf(temperature1*100, 4, 0, str_temperature1);
  batVolt = analogRead(adc);  // This reads the analog in value
  batVolt = batVolt*0.0043; //analog to volts conversion
  batVolt = batVolt + 0.03; //calibration
  Serial.print("BatVolt:");Serial.println(batVolt);
  dtostrf(batVolt*100, 3, 0, str_batVolt);
  
  Serial.print("Text=");
  sprintf(text,"boia %s %s", str_temperature1, str_batVolt);
  Serial.println(text);
  
  //radio.write(&text, sizeof(text));
  // Send using LoRa
  LoRa.beginPacket();
  LoRa.print(text);
  //LoRa.print("boia");
  //LoRa.print(" ");
  //LoRa.print((int)temperature1*100);
  
  LoRa.endPacket();

  counter++;
  
  Serial.println(counter);
  //delay(2000);
  ESP.deepSleep(60e6);  //deep sleep for 10 seconds
}
