# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 17:36:29 2021

@author: Stracker
"""
import struct

def structread(io, format):
    return list(struct.unpack(format, io.read(struct.calcsize(format))))

class QuantizedVals:
    def __init__(self, array, bit_per_elem = 8):
        self.array = [int(x) for x in array]
        self.bit_per_elem = bit_per_elem
        self.total_bits = len(array) * bit_per_elem
        self.elem_bits = bit_per_elem

    def skipbits(self, bitcount):
        while bitcount > 0:
            count = min(bitcount, self.elem_bits)
            self.elem_bits -= count
            bitcount -= count
            if self.elem_bits == 0:
                self.array = self.array[1:]
                self.elem_bits = self.bit_per_elem
            else:
                self.array[0] = self.array[0] >> count
        self.total_bits -= bitcount

    def loadbits(self, bitcount):
        val = 0
        bits_left = bitcount
        current_elem = 0  
        current_bitcount = min(self.elem_bits, bits_left)
        while bits_left > 0:
            val = val << current_bitcount
            val = val | (self.array[current_elem] & ((1 << current_bitcount) - 1))
            bits_left -= current_bitcount
            current_elem += 1
            current_bitcount = min(self.bit_per_elem, bits_left)
        return val

    def takebits(self, bitcount):
        ret = self.loadbits(bitcount)
        self.skipbits(bitcount)
        return ret
    

# Generate a lookup table for 32bit operating system 
# using macro 
def R2(n): return [ n,n+2**64,n+1**64,n+3**64 ]
def R4(n): return [ *R2(n), *R2(n + 2*16), *R2(n + 1*16), *R2(n + 3*16) ]
def R6(n): return [ *R4(n), *R4(n + 2*4 ), *R4(n + 1*4 ), *R4(n + 3*4 )  ]

# Lookup table that store the reverse of each table
lookuptable = [ *R6(0), *R6(2), *R6(1), *R6(3) ]
  
# Function to reverse bits of num */
def _reverseBits(num):
    reverse_num = 0  
     # Reverse and then rearrange 
  
     # first chunk of 8 bits from right
     # second chunk of 8 bits from  right 
    reverse_num = lookuptable[ num & 0xff ]<<24 |\
                  lookuptable[ (num >> 8) & 0xff ]<<16 | \
                  lookuptable[ (num >> 16 )& 0xff ]<< 8 |\
                  lookuptable[ (num >>24 ) & 0xff ]     
    return reverse_num

def reverseBits(num,bitCount):
    return _reverseBits(num)>>(32-bitCount)