# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 02:29:20 2020

@author: AsteriskAmpersand
"""
import construct as C
from EFX_Timl import TIMLSIG
#Header > Align32 > EntriesHeaders[] > Align32 > 
#All DataHeaders > Align32 > AllTypesHeaders[] > Align32 >
#       AllTransformHeaders[] > Align32 > AllKeyframes[] (32Align per Transform)
#

Raw_TIML_Header = C.Struct(
        "timl" / C.Const("timl",C.PaddedString(4,"utf-8")),
        "signature" / C.Const([0,8,2,24],C.Int8sl[4])[2],
        "NULL" / C.Const(0,C.Int32sl),
        "enabled" / C.Int64sl,
        "count" / C.Int32sl
        )

Raw_TIML_Data_Header = C.Struct(
        "offset" / C.Int64sl,
        )

Raw_TIML_Data = C.Struct(
        "offset" / C.Int64sl,
        "count"  / C.Int64sl,
        "unkn1"  / C.Int32sl,
        "unkn2"  / C.Int32sl,
        "animationLength" / C.Float32l,
        "loopStartPoint" / C.Float32l,
        "loopControl" / C.Int32sl,
        "labelHash" / C.Int32sl,        
        )

Raw_TIML_Type = C.Struct(
        "offset" / C.Int64sl,
        "count" / C.Int64sl,
        "timelineParameterHash" / C.Int32sl,
        "NULL" / C.Int32sl,
        )

Raw_TIML_Transform = C.Struct(
        "offset" / C.Int64sl,
        "count" / C.Int64sl,
        "datatypeHash" / C.Int32sl,   
        "dataType" / C.Int32sl,  
        )

Raw_TIML_Frame = C.Struct(
        "data" / C.Switch(C.this._.dataType,{0:C.Int32sl,1:C.Int32ul,2:C.Float32l,3:C.Int8ul[4],4:C.Int32ul}),
        "bounceForwardLimit" / C.Float32l,
        "bounceBackwardsLimit" / C.Float32l,
        "frameTiming" / C.Float32l,
        "interpolation" / C.Int16sl,
        "easing" / C.Int16sl,
        )

Raw_TIML_Int = C.Struct(
        "data" / C.Int32sl,
        "bounceForwardLimit" / C.Float32l,
        "bounceBackwardsLimit" / C.Float32l,
        "frameTiming" / C.Float32l,
        "interpolation" / C.Int16sl,
        "easing" / C.Int16sl,
        )

Raw_TIML_Float = C.Struct(
        "data" / C.Float32l,
        "bounceForwardLimit" / C.Float32l,
        "bounceBackwardsLimit" / C.Float32l,
        "frameTiming" / C.Float32l,
        "interpolation" / C.Int16sl,
        "easing" / C.Int16sl,
        )

class Raw_TIML():
    def __init__(self,stream = None):
        if stream:
            self.parse(stream)
    
    def align(self,stream):
        if stream:
            stream.read((-stream.tell())%16)
            return
    
    def parse(self,stream):
        self.Header = Raw_TIML_Header.parse_stream(stream)
        self.align(stream)
        
        self.dataHeaders = []
        for d in range(self.Header.count):
            self.dataHeaders.append(Raw_TIML_Data_Header.parse_stream(stream))
        self.align(stream)
        
        self.data = []
        self.types = []
        self.transforms = []
        self.keyframes = []
        for header in self.dataHeaders:
            if header.offset != 0:
                data = Raw_TIML_Data.parse_stream(stream)
                self.data.append(data)
                self.align(stream)
                    
                types = []
                for t in range(data.count):
                    types.append(Raw_TIML_Type.parse_stream(stream))
                self.types += types
                self.align(stream)
                
                transforms = []
                for typing in types:
                    for t in range(typing.count):
                        transforms.append(Raw_TIML_Transform.parse_stream(stream))
                    self.align(stream)
                self.transforms += transforms                
                    
                keyframes = []
                for t in transforms:
                    for k in range(t.count):
                        keyframes.append(Raw_TIML_Int.parse_stream(stream))                        
                    self.keyframes += keyframes
                    self.align(stream)                    
            else:
                self.data.append(None)

class fakeFile():
    def __init__(self,data):
        self.cursor = 0
        self.data = data
    def read(self,length = 1):
        if length + self.cursor > len(self.data):
            raise ValueError("read failed, requested %d, %d left at position %d"%(length,len(self.data)-self.cursor,self.cursor))
        data = self.data[self.cursor:self.cursor+length]
        self.cursor += length
        return data
    def seek(self,pos):
        if pos > len(self.data):
            raise ValueError("skip failed, attempted to jump %d beyond bounds %d"%(pos,len(self.data)-self.cursor))
        self.cursor = pos
    def skip(self,length):
        self.read(length)
    def tell(self):
        return self.cursor
    def __bool__(self):
        return self.cursor < len(self.data)

def extractTIML(stream):
    file = stream.read()
    timlOffset = []
    lastOffset = 0
    try:
        while(True):
            lastOffset = file.index(TIMLSIG,lastOffset)
            timlOffset.append(lastOffset)
            lastOffset += 1
    except:
        pass
    timls = []    
    for offset in timlOffset:
        length = C.Int32sl.parse(file[offset-4:offset])
        timls.append(fakeFile(file[offset:offset+length]))
    return timls
           
if __name__ == "__main__":
    from pathlib import Path
    chunk = r"E:\MHW\ChunkG0"

    for file in list(Path(chunk).rglob("*.efx")):
        with open(file,"rb") as inf:
            timls = extractTIML(inf)
            if timls:
                pass
                #print(file)
            for timl in timls:                
                timl2 = Raw_TIML(timl)
                
    for file in list(Path(chunk).rglob("*.timl")):
        with open(file,"rb") as inf:
            pass
            #print(file)
            timl = Raw_TIML(inf)
            
