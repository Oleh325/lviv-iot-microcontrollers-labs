#include <Arduino.h>
#include <DHT22.h>

#define SLAVE_ADDRESS 0x57
#define pinDATA 9

DHT22 dht22(pinDATA); 

byte address;
int v = 0;

void writeData();
char crc8(const char *data,int length);

void setWriteModeRS485() {
  PORTD |= 1 << PD2;
  delay(1);
}

// переривання по завершенню передачі
ISR(USART_TX_vect) {
  PORTD &= ~(1 << PD2); 
}

void setup() {
  delay(1000);
  DDRD = 0b00000111;
  PORTD = 0b11111000;

  Serial.begin(4800, SERIAL_8N1);
  UCSR0B |= (1 << UCSZ02) | (1 << TXCIE0);
  UCSR0A |= (1 << MPCM0);

  delay(1);

}

void loop() {
  if (Serial.available()) {
    byte inByte = Serial.read();
    if (SLAVE_ADDRESS == inByte) {
      UCSR0A &= ~(1 << MPCM0);
      setWriteModeRS485();
      writeData();
      delay(200);
    } 
  }
}


void writeData()
{
  byte byteData[40];
  String data = "Temperature: ";
  if (dht22.getLastError() != dht22.OK) { return 0; }
  data.concat(dht22.getTemperature());
  data.concat(", Humidity: ");
  data.concat(dht22.getHumidity());
  data.getBytes(byteData, 40);
  
  byte encryptedByteData[42];
  for (int i = 0; i < 40; i++) {
    encryptedByteData[i] = byteData[i];
  }

  unsigned short checkSumCRC = crc8(byteData, sizeof(byteData));
  byte firstByteOfCheckSum = (checkSumCRC >> 8) & 0xFF;
  byte secondByteOfCheckSum = checkSumCRC & 0xFF;
  encryptedByteData[40] = firstByteOfCheckSum;
  encryptedByteData[41] = secondByteOfCheckSum;

  for (unsigned int i = 0; i < sizeof(encryptedByteData); i++) {
    Serial.write(encryptedByteData[i]);         
  } 
    
  v++;
  if (v == 5) {
    v = 0;
  }
}

// імплементація CRC8
char crc8(const char *data, int length)
{
   char crc = 0x00;
   char extract;
   char sum;
   for(int i=0;i<length;i++)
   {
      extract = *data;
      for (char tempI = 8; tempI; tempI--) 
      {
         sum = (crc ^ extract) & 0x01;
         crc >>= 1;
         if (sum)
            crc ^= 0x8C;
         extract >>= 1;
      }
      data++;
   }
   return crc;
}