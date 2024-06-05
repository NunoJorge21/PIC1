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
char location[30];
const int numCoords = 5;
static int coordIndex = 0;
const char coordinates[numCoords][50] = {
  "Lat: 37.7749, Lng: -122.4194",
  "Lat: 37.7849, Lng: -122.4194",
  "Lat: 37.7949, Lng: -122.4194",
  "Lat: 37.8049, Lng: -122.4194",
  "Lat: 37.8149, Lng: -122.4194"
};

//Microphone Variables

bool LED_SWITCH = false; //Booleana para controlar o led 
static const char channels = 1; // Numero de canais de saída
static const int frequency = 25000; // frequência de amostragem (PCM output) 16kHz 
// (verificar se podemos usar uma frequência mais alta para termos dados com mais qualidade mas um programa mais pesado)
short sampleBuffer[512]; // Buffer to armazenar as amostras, cada uma de 16 bits
int samplesRead; // Numero de amostras lidas
short sampled[NSAMP];
int readcounter = 0;

//Process PDM data
void onPDMdata() {
  // Número de bytes disponíveis
  int bytesAvailable = PDM.available();

  // Ler os dados
  PDM.read(sampleBuffer, bytesAvailable);

  // 16 bits ou seja 2 bytes por amostra
  samplesRead = bytesAvailable / 2;
}

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

//Sends data through LoRa
void LoRaSend(short int* data){
  char message[50];
  Serial.println("Sending data");
  LoRaHeader(1);
  for(int i = 0; i < NSAMP; i = i + 4){
    sprintf(message, "S: %d %d %d %d", data[i], data[i+1], data[i+2], data[i+3]); //Tem que ser potência de 2
    if(LoRa.beginPacket()){
      LoRa.print(message);
      //Serial.println(message);//debug
      LoRa.endPacket();
    }
    else{
      Serial.print("ERROR. Couldn't send data through LoRa.");
      while(1);
    }
    delay(20);
  }
  LoRaHeader(0);
  digitalWrite(RE_LED, LOW);
}

void LoRaReceive(){
  char message[50];
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    int index = 0;
    while (LoRa.available() && index < sizeof(message) - 1) {
      message[index++] = (char)LoRa.read();  
    }
    message[index] = '\0';
    if(strcmp(message, "received") == 0) {
      Serial.println(message);
      digitalWrite(TS_LED, HIGH);
      delay(300);
      digitalWrite(TS_LED, LOW);
      delay(100);
      digitalWrite(TS_LED, HIGH);
      delay(300);
      digitalWrite(TS_LED, LOW);
    }
  }
}
//send location by lora
void SendLocation(){
  if(LoRa.beginPacket()){
      LoRa.print(location);
      LoRa.endPacket();
    }
    else{
      Serial.print("ERROR. Couldn't send data through LoRa.");
      while(1);
    }
}
//Adds header to LoRa information
void LoRaHeader(bool a){
  char message[40];
  if(a == true)
  {
    strcpy(message, "start");
    if(LoRa.beginPacket()){
      
      LoRa.print(message);
      LoRa.endPacket();
    }
    else{
      Serial.print("ERROR. Couldn't send data through LoRa.");
      while(1);
    }
    SendLocation();
  }
  else
  {
    strcpy(message, "finish");
    if(LoRa.beginPacket()){
      
      LoRa.print(message);
      LoRa.endPacket();
    }
    else{
      Serial.print("ERROR. Couldn't send data through LoRa.");
      while(1);
    }
  }
  delay(10);
}

//Gets samples and copies it to samples vector
void GetSamples(){
  Serial.println("Obtaining samples");
  digitalWrite(RE_LED, HIGH);
  readcounter = 0;
  while(readcounter < NSAMP){
    for (int i = 0; i < samplesRead; i++) {
      sampled[readcounter] = sampleBuffer[i];
      Serial.print("oi");
      readcounter++;
      if(readcounter >= NSAMP - 1) break;
    }
    // Recomeçar a contagem
    samplesRead = 0;
  }
  Serial.print("\n");
  Serial.println("Samples obtained.");
}

//Initiates GPS [Work in progress]
void GPSInit(){
  Serial1.begin(9600);
  Serial.println("tamos on no GPS");
}

//Gets Latitude and Longitude [Work in progress]
bool GetGPS(int index) {
  if (index < 0 || index >= numCoords) {
    return false;
  }
  strcpy(location, coordinates[index]);
  return true;
}

//Starts PDM
void PDMInit(){
  // Chamar a função que lê os dados à medida que vamos recebendo novos dados
  PDM.onReceive(onPDMdata);

  // Inicializar PDM (Pulse Density Modulation) com o número de canais e frequência de amostragem
  if (!PDM.begin(channels, frequency)) {
    Serial.print("ERROR. Couldn't start PDM channel.");
    while (1);
  }
}

//Debug function, compatible with ReadPythonReceiver.py code in order to test the receiver data
void SendToComputer(short int* data){
  char message[50];
  Serial.println("start");
  for(int i = 0; i < NSAMP; i = i + 4  ){
    sprintf(message, "sent: %d %d %d %d", data[i], data[i+1], data[i+2], data[i+3]);
    Serial.println(message);
  } 
  Serial.println("finish");
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

  //Starting protocols
  PDMInit();
  GPSInit();
  LoRaInit();
}



void loop() {
  
  if (digitalRead(BUTTON_PIN) == HIGH) {
    if(GetGPS(coordIndex)){
      Serial.print("got the gps:");
      Serial.println(location);
      GetSamples();
      
      LoRaSend(sampled);
      Serial.println("Completed my task");
      coordIndex = (coordIndex + 1) % numCoords;
    }else{delay(1000);}
  }

  LoRaReceive();
}
   
