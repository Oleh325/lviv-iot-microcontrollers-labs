#include <Arduino.h>

bool isAddress = true;
bool isCommand = false;
byte command;

void setWriteModeRS485() {
  byte port = PORTD;
  PORTD |= 1 << PD1; // режим відправки
  delay(1);
}

// переривання при завершенні передачі
ISR(USART1_TX_vect)
{ 
  PORTD &= ~(1 << PD1); // режим прийому
}

void setup() {
  delay(1000);  
  
  // En_m - на вихід + низький рівень
  DDRD |= 1 << PD1;
  PORTD &= ~(1 << PD1);

  // initialize UART0 (RS-232)
  Serial.begin(4800);

  // initialize RS-485
  Serial1.begin(4800, SERIAL_8N1);
  Serial1.write("");
  UCSR1B |= (1 << UCSZ12) | (1 << TXCIE1);
}

void loop() {
  if (Serial.available()) { 
    byte inByte = Serial.read();
    if (isAddress) {
      setWriteModeRS485();
      UCSR1B |= 1 << TXB81;
      Serial1.write(inByte);
      isAddress = false;
      isCommand = true;
    } else if (isCommand) {
      command = inByte;
      isCommand = false;
      setWriteModeRS485();
      // після запису даних у буфер передачі необхідно
      // надати дозвіл на переривання для події спорожнення буфера UDR.
      UCSR1B &= ~(1 << TXB81); 
      Serial1.write(inByte);
      if (command == 0xB1) isAddress = true; // Команда читання 1 байту
    } else { // data byte
      isAddress = true;
      setWriteModeRS485();
      UCSR1B &= ~(1 << TXB81);
      Serial1.write(inByte);
    }
  }

  if (Serial1.available()) { // if we receive something from slaves, we also process it.
    byte inByte1 = Serial1.read();
    Serial.write(inByte1);
  }
}
