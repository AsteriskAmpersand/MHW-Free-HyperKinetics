# -*- coding: utf-8 -*-
"""
Created on Sat Dec  5 09:03:50 2020

@author: AsteriskAmpersand
"""
import construct as C

mbdHeader = C.Struct(
    "signature" / C.Int32sl,
    "version" / C.Int32sl,
    "count" / C.Int32sl,
    "spacer" / C.Int32sl,
)

stringBlock = C.Struct(
    "animationID" / C.Int32sl,#;//9
    "declaration" / C.CString("utf8"),#;//
    "unkn4" / C.Float32l,#;//2 Doesn't seem to do anything
    "startFrame" / C.Int32sl,#;//3 EntryPoint0
    "interpolationPoint" / C.Int32sl,#;//4 EntryPoint1
    "animationOverlapBlending" / C.Int32sl,#;//5 EntryPoint2
    "unkn8" / C.Float32l,#;//6
    "one0" / C.Int32sl,#;//7
    "min1" / C.Int32sl,#;//8    
)

mbdEntry = C.Struct(
    "index" / C.Int32sl,
    "stringCount" / C.Int32sl,
    "zero" / C.Int32sl,    
    "block" / stringBlock[C.this.stringCount],
    "unkn3" / C.Int32sl,
    "unkn11" / C.Int32sl,
    "unkn12" / C.Int32sl,
)

mbdFile = C.Struct(
    "Header" / mbdHeader,
    "Entries" / mbdEntry[C.this.Header.count],
    )

from pathlib import Path

unkn4 = set()
one0 = set()
unkn8 = set()
min1 = set()
unkn3 = set()
unkn11 = set()
zero = set()
unkn12 = set()

#anim2 = set()
root = r"E:\MHW\ChunkG0\hm\wp"
for file in Path(root).rglob("*.mbd"):
    mbd = mbdFile.parse_file(str(file))
    for ix,entry in enumerate(mbd.Entries):        
        unkn3.add(entry.unkn3)
        unkn11.add(entry.unkn11)
        zero.add(entry.zero)
        unkn12.add(entry.unkn12)
        for jx,subentry in enumerate(entry.block):
            #if subentry.one0 != 0:
            #   print("One0: %s: %d = %d"%(str(file.relative_to(root)), ix,subentry.one0))  
            if subentry.min1 != -1:
               print("Min1: %s: %d = %d"%(str(file.relative_to(root)), ix,subentry.min1))  
            #if subentry.unkn8 != 1.0:
            #   print("Unkn8: %s: %d = %f"%(str(file.relative_to(root)), ix,subentry.unkn8))    
            unkn4.add(subentry.unkn4)
            unkn8.add(subentry.unkn8)   
            one0.add(subentry.one0)
            min1.add(subentry.min1)
#print(anim2)
print(unkn4)
print(one0)
print(unkn8)
print(min1)
print(unkn3)
print(unkn11)
print(zero)
print(unkn12)