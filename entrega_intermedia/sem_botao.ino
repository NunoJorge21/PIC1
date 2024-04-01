#include <WiFiNINA.h>
#include <PDM.h>

//Inicialização de variáveis

bool LED_SWITCH = false; //Booleana para controlar o led 

//float dB = 0;
const float referenceVoltage = 3.3; // tensão de referência 3.3V
const float calibrationConstant = 100; // Constante de calibração (a determinar!)

static const char channels = 1; // Numero de canais de saída

static const int frequency = 16000; // frequência de amostragem (PCM output) 16kHz 
// (verificar se podemos usar uma frequência mais alta para termos dados com mais qualidade mas um programa mais pesado)

short sampleBuffer[512]; // Buffer to armazenar as amostras, cada uma de 16 bits

int samplesRead; // Numero de amostras lidas


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

// Função de Conversão para dBs
float pdmToDB(int rawValue) {
    // Valor da amostra para uma tensão
    float voltage = ((float)rawValue / 4096.0) * referenceVoltage;

    // Tensão calculada para dB
    float dB = 20.0 * log10(voltage / referenceVoltage) + calibrationConstant;

    return dB;
}


//Setup
void setup() {
  Serial.begin(9600);
  pinMode(LEDB, OUTPUT);
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

//Loop
void loop() {


  if (samplesRead) {

    // Fazer print das amostras no serial plotter/monitor
    for (int i = 0; i < samplesRead; i++) {
      if (channels != 1) {
        Serial.print("Error");
      }
      float voltage = ((float)sampleBuffer[i] / 4096.0) * referenceVoltage;
      Serial.println(String(voltage));

    }

    // Recomeçar a contagem
    samplesRead = 0;
    
  }
  
}
   
