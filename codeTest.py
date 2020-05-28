#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
#import struct, time, os, code

norm = lambda sig: sig / np.sqrt(np.sum(sig * sig))
def correlate(a, b):
    return np.abs(np.dot(norm(a), norm(b)))

def code(v, leng):
    c = np.zeros(leng)
    for i in range(leng):
        if 1 == (v >> (leng-i-1))&1:
            c[i] = 1
        else:
            c[i] = -1
    return c
def printCode(code):
    s = ''
    for v in code:
        if v == 1:
            s += '1'
        else:
            s += '0'
    print(s, end='')

z = 0x38
nz = 0x07
codeLen = 6
for i in range(2**(codeLen-1)):
    for j in range(2**(codeLen-1)):
        if (i == j) or (i == nz) or (j == nz):
            continue
        a = code(z, codeLen)
        b = code(i, codeLen)
        c = code(j, codeLen)
        cor = max(correlate(a, b), correlate(b, c), correlate(a, c))
        if cor < 0.666:
            printCode(b); print(' ', end=''); printCode(c)
            print(' -', cor)
        
quit()
maxSnr = -1
codeLen = 11
for i in range(2**(codeLen-1)):
#codeLen = 11
#for i in range(0xe00 >> 1, 0xfff >> 1, 2):
    cors = np.zeros(codeLen)
    c = code(i, codeLen)
    for j in range(codeLen):
        cors[j] = correlate(c, np.roll(c, j))
    printCode(c)
    if np.max(cors[1:]) == 0:
        print(' - inf')
        maxSnr = 'inf'
    else:
        snr = cors[0] / np.max(cors[1:])
        if (maxSnr != 'inf') and (snr > maxSnr):
            maxSnr = snr
        print(' -', snr)
print('Best SNR:', maxSnr)
