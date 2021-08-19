# -*- coding: utf-8 -*-
"""
Created on Sun Jun 27 03:49:03 2021

@author: AsteriskAmpersand
"""
from pathlib import Path

class NonUniqueHash(Exception):
    pass

class HashTable():
    def __init__(self):
        self.table = dict()
        self.mtable = dict()
    def add(self,name,h,maskedh):
        if h not in self.table:
            self.table[h] = []    
        self.table[h].append(name)
        if maskedh not in self.mtable:
            self.mtable[maskedh] = []    
        self.mtable[maskedh].append(name)
    def resolve(self,h,unique = True):
        "Returns inverse, if it was resolved and if it is unique"
        candidates = []
        if h in self.table:
            candidates += self.table[h]
        if h&0x0FFFFFFF in self.mtable:
            candidates += self.mtable[h&0x0FFFFFFF]
        results = set(candidates)
        if len(results) == 0:
            return h,False,True
        if len(results) == 1:
            return next(iter(results)),True,True
        else:
            if unique:
                raise NonUniqueHash("The following value %s is hashed by multiple strings %s"%(hex(h),str(candidates)))
            else:
                return results,True,False      

def buildTable():
    datafile = Path(__file__).parent / r"..\struct\TIMLDatatypes.txt"
    timelinefile = Path(__file__).parent / r"..\struct\TIMLTimelineParam.txt"
    table = HashTable()
    with open(datafile,"r",encoding = 'utf-8') as hashfile:
        for line in hashfile:
            line.strip()
            line = line.replace("\n","")
            hexhash,text,dt = line.split(",")
            table.add(text,int(hexhash),int(hexhash)&0x0FFFFFFF)
    with open(timelinefile,"r",encoding = 'utf-8') as hashfile:
        for line in hashfile:
            line.strip()
            line = line.replace("\n","")
            hexhash,text = line.split(",")
            table.add(text,int(hexhash),int(hexhash)&0x0FFFFFFF)
    return table
    
masterTable = buildTable()
def hashResolver(h,table = masterTable):
    result, resolved, unique = table.resolve(h)
    return result,resolved