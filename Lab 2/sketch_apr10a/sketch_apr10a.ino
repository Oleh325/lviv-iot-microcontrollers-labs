const unsigned int delayInMs = 400;
const unsigned char buttonPinAlgo1 = 65;
const unsigned char buttonPinAlgo2 = 66;
int inByte;
const int algo1_states[] = {0b00000001, 0b00000010, 0b00000100, 0b00001000, 0b00010000, 0b00100000, 0b01000000, 0b10000000};
const int algo2_states[] = {0b10000000, 0b00100000, 0b00001000, 0b00000010, 0b01000000, 0b00010000, 0b00000100, 0b00000001};

void setup()
{
  for(uint16_t i = 42; i < 50; i++)
  {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
  pinMode(buttonPinAlgo1, INPUT_PULLUP);
  pinMode(buttonPinAlgo2, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop()
{
  if (Serial.available() > 0)
  {
    inByte = Serial.read();
    if (inByte == 0xA1)
    {
      algorithm1();
    }
    else if (inByte == 0xA2)
    {
      algorithm2();
    }
  }
  if(digitalRead(buttonPinAlgo1) == LOW) {
    Serial.write(0xA1);
  }
  if(digitalRead(buttonPinAlgo2) == LOW) {
    Serial.write(0xA2);
  }
}

void algorithm1()
{
  for (uint16_t i = 41; i <= 50; i++)
  {
    if (i != 50)
    {
      digitalWrite(i, HIGH);      
    }
    if (i > 42)
    {
      digitalWrite(i-1, LOW);
    }
    delay(delayInMs);
  }
}

void algorithm2()
{
  for (uint16_t i = 49; i > 41; i -= 2)
  {
    digitalWrite(i, HIGH); 
    if (i < 48)
    {
      digitalWrite(i + 2, LOW);      
    }
    if (i == 48)
    { 
      digitalWrite(43, LOW);      
    }
    if (i == 43)
    {
      i = 50;
    }
    delay(delayInMs);
  }
  digitalWrite(42, LOW);
}