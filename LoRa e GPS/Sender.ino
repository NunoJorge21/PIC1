#include <PDM.h>
#include "Complex.h"
#include <LoRa.h>
#include <TinyGPSPlus.h>
#include <SoftwareSerial.h>

#define BUTTON_PIN 10
#define RX 1
#define TX 0
#define NSAMP 10000 //130000 at 44kHz, 40000 at 16kHz //numero de amostras
#define NF 5000 //half of NSAMP

//Inicialização de variáveis

//GPS Variables
SoftwareSerial gpsSerial(RX, TX);
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

//Fourier Algoithm Variables

Complex j(0.0, 1.0); //Initialization of imaginary unit
Complex X[NF]; //Vector used to calculate the fourier transform with the samples obtained 
float S[NF+2]; //Power density

////Funções

//Function returns the absolute value of a given complex number
double complexAbs(const Complex& c) {
    return sqrt(c.getReal() * c.getReal() + c.getImag() * c.getImag());
}

//Função para processar os dados do microfone pdm
void onPDMdata() {
  // Número de bytes disponíveis
  int bytesAvailable = PDM.available();

  // Ler os dados
  PDM.read(sampleBuffer, bytesAvailable);

  // 16 bits ou seja 2 bytes por amostra
  samplesRead = bytesAvailable / 2;
}

//  Calculates Spectral Density of a given sample and inserts 
//latitude and longitude of the location at the end of the vector
float SpectralDensity() {
  Serial.print("Starting Fourier Algorithm.");
  for(int i = 0; i < NF; i++){
        for(int k = 0; k < NSAMP; k++){
            X[i] += sampled[k]*(cos((2*M_PI*k*i)/NSAMP) - j*sin((2*M_PI*k*i)/NSAMP));
        }
        if(i == 0 || i == NF - 1) S[i] = pow(complexAbs(X[i])/NSAMP, 2);
        else S[i] = 2*pow(complexAbs(X[i])/NSAMP,2);
  }
  Serial.print("Spectral Density calculated.");
  S[NF] = lat;
  S[NF+1] = lng;
  Serial.print("Latitude and Longitude saved.");
}

//Starts LoRa protocol
void LoRaInit(){
  if (!LoRa.begin(433E6)) {
    Serial.print("ERROR. Couldn't start LoRa.");
    while (1);
  }

  setSpreadingFactor(6);       // Set spreading factor to the lowest available (SF6)
  setSignalBandwidth(500);     // Set signal bandwidth to the widest available (500 kHz)
  setCodingRate4(5);           // Set coding rate to the lowest available (CR4/5)
}

//Sends data through LoRa
void LoRaSend(byte* data, size_t length){

  if(LoRa.beginPacket()){
    Serial.print("Sending package");
    LoRa.write(data, length);
    LoRa.endPacket();
  }
  else{
    Serial.print("ERROR. Couldn't send data through LoRa.");
    while(1);
  }
}

//Gets samples and copies it to samples vector
void GetSamples(){
  Serial.print("Obtaining samples");
  readcounter = 0;
  while(readcounter <= NSAMP){
    for (int i = 0; i < samplesRead; i++) {
      sampled[readcounter] = sampleBuffer[i];
      readcounter++;
    }
    // Recomeçar a contagem
    samplesRead = 0;
  }
  Serial.print("Samples obtained.");
}

//Initiates GPS
void GPSInit(){
  if(!gpsSerial.begin(9600)){
    Serial.print("ERROR. Couldn't start GPS.");
    while(1);
  }
}

//Gets Latitude and Longitude
void GetGPS(){
  while (gpsSerial.available() > 0) {
    if (gps.encode(gpsSerial.read())) {
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

//Setup
void setup() {

  //Starting connection to computer
  Serial.begin(9600);

  //PINS
  pinMode(LEDB, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);

  //Starting protocols
  PDMInit();
  GPSInit();
  LoRaInit();
}

void loop() {

  if (digitalRead(BUTTON_PIN) == HIGH ) {

    GetSamples();
    GetGPS();
    SpectralDensity();
    LoRaSend(S, sizeof(S));

    Serial.print("Completed my task");
  }

}
   