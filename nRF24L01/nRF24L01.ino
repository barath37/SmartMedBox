#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define CE_PIN 10
#define CSN_PIN 9

RF24 radio(CE_PIN, CSN_PIN);
const byte address[6] = "00001";
int data;

void setup() {
  SPI.begin();
  Serial.begin(9600);
  delay(1000);

  if (!radio.begin()) {
    Serial.println("❌ radio.begin() failed – check power, wiring");
    while (1);
  }

  if (!radio.isChipConnected()) {


    Serial.println("❌ NRF24 module not detected – SPI problem");
    while (1);
  }

  radio.setPALevel(RF24_PA_LOW); // Start with LOW — PA_MAX often too noisy without filtering
  radio.setDataRate(RF24_250KBPS); // More stable at long range
  radio.setChannel(76);
  radio.setRetries(3, 5);
  radio.openWritingPipe(address);
  radio.stopListening();

  Serial.println("✅ Transmitter Ready");
}

void loop() {
  data = 1;
  bool sent1 = radio.write(&data, sizeof(data));
  Serial.print("Sent 1: ");
  Serial.println(sent1 ? "✅ Success" : "❌ Fail");
  delay(1000);

  data = 0;
  bool sent0 = radio.write(&data, sizeof(data));
  Serial.print("Sent 0: ");
  Serial.println(sent0 ? "✅ Success" : "❌ Fail");
  delay(1000);
}
/*
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define CE_PIN 10
#define CSN_PIN 9

RF24 radio(CE_PIN, CSN_PIN);
const byte address[6] = "00001";
int data;

void setup() {
  Serial.begin(9600);
  delay(1000);

  if (!radio.begin()) {
    Serial.println("❌ radio.begin() failed – check power, wiring");
    while (1);
  }

  if (!radio.isChipConnected()) {
    Serial.println("❌ NRF24 module not detected – SPI problem");
    while (1);
  }

  radio.setPALevel(RF24_PA_LOW);         // Match transmitter
  radio.setDataRate(RF24_250KBPS);       // Match transmitter
  radio.setChannel(76);                  // Must match
  radio.setRetries(3, 5);                // Accept retransmissions

  radio.openReadingPipe(0, address);
  radio.startListening();

  Serial.println("✅ Receiver Ready");
}

void loop() {
  if (radio.available()) {
    radio.read(&data, sizeof(data));
    Serial.print("📡 Received: ");
    Serial.println(data);
  }
}
*/
