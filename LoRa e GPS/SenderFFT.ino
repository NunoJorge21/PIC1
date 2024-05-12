#include <PDM.h>
#include <LoRa.h>
#include <TinyGPSPlus.h>
#include <WiFiNINA.h>
#include <SPI.h>

#define BUTTON_PIN 10
#define SS 9
#define RST 8
#define DIO 7
#define NSAMP 2048//130000 at 44kHz, 40000 at 16kHz //numero de amostras
#define NF 1024
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

//Fourier Algorithm

int X[NF];
float S[NF];

byte  sine_data [91]=
{
0,  
4,    9,    13,   18,   22,   27,   31,   35,   40,   44, 
49,   53,   57,   62,   66,   70,   75,   79,   83,   87, 
91,   96,   100,  104,  108,  112,  116,  120,  124,  127,  
131,  135,  139,  143,  146,  150,  153,  157,  160,  164,  
167,  171,  174,  177,  180,  183,  186,  189,  192,  195,       //Paste this at top of program
198,  201,  204,  206,  209,  211,  214,  216,  219,  221,  
223,  225,  227,  229,  231,  233,  235,  236,  238,  240,  
241,  243,  244,  245,  246,  247,  248,  249,  250,  251,  
252,  253,  253,  254,  254,  254,  255,  255,  255,  255
};
float f_peaks[5];
////Funções

//Needed for EasyFFT algorithm
float sine(int i){
  int j=i;
  float  out;
  while(j<0){j=j+360;}
  while(j>360){j=j-360;}
  if(j>-1   && j<91){out=  sine_data[j];}
  else if(j>90  && j<181){out= sine_data[180-j];}
  else if(j>180  && j<271){out= -sine_data[j-180];}
  else if(j>270 && j<361){out= -sine_data[360-j];}
  return (out/255);
}

//Needed for EasyFFT algorithm
float cosine(int i){
  int j=i;
  float  out;
  while(j<0){j=j+360;}
  while(j>360){j=j-360;}
  if(j>-1   && j<91){out=  sine_data[90-j];}
  else if(j>90  && j<181){out= -sine_data[j-90];}
  else  if(j>180 && j<271){out= -sine_data[270-j];}
  else if(j>270 && j<361){out= sine_data[j-270];}
  return (out/255);
}

//Algorithm EasyFFT
float FFT(short int in[], float Frequency){
  Serial.print("Starting Fourier Algorithm.");
  unsigned  int data[12]={1,2,4,8,16,32,64,128,256,512,1024,2048};
  int a,c1,f,o,x;
  a=NSAMP;  
                                 
  for(int i=0;i<12;i++)                 //calculating  the levels
  { 
    if(data[i]<=a){o=i;}
    else break;
  }
   
  int in_ps[data[o]]={};     //input for sequencing
  float out_r[data[o]]={};   //real part of transform
  float  out_im[data[o]]={};  //imaginory part of transform
          
  x=0;  
  for(int b=0;b<o;b++)                     // bit reversal
  {
    
    c1=data[b];
    f=data[o]/(c1+c1);
    for(int  j=0;j<c1;j++)
    { 
      x=x+1;
      in_ps[x]=in_ps[j]+f;
    }
  }
  
  for(int i=0;i<data[o];i++)            // update input array as per bit reverse order
  {
    if(in_ps[i]<a)
      {out_r[i]=in[in_ps[i]];}
    if(in_ps[i]>a)
      {out_r[i]=in[in_ps[i]-a];}      
  }
  
  int i10,i11,n1;
  float e,c,s,tr,ti;

  for(int  i=0;i<o;i++)                                    //fft
  {
    i10=data[i];              // overall values of sine/cosine  :
    i11=data[o]/data[i+1];    // loop with similar sine cosine:
    e=360/data[i+1];
    e=0-e;
    n1=0;

    for(int j=0;j<i10;j++)
    {
      c=cosine(e*j);
      s=sine(e*j);    
      n1=j;
          
      for(int  k=0;k<i11;k++)
      {
        tr=c*out_r[i10+n1]-s*out_im[i10+n1];
        ti=s*out_r[i10+n1]+c*out_im[i10+n1];
          
        out_r[n1+i10]=out_r[n1]-tr;
        out_r[n1]=out_r[n1]+tr;
          
        out_im[n1+i10]=out_im[n1]-ti;
        out_im[n1]=out_im[n1]+ti;          
          
        n1=n1+i10+i10;
      }       
    }
  }
  
  //---> here onward out_r contains  amplitude and our_in conntains frequency (Hz)
  for(int i=0;i<data[o-1];i++)               // getting amplitude from compex number
    {
      out_r[i]=sqrt(out_r[i]*out_r[i]+out_im[i]*out_im[i]);  // to  increase the speed delete sqrt
      out_im[i]=i*Frequency/NSAMP;
      
      //Serial.print(out_im[i]); Serial.print("Hz");
      //Serial.print("\	");                            // un comment to print freuency bin    
      //Serial.println(out_r[i]);  
    }

  x=0;       // peak detection
  for(int i=1;i<data[o-1]-1;i++)
  {
    if(out_r[i]>out_r[i-1] &&  out_r[i]>out_r[i+1]) 
      {in_ps[x]=i;    //in_ps array used for storage of  peak number
      x=x+1;}    
  }

  s=0;
  c=0;
  for(int  i=0;i<x;i++)             // re arraange as per magnitude
  {
    for(int  j=c;j<x;j++)
    {
      if(out_r[in_ps[i]]<out_r[in_ps[j]]) 
        {s=in_ps[i];
        in_ps[i]=in_ps[j];
        in_ps[j]=s;}
    }
    c=c+1;
  }

  for(int i=0;i<5;i++)     //  updating f_peak array (global variable)with descending order
  {
    f_peaks[i]=out_im[in_ps[i]];
  }
  Serial.println("Fourier Transform calculated.");
  for(int i = 0; i < NF; i++)
    X[i] = round(out_r[i]);
}

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
void LoRaSend(int* data){
  char message[50];
  Serial.println("Sending data");
  LoRaHeader(1);
  for(int i = 0; i < NF; i = i + 4){
    sprintf(message, "sent: %d %d %d %d", data[i], data[i+1], data[i+2], data[i+3]); //Tem que ser potência de 2
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

//Adds header to LoRa information
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

//Gets Latitude and Longitude [Work in progress]
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

//Debug function, compatible with ReadPythonReceiver.py code in order to test the receiver data
void SendToComputer(int* data){
  char message[50];
  Serial.println("start");
  for(int i = 0; i < NF; i = i + 4  ){
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

  while (!Serial);
  //Starting protocols
  PDMInit();
  //GPSInit(); [Work in progress]
  LoRaInit();
}

void loop() {

  if (digitalRead(BUTTON_PIN) == HIGH ) {

    GetSamples();
    //GetGPS(); [Work in progress]
    
    FFT(sampled, frequency);
    //SendToComputer(X);
    LoRaSend(X);
    
    delay(1000);
    Serial.println("Completed my task");
  }

}
   
