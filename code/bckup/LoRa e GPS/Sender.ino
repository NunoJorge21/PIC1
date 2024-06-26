#include <PDM.h>
#include <LoRa.h>
#include <TinyGPSPlus.h>
#include <WiFiNINA.h>
#include <SPI.h>

#define BUTTON_PIN 10
#define SS 9
#define RST 8
#define DIO 7
#define NSAMP 2048 //130000 at 44kHz, 40000 at 16kHz //numero de amostras

//Inicialização de variáveis

//GPS Variables
TinyGPSPlus gps;
float lat;
float lng;

//Microphone Variables

bool LED_SWITCH = false; //Booleana para controlar o led 
static const char channels = 1; // Numero de canais de saída
static const int frequency = 25000; // frequência de amostragem (PCM output) 16kHz 
// (verificar se podemos usar uma frequência mais alta para termos dados com mais qualidade mas um programa mais pesado)
short sampleBuffer[512]; // Buffer to armazenar as amostras, cada uma de 16 bits
int samplesRead; // Numero de amostras lidas
short sampled[NSAMP];
int readcounter = 0;


////Funções

//Função para processar os dados do microfone pdm
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
  char message[30];
  Serial.println("Sending data");
  LoRaHeader(1);
  for(int i = 0; i < NSAMP; i = i + 4){
    sprintf(message, "sent %d: %d %d %d %d ", (i/4), data[i], data[i+1], data[i+2], data[i+3]);
    if(LoRa.beginPacket()){
      
      LoRa.print(message);
      LoRa.endPacket();
    }
    else{
      Serial.print("ERROR. Couldn't send data through LoRa.");
      while(1);
    }
    delay(20);
  }
  LoRaHeader(0);
}

void LoRaHeader(bool a)
{
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
  readcounter = 0;
  while(readcounter <= NSAMP){
    for (int i = 0; i < samplesRead; i++) {
      sampled[readcounter] = sampleBuffer[i];
      Serial.print("oi");
      readcounter++;
    }
    // Recomeçar a contagem
    samplesRead = 0;
  }
  Serial.print("\n");
  Serial.println("Samples obtained.");
}

//Initiates GPS
void GPSInit(){
  Serial1.begin(9600);
  while(!Serial1);
  Serial.println("tamos on no GPS");
}

//Gets Latitude and Longitude
void GetGPS(){
  while (Serial1.available() > 0) {
    if (gps.encode(Serial1.read())) {
      if(gps.location.isValid()){
        Serial.print("GPS Location is valid.");
        lat = gps.location.lat();
        lng = gps.location.lng();
      }
      else{
        Serial.print("GPS location invalid.");
      }
    }
  }
  sampled[NSAMP] = lat;
  sampled[NSAMP+1] = lng;
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

void SendToComputer(short int* data){
  Serial.println("start");
  for(int i = 0; i < NSAMP; i++ ){
    Serial.println(data[i]);
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

  while (!Serial);
  //Starting protocols
  PDMInit();
  //GPSInit();
  LoRaInit();
}

void loop() {

  if (digitalRead(BUTTON_PIN) == HIGH ) {

    GetSamples();
    //GetGPS();

    SendToComputer(sampled);
    LoRaSend(sampled);

    delay(1000);
    Serial.println("Completed my task");
  }

}
   