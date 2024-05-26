#include <WiFiNINA.h>
#include <PDM.h>

#define BUTTON_PIN 10
#define NSAMP 10000 //130000 at 44kHz, 40000 at 16kHz //numero de amostras

//Inicialização de variáveis

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



//Setup
void setup() {
  Serial.begin(9600);
  pinMode(LEDB, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);
  while (!Serial);
  // Chamar a função que lê os dados à medida que vamos recebendo novos dados
  PDM.onReceive(onPDMdata);

  // >Ganho (ver se é necessário)
  // PDM.setGain(30);

  // Inicializar PDM (Pulse Density Modulation) com o número de canais e frequência de amostragem
  if (!PDM.begin(channels, frequency)) {
    Serial.println("Failed to start PDM!");
    while (1);
  }
}

void loop() {

  if (digitalRead(BUTTON_PIN) == HIGH ) {
    readcounter = 0;
    Serial.println("start of while...");
    while(readcounter <= NSAMP){
      for (int i = 0; i < samplesRead; i++) {
      //Serial.println(sampleBuffer[i]);
      // readcounter++;
      sampled[readcounter] = sampleBuffer[i];
      //Serial.println(sampled[readcounter]);
      Serial.println("lego");
      readcounter++;
      }
      // Recomeçar a contagem
      samplesRead = 0;
    }
    Serial.println("start");
    for(int i = 1; i <= NSAMP; i++ ){
      Serial.println(sampled[i]);
    } 
    Serial.println("finish");
  }

}
   
