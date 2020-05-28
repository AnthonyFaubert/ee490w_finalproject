"""
Embedded Python Blocks:

Each this file is saved, GRC will instantiate the first class it finds to get
ports and parameters of your block. The arguments to __init__  will be the
parameters. All of them are required to have default values!
"""
import numpy as np
from gnuradio import gr
import time

STATE_SYNC = 0
STATE_DATA = 1

DTYPE = np.float32

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
class blk(gr.sync_block):
    def patternToSignal(self, pattern):
        protoSignal = []
        for bit in pattern:
            if bit == 0:
                bit = -1
            protoSignal += [bit] * self.bitSampleWidth
        return normalize(np.array(protoSignal, dtype=DTYPE))
    def __init__(self, samp_rate=64e3, sync_threshold=0.1, bit_period=1e-3):  # only default arguments here
        gr.sync_block.__init__(
            self,
            name='Message Decoder (Python)',
            in_sig=[DTYPE],
            out_sig=[]
        )
        self.bitSampleWidth = int(bit_period * samp_rate)
#        self.sampleRate = 
        self.thresh = sync_threshold
        self.state = STATE_SYNC
#        self.bitPeriod = 
        self.decodeBufferSync = np.zeros(self.bitSampleWidth * len(PATTERN_SYNC), dtype=DTYPE)
        self.decodeBufferBit = np.zeros(self.bitSampleWidth * len(PATTERN_BIT_0), dtype=DTYPE)
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
        print ('msgDecoded', self.message)
        if now > self.nextPrint:
            print (self.message)
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
                print 'Sync!'
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
        
    def work(self, input_items, output_items):
        return 0
        if self.debug:
            print ('#$#$ input data len', input_items[0], len(input_items[0]))
            self.debug = False
        dataUsed = 0
        while dataUsed < len(input_items[0]):
            if self.state == STATE_SYNC:
                dataUsed += self.doSyncState(input_items[0][dataUsed:])
            elif self.state == STATE_DATA:
                dataUsed += self.doDataState(input_items[0][dataUsed:])
        return 0
        #output_items[0][:] = input_items[0]
        #return len(output_items[0])
