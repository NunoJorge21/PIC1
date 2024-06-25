#include <PDM.h>
#include <LoRa.h>
#include <TinyGPSPlus.h>
#include <WiFiNINA.h>
#include <SPI.h>

#define BUTTON_PIN 10
#define TS_LED 4//Transmission Sucess LED
#define RE_LED 5 //Recording LED
#define SS 9
#define RST 8
#define DIO 7
#define NSAMP 1024//130000 at 44kHz, 40000 at 16kHz //numero de amostras
//Inicialização de variáveis

//GPS Variables
TinyGPSPlus gps;
char location[40];

//Microphone Variables

bool LED_SWITCH = false; //Booleana para controlar o led 
static const char channels = 1; // Numero de canais de saída
static const int frequency = 25000; // frequência de amostragem (PCM output) 16kHz 
// (verificar se podemos usar uma frequência mais alta para termos dados com mais qualidade mas um programa mais pesado)
short sampleBuffer[512]; // Buffer to armazenar as amostras, cada uma de 16 bits
int samplesRead; // Numero de amostras lidas
short sampled[NSAMP];
int readcounter = 0;


//Initiates GPS [Work in progress]
void GPSInit(){
  Serial1.begin(9600);
  while(!Serial1);
  Serial.println("tamos on no GPS");
}

//Gets Latitude and Longitude [Work in progress]
bool GetGPS(){
  while (Serial1.available() > 0) {
    if (gps.encode(Serial1.read())) {
      if(gps.location.isValid()){
        //Serial.print("GPS Location is valid.");
        sprintf(location, "Lat: %.8f, Lng: %.8f", gps.location.lat(), gps.location.lng());
        //Serial.println(location);
        return true;
      }
      else{
        Serial.println(F("INVALID"));
        return false;
      }
    }
  }
}


//Setup
void setup() {

  //Starting connection to computer
  Serial.begin(9600);
  
  //PINS
  pinMode(LEDB, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);
  pinMode(TS_LED, OUTPUT);
  pinMode(RE_LED, OUTPUT);

  GPSInit();
}

void loop() {
  
  if (digitalRead(BUTTON_PIN) == HIGH) {
    if(GetGPS()){
      Serial.print("got the gps:");
      Serial.println(location);
    
    }else{
      Serial.println("no gps available");
    }
    delay(1000);
  }
}
   
