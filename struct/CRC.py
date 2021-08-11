# -*- coding: utf-8 -*-
"""
CRC32 taken from https://stackoverflow.com/questions/41564890/crc32-calculation-in-python-without-using-libraries
"""

import binascii
from array import array

poly = 0xEDB88320

table = array('L')
for byte in range(256):
    crc = 0
    for bit in range(8):
        if (byte ^ crc) & 1:
            crc = (crc >> 1) ^ poly
        else:
            crc >>= 1
        byte >>= 1
    table.append(crc)

def crc32(string):
    value = 0xffffffff
    for ch in string:
        value = table[(ord(ch) ^ value) & 0xff] ^ (value >> 8)
    return -1 - value

def jamcrc32(string):
    crc = crc32(string)
    jam = (int((crc^0xFFFFFFFF)) & 0xFFFFFFFF)
    return jam.to_bytes(4,"little")