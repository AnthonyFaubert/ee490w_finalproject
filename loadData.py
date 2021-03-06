#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import struct, time, os, code

FILE = '/tmp/data.bin'
FLOATS_PER_CHUNK = 256
STRUCT = '<' + 'f'*FLOATS_PER_CHUNK
SAMPLE_RATE = 128e3
BIT_PERIOD = 165e-6
SYNC_THRESHOLD = 0.9
SLIP = 8
# all on a file with ~51,249,152 floats
# old does ~17.5s to load
# single float per loop cycle takes ~16.7s
# 4 floats per loop cycle takes ~13.5s
# 64 floats per loop cycle takes ~2.4s
# 1024 floats per loop cycle takes ~1.9s
# 256 takes ~2.0s
t1 = time.time()
numChunks = int(os.stat(FILE).st_size / 4 / FLOATS_PER_CHUNK)
numFloats = numChunks * FLOATS_PER_CHUNK
vals = np.zeros(numFloats, dtype=np.float32)
f = open(FILE, 'rb')
for i in range(0, numFloats, FLOATS_PER_CHUNK):
    vals[i:i+FLOATS_PER_CHUNK] = struct.unpack(STRUCT, f.read(4 * FLOATS_PER_CHUNK))
f.close()
t2 = time.time()
print('%.03f to decode %d floats' % (t2-t1, numFloats))

STATE_SYNC = 0
STATE_DATA = 1
PATTERN_BIT_0 = [0, 0, 1, 0, 1, 1]
PATTERN_BIT_1 = [0, 1, 1, 1, 1, 0]
PATTERN_SYNC = [1,1,1,0, 0,0,1, 0,0,1, 0] # 11-bit Barker code
PATTERN_BIT_END = PATTERN_SYNC[:len(PATTERN_BIT_0)]
#0001,0010,0100,0111 are good patterns
lens = [len(PATTERN_BIT_0), len(PATTERN_BIT_1), len(PATTERN_BIT_END)]
assert(min(lens) == max(lens))

def crc16(bs):
    crc = 0
    for b in bs:
        crc ^= b
        for i in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc = crc >> 1
    return crc

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
            protoSignal += [bit] * self.bitLen
        return normalize(np.array(protoSignal, dtype=np.float32))
    def __init__(self, data):
        self.bitLen = int(BIT_PERIOD * SAMPLE_RATE)
        self.thresh = SYNC_THRESHOLD
        self.state = STATE_SYNC

        self.dataIndex = 0
        self.data = data
        #plt.plot(self.data[:20000:10]); plt.show(); quit()

        self.pulseSync = self.patternToSignal(PATTERN_SYNC)
        self.syncLen = len(self.pulseSync)
        self.pulseBit0 = self.patternToSignal(PATTERN_BIT_0)
        self.bitSymbolLen = len(self.pulseBit0)
        self.pulseBit1 = self.patternToSignal(PATTERN_BIT_1)
        self.pulseDesync = self.patternToSignal(PATTERN_BIT_END)
        
        self.message = ''
        self.nextPrint = 0
        self.debug = True
        self.sdbg_mc = 0
        self.messageCount = 0
        self.messageCountGood = 0

    def messageReadByte(self):
        if len(self.message) < 8:
            return b''
        b = 0
        for i in range(8):
            b |= int(self.message[i]) << i
        self.message = self.message[8:]
        return bytes([b])
    def doMessage(self):
        now = time.time()
        rawMsg = self.message
        bs = b''
        while True:
            b = self.messageReadByte()
            if len(b) == 0:
                break
            bs += b
        crcGood = False
        if len(bs) > 2:
            crcActual = crc16(bs[:-2])
            crcExpected = (bs[-2] << 8) | bs[-1]
            if crcActual == crcExpected:
                crcGood = True
            else:
                print("CRCs don't match!", crcActual, crcExpected)
        if crcGood:
            print('Good message:', bs[:-2])
            self.messageCountGood += 1
        else:
            print('Bad message:', bs)
            if len(self.message) > 0:
                print('Raw message:', rawMsg)
                print('Orphan bits:', self.message)
        self.message = ''
        self.messageCount += 1
        
    def dataLeft(self):
        return len(self.data) - self.dataIndex
    def dataWindow(self):
        if self.state == STATE_SYNC:
            sigLen = self.syncLen
        elif self.state == STATE_DATA:
            sigLen = self.bitSymbolLen
        window = self.data[self.dataIndex:self.dataIndex+sigLen]
        return normalize(window - np.average(window))

    def doSyncState(self):
        while self.dataLeft() > self.syncLen:
            correlation = np.abs(np.dot(self.dataWindow(), self.pulseSync))
            if correlation > self.sdbg_mc:
                self.sdbg_mc = correlation
                self.sdbg_i = self.dataIndex
            if correlation > self.thresh:
                if self.debug:
                    plt.plot(self.dataWindow());plt.plot(self.pulseSync);plt.title('Sync threshold');plt.show()
                    print('Sync detected. Finding best sync...')
                while True:
                    self.dataIndex += 1
                    correlation2 = np.abs(np.dot(self.dataWindow(), self.pulseSync))
                    if correlation2 > correlation:
                        correlation = correlation2
                    else:
                        self.dataIndex -= 1
                        if self.debug:
                            plt.plot(self.dataWindow());plt.plot(self.pulseSync);plt.title('Best sync');plt.show()
                        self.dataIndex += self.syncLen
                        self.state = STATE_DATA
                        return False # not out of data
            else:
                self.dataIndex += 1
        return True # out of data

    def doDataState(self):
        while self.dataLeft() > self.bitSymbolLen:
            signal = self.dataWindow()
            corBit0 = np.abs(np.dot(self.pulseBit0, signal))
            corBit1 = np.abs(np.dot(self.pulseBit1, signal))
            corEnd = np.abs(np.dot(self.pulseDesync, signal))
            corMax = max(corBit0, corBit1, corEnd)

            if corEnd == corMax:
                if self.debug:
                    plt.plot(self.dataWindow());plt.plot(self.pulseDesync);plt.title('Desync');plt.show()
                    self.debug = False
                #di = self.dataIndex
                #bl = self.bitLen
                #plt.plot(self.data[di-bl*20:di+len(self.pulseDesync)+bl*5])
                #plt.plot(np.concatenate([np.zeros(bl*20), self.pulseDesync, np.zeros(bl*5)]))
                #plt.show(); quit()
                #code.interact(local=dict(globals(), **locals()))
                # finished message
                self.state = STATE_SYNC
                self.doMessage()
                return False # not out of data
            
            if corBit0 == corMax:
                self.message += '0'
                pulse = self.pulseBit0
            else:
                self.message += '1'
                pulse = self.pulseBit1
            # Go SLIP samples to the left and right searching for the best match for this bit
            bestCor = -1
            bestIndex = -1
            # FIXME: never checked to see if we have enough data to slip forward
            for i in range(self.dataIndex - SLIP, self.dataIndex + SLIP +1):
                self.dataIndex = i
                cor = np.abs(np.dot(self.dataWindow(), pulse))
                if cor > bestCor:
                    bestCor = cor
                    bestIndex = i
            self.dataIndex = bestIndex + self.bitSymbolLen
        return True # out of data
        
    def work(self):
        outOfData = False
        while not outOfData:
            if self.state == STATE_SYNC:
                outOfData = self.doSyncState()
            elif self.state == STATE_DATA:
                outOfData = self.doDataState()
        print('Decoded %d messages, of which %d were good.' % (self.messageCount, self.messageCountGood))
        #self.dataIndex = self.sdbg_i
        #self.state = STATE_SYNC
        #win = self.dataWindow()
        #print(np.dot(win, win))
        #plt.plot(win); plt.show()
        #code.interact(local=dict(globals(), **locals()))
        
            

proc = DataProccessor(vals)
proc.work()
quit()

# sync = 3*4ms/bit = 12ms
# data = 13bytes * 8bits/byte * 4ms/bit
# end = 1 * 4ms/bit
# total 432ms: ~27.6k samples @ 64kHz
maxI = int(28e3)
step = 16
ms = np.linspace(0, maxI / 64.0, maxI * 1.0 / step)
Y = vals[:maxI:step]
yfill = 0.0
plt.plot(ms, Y)
plt.fill_between(ms, Y, y2=yfill, color='blue', alpha=0.4)
plt.xlabel('time (ms)')
plt.title('Initial chunk of raw data')
plt.tight_layout()

plt.figure()
Z = np.zeros(len(Y))
Z[np.where(Y > 0.5)] = 1
plt.plot(ms, Z)
plt.fill_between(ms, Z, y2=0, color='r', alpha=0.3)
plt.xlabel('time (ms)')
plt.ylim([-0.05, 1.05])
plt.title('Thresholded data')
plt.tight_layout()

plt.show()

#code.interact(local=dict(globals(), **locals()))
