# -*- coding: utf-8 -*-
"""
Created on Sat Feb  9 00:55:14 2019

@author: AsteriskAmpersand
"""

class FileLike():
    def __init__(self, dataArray):
        self.i = 0
        self.data = dataArray
        
    def read(self, x=None):
        if x is None:
            data = self.data[self.i:]
            self.i = len(self.data)
            return data
        if self.i+x > len(self.data):
            raise IndexError("Reading out of Bounds at %d for %d"%(self.i,x))
        if x < 0:
            raise ValueError("Will not read backwards")
        data = self.data[self.i:self.i+x]
        self.i += x
        return data
    
    def peek(self, x=4):
        pos = self.tell()
        data = self.read(x)
        self.seek(pos)
        return data
    
    def seek(self, x):
        self.i = x
        return
    
    def skip(self, x):
        self.i += x
        return
    
    def tell(self):
        return self.i
    
    def __len__(self):
        return len(self.data)
    
    def remaining(self):
        return len(self.data)-self.i
    
    def __bool__(self):
        return bool(self.remaining())
    
    def __getitem__(self,key):
        if type(key) is int:
            if key < 0:
                return self.data[key]
            return self.data[self.i+key]
        if type(key) is slice:
            i = self.i
            start,stop,step = key.start,key.stop,key.step
            if start is not None:
                if start >= 0:
                    start = i+start
            else:
                start = i
            if stop is not None: 
                if stop >= 0:
                    stop = i+stop
            return self.data[slice(start,stop,step)]
        raise TypeError("Key is not slice or integer")