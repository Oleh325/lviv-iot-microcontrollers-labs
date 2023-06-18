const int buzzerPin = 37;

unsigned char number[10]  = {0xc0, 0xf9, 0xa4, 0xb0, 0x99, 0x92, 0x82, 0xf8, 0x80, 0x90};
unsigned char bcd_time[6] = {number[0], number[0], number[0], number[0], number[0], number[0]};
unsigned char alarm_time[6] = {number[0], number[0], number[0], number[0], number[0], number[0]};
unsigned char portd_positions[6] = {0b00000010, 0b00000100, 0b00001000, 0b00010000, 0b00100000, 0b01000000};

struct Time
{
  unsigned char second, minute, hour;
};
Time T2 = {0, 0, 0};
Time Alarm = {0, 0, 0};

unsigned char fig_number = 0;
bool clock_mode = true;
bool alarm_state = false;

void bcd(unsigned char number, unsigned char position);

ISR(TIMER2_COMPA_vect) {
  if (++T2.second == 60) {
    T2.second = 0;
    if (++T2.minute == 60) {
      T2.minute = 0;
      if (++T2.hour == 24)
        T2.hour = 0;
      bcd(T2.hour, 0);
    }
    bcd(T2.minute, 2);
  }
  bcd(T2.second, 4);
}

ISR(TIMER0_COMPA_vect) {
  fig_number++;
  if (fig_number == 6) {
    fig_number = 0;
  }
   
  PORTD = portd_positions[fig_number];
  if (clock_mode) {
    if (fig_number == 1 || fig_number == 3) {
      PORTA = bcd_time[fig_number] & ~0x80;
    } else {
      PORTA = bcd_time[fig_number];
    }
  } else {
    if (fig_number == 1 || fig_number == 3) {
      PORTA = alarm_time[fig_number] & ~0x80;
    } else {
      PORTA = alarm_time[fig_number];
    }
  }
  if (alarm_state) {
    if (T2.hour == Alarm.hour && T2.minute == Alarm.minute && T2.second == Alarm.second) {
      digitalWrite(buzzerPin, HIGH);    
    }
  }
  if (alarm_state && !clock_mode) {
    if (PORTD == 0b01000000) {
      PORTA = 0x88;
    }
  }
  Time end = {0, 0, 0};
  end.second = Alarm.second + 30;
  if (end.second > 59) {
    end.second -= 60;
    end.minute += 1;
  }
  end.minute += Alarm.minute;
  if (end.minute > 59) {
    end.minute -= 60;
    end.hour += 1;
  }
  end.hour += Alarm.hour;
  if (end.hour > 23) {
    end.hour -= 24;
  }
  if (T2.hour == end.hour && T2.minute == end.minute && T2.second == end.second) {
    digitalWrite(buzzerPin, LOW);
  }
}

void setup() {
  noInterrupts();

	DDRD = 0xFF;
	PORTD = 0xFF;    

	DDRA = 0xFF;
	PORTA = 0xFF; 

	DDRB = 0x00; 
	PORTB = 0xFF;

  TCNT0 = 0;
  OCR0A = 25;
  TCCR0A = (1 << WGM01);
  TCCR0B = (1 << CS02) | (1 << CS00);
  TIMSK0 |= (1 << OCIE0A);
  
  TIMSK2 = (0 << OCIE2A) | (0 << OCIE2B) | (0 << TOIE2); 
  ASSR |= 1 << AS2;
  TCNT2 = 0;
  TCCR2A = (1<<COM2A0) | (1<<WGM21);
  TCCR2B = (1<<CS22) | (1<<CS21) | (1<<CS20);
  OCR2A = 32;
  while ((ASSR & ((1 << OCR2AUB) | (1 << OCR2BUB) | (1 << TCR2AUB) | (1 << TCR2BUB) | (1<< TCN2UB))));
  TIFR2 = (1 << TOV2) | (1 << OCF2A) | (1 << OCF2B);
  TIMSK2 = (1 << OCIE2A);

  interrupts();

  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);
}

void loop() {
  if (clock_mode) {
    if((PINB&(1<<0))==0) { // increment hours
      if (++T2.hour == 24) T2.hour = 0;
      bcd(T2.hour, 0);

      delay(100000);
    }

    if((PINB&(1<<1))==0) { // increment minutes
      if (++T2.minute == 60) T2.minute = 0;
      bcd(T2.minute, 2);

      delay(100000);
    }
  } else {
    if((PINB&(1<<0))==0) { // increment hours
      if (++Alarm.hour == 24) Alarm.hour = 0;
      alarm(Alarm.hour, 0);

      delay(100000);
    }

    if((PINB&(1<<1))==0) { // increment minutes
      if (++Alarm.minute == 60) Alarm.minute = 0;
      alarm(Alarm.minute, 2);

      delay(100000);
    }    
  }

  if((PINB&(1<<2))==0) { // change mode
    clock_mode = !clock_mode;
    delay(100000);
  }

  if((PINB&(1<<3))==0) { // toggle alarm state
    alarm_state = !alarm_state;
    delay(100000);
  }
}

void bcd(unsigned char fig_in, unsigned char position) { 
  unsigned char bcdL = fig_in;
  unsigned char bcdH = 0;
  while (bcdL >= 10) {
    bcdL -= 10;
    bcdH++;
  }
  bcd_time[position] = number[bcdH];
  bcd_time[position + 1] = number[bcdL];
}

void alarm(unsigned char fig_in, unsigned char position) { 
  unsigned char bcdL = fig_in;
  unsigned char bcdH = 0;
  while (bcdL >= 10) {
    bcdL -= 10;
    bcdH++;
  }
  alarm_time[position] = number[bcdH];
  alarm_time[position + 1] = number[bcdL];
}
