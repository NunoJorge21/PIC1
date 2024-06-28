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

#define N 40 // Number of latest coordinates to average

//GPS Variables
TinyGPSPlus gps;
char location[40];
double latitudes[N];
double longitudes[N];
int coordIndex = 0;
bool bufferFilled = false;

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
  LoRa.setSignalBandwidth(125E3);     // Set signal bandwidth to the widest available (500 kHz)
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
      for(int i = 0; i<5; i++){
        digitalWrite(TS_LED, HIGH);
        delay(300);
        digitalWrite(TS_LED, LOW);
        delay(100);
      }
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
  while(!Serial1);
  Serial.println("tamos on no GPS");
}

// Function to check if GPS data is too old
bool isDataOld() {
  // Age of the GPS data in milliseconds. Adjust the threshold as needed.
  unsigned long maxAge = 2000; // 2 seconds
  return gps.location.age() > maxAge;
}

// Modified GetGPS function to get coordenates
bool GetGPS(){
  while (Serial1.available() > 0) {
    if (gps.encode(Serial1.read())) {
      if (gps.location.isValid() && !isDataOld()) {
        return true;
      } else {
        Serial.println(F("INVALID OR OLD DATA"));
        return false;
      }
    }
  }
  return false; // No new data
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

// Update coordinates arrays
void updateCoordinates(double lat, double lng) {
  latitudes[coordIndex] = lat;
  longitudes[coordIndex] = lng;
  Serial.print("got the gps:");
  Serial.print("Lat: ");
  Serial.print(lat, 8);
  Serial.print(", Lng: ");
  Serial.println(lng, 8);
  coordIndex = (coordIndex + 1) % N;

  if (coordIndex == 0) {
    bufferFilled = true;
  }
}

// Compute average coordinates
void getAverageCoordinates(double &avgLat, double &avgLng) {
  avgLat = 0;
  avgLng = 0;

  int count = bufferFilled ? N : coordIndex;

  for (int i = 0; i < count; i++) {
    avgLat += latitudes[i];
    avgLng += longitudes[i];
  }

  avgLat /= count;
  avgLng /= count;
}

// Reset coordinates arrays
void resetCoordinates() {
  for (int i = 0; i < N; i++) {
    latitudes[i] = 0;
    longitudes[i] = 0;
  }
  coordIndex = 0;
  bufferFilled = false;
}

void GPSData(){
  resetCoordinates();
  Serial.println("Collecting GPS data...");

  while (!bufferFilled) {
    if (GetGPS() == true) {
      updateCoordinates(gps.location.lat(), gps.location.lng());
      delay(250);
    }
  }

  double avgLat, avgLng;
  getAverageCoordinates(avgLat, avgLng);
  Serial.print("avg got the gps:");
  Serial.print("Lat: ");
  Serial.print(avgLat, 8);
  Serial.print(", Lng: ");
  Serial.println(avgLng, 8);
  sprintf(location, "L:%.8f,%.8f", avgLat, avgLng);
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
  
  if (GetGPS()==true){
      digitalWrite(RE_LED, HIGH);
      delay(200);
      digitalWrite(RE_LED, LOW);
      delay(100);
    if (digitalRead(BUTTON_PIN) == HIGH) {
      digitalWrite(RE_LED, HIGH);
      GPSData();
      // Serial.print("got the gps:");
      // Serial.println(location);
      GetSamples();
      
      LoRaSend(sampled);
      Serial.println("Completed my task");
    }
  }else{
    Serial.println("no gps available or data is old");
    digitalWrite(RE_LED, HIGH);
    delay(800);
    digitalWrite(RE_LED, LOW);
    delay(400);
  }

  LoRaReceive();
}
   
