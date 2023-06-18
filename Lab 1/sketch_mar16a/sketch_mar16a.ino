const unsigned int delayInMs = 1150;
const unsigned char buttonPin = 32;
const int states[] = {0b10000000, 0b00000001, 0b01000000, 0b00000010, 0b00100000, 0b00000100, 0b00010000, 0b00001000};

void setup() {
  DDRA = 0xFF;
  PORTA = 0;
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
  if(digitalRead(buttonPin) == LOW) {
    for(int i = 0; i < 8; i++){
      PORTA = states[i];
      delay(delayInMs);
    }
    PORTA = 0;
  }
}