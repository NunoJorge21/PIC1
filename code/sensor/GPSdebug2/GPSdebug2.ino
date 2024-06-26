#include <PDM.h>
#include <LoRa.h>
#include <TinyGPSPlus.h>
#include <WiFiNINA.h>
#include <SPI.h>

#define BUTTON_PIN 10
#define TS_LED 4 // Transmission Success LED
#define RE_LED 5 // Recording LED
#define SS 9
#define RST 8
#define DIO 7
#define NSAMP 1024 // Number of samples

#define N 40 // Number of latest coordinates to average

// GPS Variables
TinyGPSPlus gps;
char location[40];
double latitudes[N];
double longitudes[N];
int coordIndex = 0;
bool bufferFilled = false;

// Microphone Variables
bool LED_SWITCH = false; // Boolean to control the LED 
static const char channels = 1; // Number of output channels
static const int frequency = 25000; // Sampling frequency (PCM output)
short sampleBuffer[512]; // Buffer to store samples, each 16-bit
int samplesRead; // Number of samples read
short sampled[NSAMP];
int readcounter = 0;

// Initiates GPS [Work in progress]
void GPSInit(){
  Serial1.begin(9600);
  while(!Serial1);
  Serial.println("GPS initialized");
}

// Gets Latitude and Longitude [Work in progress]
bool GetGPS(){
  while (Serial1.available() > 0) {
    if (gps.encode(Serial1.read())) {
      if(gps.location.isValid()){
        sprintf(location, "Lat: %.8f, Lng: %.8f", gps.location.lat(), gps.location.lng());
        return true;
      } else {
        return false;
      }
    }
  }
  return false;
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

// Setup
void setup() {
  // Starting connection to computer
  Serial.begin(9600);

  // PINS
  pinMode(TS_LED, OUTPUT);
  pinMode(RE_LED, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);

  GPSInit();
}

void loop() {
  if (GetGPS() == true) {
    updateCoordinates(gps.location.lat(), gps.location.lng());
  }

  if (digitalRead(BUTTON_PIN) == HIGH) {
    double avgLat, avgLng;
    getAverageCoordinates(avgLat, avgLng);
    Serial.print("avg got the gps:");
    Serial.print("Lat: ");
    Serial.print(avgLat, 8);
    Serial.print(", Lng: ");
    Serial.println(avgLng, 8);
    delay(1000); // Add a delay to debounce the button
  }
}
