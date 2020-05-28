#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import struct, time, os

FILE = '/tmp/data.bin'

t1 = time.time()
#numFloats = int(os.stat(FILE).st_size / 4)
#vals = np.zeros(numFloats, dtype=np.float32)
f = open(FILE, 'rb')
a = f.read()
f.close()
t2 = time.time()

numFloats = int(len(a) / 4)
vals = np.zeros(numFloats, dtype=np.float32)
for i in range(numFloats):
    vals[i] = struct.unpack('<f', a[i*4:(i + 1)*4])[0]
t3 = time.time()
print('%.03f to open, %.03f to decode' % (t2-t1, t3-t2))
quit()
#plt.stem(vals[:100])
#plt.tight_layout()
#plt.show()

STATE_SYNC = 0
STATE_DATA = 1
PATTERN_SYNC = [0,0,0,0, 1,1,1,1, 0,0,0,0]
PATTERN_BIT_0 = [1, 0, 1, 0]
PATTERN_BIT_1 = [1, 1, 0, 0]
PATTERN_BIT_END = [1, 1, 1, 1]
lens = [len(PATTERN_BIT_0), len(PATTERN_BIT_1), len(PATTERN_BIT_END)]
assert(min(lens) == max(lens))

def normalize(sig):
    '''Normalize a signal and return it'''
    norm = np.sqrt(np.sum(sig * sig))
    return sig / norm
class DataProccessor:
    def patternToSignal(self, pattern):
        protoSignal = []
        for bit in pattern:
            if bit == 0:
                bit = -1
            protoSignal += [bit] * self.bitSampleWidth
        return normalize(np.array(protoSignal, dtype=np.float32))
    def __init__(self, samp_rate=64e3, sync_threshold=0.1, bit_period=1e-3):
        self.bitSampleWidth = int(bit_period * samp_rate)
#        self.sampleRate = 
        self.thresh = sync_threshold
        self.state = STATE_SYNC
#        self.bitPeriod = 
        self.decodeBufferSync = np.zeros(self.bitSampleWidth * len(PATTERN_SYNC), dtype=np.float32)
        self.decodeBufferBit = np.zeros(self.bitSampleWidth * len(PATTERN_BIT_0), dtype=np.float32)
        self.bufferIndex = 0

        self.pulseSync = self.patternToSignal(PATTERN_SYNC)
        self.pulseBit0 = self.patternToSignal(PATTERN_BIT_0)
        self.pulseBit1 = self.patternToSignal(PATTERN_BIT_1)
        self.pulseDesync = self.patternToSignal(PATTERN_BIT_END)
        
        self.message = ''
        self.nextPrint = 0
        self.debug = True

    def doMessage(self):
        now = time.time()
        print('msgDecoded', self.message)
        if now > self.nextPrint:
            print(self.message)
            self.nextPrint = now + 1
        self.message = ''
    def doSyncState(self, data):
        needed = len(self.decodeBufferSync) - self.bufferIndex
        usage = min(len(data), needed)
        for i in range(usage):
            self.decodeBufferSync[self.bufferIndex] = data[i]
            self.bufferIndex += 1
        assert(self.bufferIndex <= len(self.decodeBufferSync))
        while self.bufferIndex >= len(self.decodeBufferSync):
            # the buffer is full, compute on it
            # Pattern is already normalized, signal is not
            correlation = np.abs(np.dot(normalize(self.decodeBufferSync), self.pulseSync))
            if correlation > self.thresh:
                print('Sync!')
                self.bufferIndex = 0
                self.state = STATE_DATA
                return usage # found sync, return to change state
            else:
                np.roll(self.decodeBufferSync, -1) # shift left by 1
                if usage < len(data): # roll in another sample and try correlating again
                    self.decodeBufferSync[-1] = data[usage]
                    usage += 1
                else: # out of data, return
                    self.bufferIndex -= 1
                    return usage
        assert(usage == len(data))
        return usage
    def doDataState(self, data):
        usage = 0
        while usage < len(data):
            self.decodeBufferBit[self.bufferIndex] = data[usage]
            self.bufferIndex += 1
            usage += 1
            if self.bufferIndex >= len(self.decodeBufferBit):
                # the buffer is full, compute on it
                signal = normalize(self.decodeBufferBit)
                corBit0 = np.abs(np.dot(self.pulseBit0, signal))
                corBit1 = np.abs(np.dot(self.pulseBit1, signal))
                corEnd = np.abs(np.dot(self.pulseDesync, signal))
                corMax = max(corBit0, corBit1, corEnd)
                
                if corEnd == corMax:
                    # finished message
                    self.state = STATE_SYNC
                    self.bufferIndex = 0
                    self.doMessage()
                    return usage
                
                if corBit0 == corMax:
                    self.message += '0'
                else:
                    self.message += '1'
                self.bufferIndex = 0
        return usage
        
    def work(self, input_items):
        dataUsed = 0
        while dataUsed < len(input_items):
            if self.state == STATE_SYNC:
                dataUsed += self.doSyncState(input_items[dataUsed:])
            elif self.state == STATE_DATA:
                dataUsed += self.doDataState(input_items[dataUsed:])

proc = DataProccessor()

#plt.stem(np.arange(int(150e3)) / 64, vals[:int(150e3)]
plt.stem(vals[150:int(5e3)])
plt.xlabel('time (ms)')

plt.tight_layout()
plt.show()
