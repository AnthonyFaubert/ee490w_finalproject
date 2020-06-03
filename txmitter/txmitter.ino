
#include <util/crc16.h>

#define SYNC_PATTERN_LEN 11
uint8_t PATTERN_SYNC[SYNC_PATTERN_LEN] = {1,1,1,0,  0,0,1, 0,0,1, 0};
#define BIT_PATTERN_LEN 6
uint8_t PATTERN_BIT0[BIT_PATTERN_LEN] = {0,0,1,0,1,1};
uint8_t PATTERN_BIT1[BIT_PATTERN_LEN] = {0,1,1,1,1,0};

#define _PRINTLN_SDS(prefix, num, suffix) \
  Serial.print(prefix); \
  Serial.print(num, DEC); \
  Serial.println(suffix);

#define DEFAULT_MSG "Hello, world!"
uint8_t msg[256];
uint8_t msgLen = 13;
int syncPattern = 0;
int bitPattern = 0;
uint16_t datai = 0;

void debugVal(uint8_t val) {
  digitalWrite(3, (val & 0x01) ? HIGH : LOW);
  digitalWrite(4, (val & 0x02) ? HIGH : LOW);
}

void setMsg(char* str) {
  uint16_t crc = 0;
  msgLen = 0;
  for (uint8_t i = 0; str[i] != 0; i++) {
    crc = _crc16_update(crc, str[i]);
    msg[i] = str[i];
    msgLen++;
  }
  msg[msgLen++] = (uint8_t) ((crc & 0xFF00) >> 8);
  msg[msgLen++] = (uint8_t) (crc & 0x00FF);
}

void setup() {
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);

  setMsg(DEFAULT_MSG);
  
  Serial.begin(9600);
  Serial.println("CSE 490W Final Project transmitter v64. Msg on next line.");
  // Println(msg):
  for (uint8_t i = 0; i < msgLen; i++) Serial.print((char) msg[i]);
  Serial.println();
}

void loop() {
  static int debug = 0;
  static unsigned long t1 = 0, t2 = 0, t3 = 0, t4 = 0;
  static int loops = 0;

  static char nextMsg[256];
  static uint8_t nextMsgLen = 0;
  unsigned long timeout = micros() + 160UL;
  
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
      _PRINTLN_SDS("Looped ", loops, " times");
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
    if (datai >= ((uint16_t)msgLen << 3)) { // if datai > bytes2bits(MSG_LEN)
      if (debug == 2) {
	t3 = millis();
	debug++;
      }
      
      datai = 0;
      syncPattern = 0;
    }
  }

  while (micros() < timeout) { // delay for 1ms from start of function
    if (Serial.available() > 0) { // handle input
      char c = Serial.read();
      if (c == '\n') {
	nextMsg[nextMsgLen] = 0;
	setMsg((char*) nextMsg);
	nextMsgLen = 0;
	if (Serial.availableForWrite() > 4) Serial.println('ACK');
      } else {
	nextMsg[nextMsgLen++] = (uint8_t) c;
      }
    }
  }
  loops++;
}
