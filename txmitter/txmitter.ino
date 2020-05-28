
#define SYNC_PATTERN_LEN 11
uint8_t PATTERN_SYNC[SYNC_PATTERN_LEN] = {1,1,1,0,  0,0,1, 0,0,1, 0};
#define BIT_PATTERN_LEN 6
uint8_t PATTERN_BIT0[BIT_PATTERN_LEN] = {0,0,1,0,1,1};
uint8_t PATTERN_BIT1[BIT_PATTERN_LEN] = {0,1,1,1,1,0};

#define _PRINTLN_SDS(prefix, num, suffix) \
  Serial.print(prefix); \
  Serial.print(num, DEC); \
  Serial.println(suffix);

uint8_t* msg = (uint8_t*) "Hello, world!";
#define MSG_LEN 13
int syncPattern = 0;
int bitPattern = 0;
uint16_t datai = 0;

void debugVal(uint8_t val) {
  digitalWrite(3, (val & 0x01) ? HIGH : LOW);
  digitalWrite(4, (val & 0x02) ? HIGH : LOW);
}    

void setup() {
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);

  Serial.begin(9600);
  Serial.println("CSE 490W Final Project transmitter v51. Msg on next line.");
  Serial.println((char*) msg);
}

int calls = 0;
void delay1ms() {
  static unsigned long clock = 0;
  clock = micros() + 1000UL;
  while (micros() < clock);
  calls++;
}

void loop() {
  static int debug = 0;
  static unsigned long t1 = 0, t2 = 0, t3 = 0, t4 = 0;
  
  if (syncPattern < SYNC_PATTERN_LEN) { // Do sync pattern
    if (debug == 0) {
      t1 = millis();
      debug++;
    } else if (debug == 3) {
      t4 = millis();
      _PRINTLN_SDS("Started sync @", t1, "ms");
      _PRINTLN_SDS("Started data @", t2, "ms");
      _PRINTLN_SDS("Finished data @", t3, "ms");
      _PRINTLN_SDS("Started next sync @", t4, "ms");
      _PRINTLN_SDS("Called delay1ms() ", calls, " times");
      debug++;
    }
    debugVal(1);

    digitalWrite(2, PATTERN_SYNC[syncPattern] ? HIGH : LOW); // sync pattern

    syncPattern++;
  } else { // Do data after sync pattern
    if (debug == 1) {
      t2 = millis();
      debug++;
    }
    debugVal(0);

    // datai = {13'byteIndex, 3'bitIndex}
    char dataByte = msg[datai >> 3];
    char dataBitMask = 1 << (datai & 0x0007); // 1 << 3'bitIndex

    if (dataByte & dataBitMask) { // bit '1' pattern
      digitalWrite(2, PATTERN_BIT1[bitPattern] ? HIGH : LOW);
    } else { // bit '0' pattern
      digitalWrite(2, PATTERN_BIT0[bitPattern] ? HIGH : LOW);
    }

    bitPattern++;
    if (bitPattern == BIT_PATTERN_LEN) {
      bitPattern = 0;
      datai++;
    }
    if (datai >= (MSG_LEN << 3)) { // if datai > bytes2bits(MSG_LEN)
      if (debug == 2) {
	t3 = millis();
	debug++;
      }
      
      datai = 0;
      syncPattern = 0;
    }
  }
  
  delay1ms();
}
