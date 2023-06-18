#include <Arduino.h>

#define SLAVE_ADDRESS 0x57

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
  byte byteMessage[24]; 
  String message = "Yatskiv Oleh Olehovych\0";
  message.getBytes(byteMessage, 24);
  
  byte encryptedByteMessage[26];
  for (int i = 0; i < 24; i++) {
    encryptedByteMessage[i] = byteMessage[i];
  }

  for(int k = 0; k < 5; k++) {
    if (v == k) {
      for (unsigned int i = 0; i < sizeof(encryptedByteMessage); i++) {
        if (k == 1 && i == 0) {
          encryptedByteMessage[i] ^= (1 << 2);
        } else if (k == 4 && i == 8) {
          encryptedByteMessage[i] ^= ((1 << 1) | (1 << 2) | (1 << 6));
        }        
      }   
    }
  }

  byte byteMessageModified[24];
  for (int i = 0; i < 24; i++) {
    byteMessageModified[i] = encryptedByteMessage[i];
  }

  unsigned short checkSumCRC = crc8(byteMessageModified, sizeof(byteMessageModified));
  byte firstByteOfCheckSum = (checkSumCRC >> 8) & 0xFF;
  byte secondByteOfCheckSum = checkSumCRC & 0xFF;
  encryptedByteMessage[24] = firstByteOfCheckSum;
  encryptedByteMessage[25] = secondByteOfCheckSum;

  for (unsigned int i = 0; i < sizeof(encryptedByteMessage); i++) {
    Serial.write(encryptedByteMessage[i]);         
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