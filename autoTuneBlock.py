"""
Embedded Python Blocks:

Each this file is saved, GRC will instantiate the first class it finds to get
ports and parameters of your block. The arguments to __init__  will be the
parameters. All of them are required to have default values!
"""
import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self, fft_size=1024, sample_rate=64e3):  # only default arguments here
        gr.sync_block.__init__(
            self,
            name='Embedded Python Block',
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )
        self.fftBuffer = np.zeros(fft_size, dtype=np.complex64)
        self.fftBufferI = 0
        self.fftBufferLen = fft_size
        self.sampleRate = sample_rate
        self.bestFreq = np.complex64(-1)

    def work(self, input_items, output_items):
        return 0
        '''
        self.fftBuffer[self.fftBufferI] = input_items[0]
        self.fftBufferI += 1
        if self.fftBufferI >= self.fftBufferLen:
            self.fftBufferI = 0
            self.bestFreq = self.fftBuffer[0] # TODO: compute new 
        #assert(len(input_items) == 1024)
        return self.bestFreq
'''
#        output_items[0][:] = input_items[0] * self.factor
#        return len(output_items[0])
