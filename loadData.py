#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
import struct, time, os, code

FILE = '/tmp/data.bin'
FLOATS_PER_CHUNK = 256
STRUCT = '<' + 'f'*FLOATS_PER_CHUNK
SAMPLE_RATE = 64e3
BIT_PERIOD = 1e-3
SYNC_THRESHOLD = 0.5
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
    def __init__(self, data, samp_rate=64e3, sync_threshold=0.02815, bit_period=1e-3):
        self.bitLen = int(bit_period * samp_rate)
        self.thresh = sync_threshold
        self.state = STATE_SYNC

        self.dataIndex = 0
        # Remap data points (should be DC balanced already)
        #data = data[180:] # there's some averaging filter initial value crap from [0:162] or so. Skip it
        # new filter initial crap is like 400*20. Might as well just throw away the first 0.5 seconds
        self.data = data[int(samp_rate/2):]
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

    def doMessage(self):
        now = time.time()
        print('msgDecoded', self.message)
        if now > self.nextPrint:
            print(self.message)
            self.nextPrint = now + 1
        self.message = ''
        
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
                print('Sync detected. Finding best sync...')
                while True:
                    self.dataIndex += 1
                    correlation2 = np.abs(np.dot(self.dataWindow(), self.pulseSync))
                    if correlation2 > correlation:
                        correlation = correlation2
                    else:
                        self.dataIndex += self.syncLen - 1
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
            if len(self.message) == 104:
                code.interact(local=dict(globals(), **locals()))
            
            if corEnd == corMax:
                plt.plot(self.dataWindow()); plt.show()
                # finished message
                self.state = STATE_SYNC
                self.doMessage()
                return False # not out of data
            
            if corBit0 == corMax:
                self.message += '0'
            else:
                self.message += '1'
            self.dataIndex += self.bitSymbolLen
        return True # out of data
        
    def work(self):
        outOfData = False
        while not outOfData:
            if self.state == STATE_SYNC:
                outOfData = self.doSyncState()
            elif self.state == STATE_DATA:
                outOfData = self.doDataState()
        self.dataIndex = self.sdbg_i
        self.state = STATE_SYNC
        win = self.dataWindow()
        print(np.dot(win, win))
        plt.plot(win); plt.show()
        code.interact(local=dict(globals(), **locals()))
        
            

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
yfill = -0.5
plt.plot(ms, Y)
plt.fill_between(ms, Y, y2=yfill, color='blue', alpha=0.4)
plt.xlabel('time (ms)')
plt.title('Initial chunk of raw data')
plt.tight_layout()

plt.figure()
Z = np.zeros(len(Y))
Z[np.where(Y > -0.4)] = 1
plt.plot(ms, Z)
plt.fill_between(ms, Z, y2=0, color='r', alpha=0.3)
plt.xlabel('time (ms)')
plt.ylim([-0.05, 1.05])
plt.title('Thresholded data')
plt.tight_layout()

plt.show()

#code.interact(local=dict(globals(), **locals()))
