# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 03:55:00 2021

@author: AsteriskAmpersand
"""
import json
import struct
try:
    from ..common import Cstruct as CS
    from ..common import FileLike as Fl
except:
    import sys
    sys.path.append('../common')
    from common import Cstruct as CS
    from common import FileLike as Fl
from collections import OrderedDict

TIMLSIG = b"timl"

class Visitable():
    def __setVisitFlags__(self,field):
        field.__visited__ = False
        field.__selfOffset__ = None
    def setVisitFlags(self,depth = 0):
        self.__setVisitFlags__(self)
        if hasattr(self,"subiterable"):
            print("  "*depth,type(getattr(self,self.subiterable)))
            for t in getattr(self,self.subiterable):
                print("  "*depth,"-",type(t))
                t.setVisitFlags(depth+1)
    def updateOffsets(self):
        print("Updating:",type(self))
        if hasattr(self,"subiterable"):
            nlevel = getattr(self,self.subiterable)
            print(nlevel)
            print()
            if nlevel:
                self.offset = nlevel[0].__selfOffset__
            for l in nlevel:
                if hasattr(l,"updateOffsets"):
                    l.updateOffsets()
    def extend(self,extendedStructure):
        if hasattr(self,"subiterable"):
            setattr(self,self.subiterable,extendedStructure)
            self.count = len(extendedStructure)
        return self
    def rprint(self):
        print(str(self))
        if hasattr(self,"subiterable"):
            for n in getattr(self,self.subiterable):
                if hasattr(n,"rprint"):
                    n.rprint()
                else:
                    print(n)

class TIML_Header(CS.PyCStruct):
    fields = OrderedDict([
        ("timl", "char[4]"),
        ("signature", "byte[8]"),
        ("NULL", "int"),
        ("enabled", "int64"),
        ("count","uint32")
        ])
    defaultProperties = {"timl":"timl",
                     "signature":[0x00,0x08,0x02,0x18,0x00,0x08,0x02,0x18],
                     "NULL":0,
                     "enabled":32}

class TIML_Data_Header(CS.PyCStruct):
    def __init__(self,size,*args,**kwargs):
        self.fields = OrderedDict([("offsets", "uint64[%d]"%size)])
        super().__init__(*args,**kwargs)

class TIML_Data(CS.PyCStruct,Visitable):
    fields = OrderedDict([
        ("offset", "uint64"),
        ("count", "uint64"),
        ("dataIx0", "int"),
        ("dataIx1", "int"),
        ("animationLength", "float"),
        ("loopStartPoint", "float"),
        ("loopControl", "int"),
        ("labelHash","uint")
        ])
    subiterable = "types"
    def structure(self):
        structure = [CS.DeferredPadding(16),self,CS.DeferredPadding(16)]
        for types in getattr(self,self.subiterable):
            structure.append(types)
        structure.append(CS.DeferredPadding(16))
        for types in getattr(self,self.subiterable):
            for transforms in getattr(types,types.subiterable):
                structure.append(transforms)
            structure.append(CS.DeferredPadding(16))
        for types in getattr(self,self.subiterable):
            for transforms in getattr(types,types.subiterable):
                for ks in getattr(transforms,transforms.subiterable):
                    structure.append(ks)                    
                structure.append(CS.DeferredPadding(16))
        structure.pop()
        return structure

class TIML_Type(CS.PyCStruct,Visitable):
    fields = OrderedDict([
        ("offset", "uint64"),
        ("count", "uint64"),
        ("timelineParameterHash", "uint"),
        ("NULL", "int")
        ])
    subiterable = "transforms"
    
class TIML_Transform(CS.PyCStruct,Visitable):
    fields = OrderedDict([
        ("offset", "uint64"),
        ("count", "uint64"),
        ("datatypeHash", "uint"),
        ("dataType", "int")
        ])
    subiterable = "keyframes"

class TIML_MetaFrame(CS.PyCStruct,Visitable):
    baseTypes =  ["int32","int32","int32"]
    def __init__(self,*args,**kwargs):
        types = self.baseTypes
        self.fields = OrderedDict([
            ("value", types[0]),
            ("controlL", types[1]),
            ("controlR", types[2]),
            ("frameTiming", "float"),
            ("transition", "int16"),
            ("dataType", "int16")
            ])
        super().__init__(*args,**kwargs)

class TIML_Int(TIML_MetaFrame):
    baseTypes =  ["uint32","uint32","uint32"]

class TIML_SInt(TIML_MetaFrame):
    baseTypes =  ["int32","int32","int32"]

class TIML_Float(TIML_MetaFrame):
    baseTypes =  ["float","float","float"]
    
class TIML_Color(TIML_MetaFrame):
    baseTypes =  ["ubyte[4]","float","float"]

class TIML_Bool(TIML_MetaFrame):
    baseTypes =  ["uint32","uint32","uint32"]

def TIML_DataFrame(typing):
    return {0:TIML_SInt,
            1:TIML_Int,
            2:TIML_Float,
            3:TIML_Color,     
            4:TIML_Bool,
            }[typing]

def TIML_Frame(typing):
    return TIML_DataFrame(typing)()

def emptyPrint(*args,**kwargs):
    return

class TIML(Visitable):
    subiterable = "data"
    def __init__(self,stream = None):
        if stream:
            self.marshall(stream)
        else:
            self.Header = TIML_Header()
            self.dataHeaders = []
            self.data = []
        self.__serializationStructure__ = None
            #Data Headers are hollow offsset objects that get populated with TIML_Data, Data is the data for the entry, and TIML_Types are the contents of the entry
    @staticmethod
    def align(stream):
        if stream:
            stream.read((-stream.tell())%16)
            return
    @staticmethod
    def pad(pos):
        return b'\x00'*(-pos%16)
    
    @staticmethod
    def marshallTIML(offset,stream):        
        if offset != 0:           
            data = TIML_Data().marshall(stream)
            #self.data.append(data)
            TIML.align(stream)                   
            types = []
            for typingIx in range(data.count):
                #output_print("\t"+hex(stream.tell())+"\t %d Typing"%typingIx)
                typing = TIML_Type().marshall(stream)
                types.append(typing)                    
            TIML.align(stream)
            for typingIx,typing in enumerate(types):
                transforms = []
                for transformIx in range(typing.count):
                    #output_print("\t"+hex(stream.tell())+"\t\t %d-%d Transform"%(typingIx,transformIx))
                    transform = TIML_Transform().marshall(stream)
                    transforms.append(transform)
                TIML.align(stream)
                typing.transforms = transforms
            for typingIx,typing in enumerate(types):
                for transformIx,transform in enumerate(typing.transforms):
                    keyframes = []
                    for keyfIx in range(transform.count):
                        #output_print("\t"+hex(stream.tell())+"\t\t\t %d-%d-%d Keyframe"%(typingIx,transformIx,keyfIx))
                        keyframes.append(TIML_Frame(transform.dataType).marshall(stream))
                    transform.keyframes = keyframes
                    TIML.align(stream)
            data.types = types
        else:
            data = None
        return data
    
    def extend(self,timlEntries):
        self.Header.construct({}).count = len(timlEntries)
        for ix,data in enumerate(timlEntries):
            if data is not None:
                data.id = ix
        self.data = list(filter(lambda x: x is not None,timlEntries))
        return self
    
    def calculateSerializingStructure(self):
        #offsets = [0 for i in range(self.Header.entryCount)]
        structure = [self.Header]
        if self.Header.count == 0: return structure
        structure += [CS.DeferredPadding(16),self.dataHeaders]
        for datum in self.data:
            structure += [CS.DeferredPadding(16)]+datum.structure()
        #while(type(substructures[-1]) is C.DeferredPadding):substructures.pop(-1)
        return structure
    
    def calculateStructureOffsets(self,structure):
        runningCount = 0
        print(list(map(type,structure)))
        for entry in structure:
            if type(entry) is CS.DeferredPadding:
                entry.pad(runningCount)
            print(type(entry))
            entry.__selfOffset__ = runningCount
            runningCount += entry.size()
        return    
    
    def calculateDataHeaders(self):
        offsets = [0 for _ in range(self.Header.count)]
        for i in self.data:
            if i is not None:
                offsets[i.id] = i.__selfOffset__
        return offsets
    
    def calculateOffsets(self):        
        self.setVisitFlags()
        #self.Header = LMTHeader()
        self.dataHeaders = TIML_Data_Header(self.Header.count)         
        structure = self.calculateSerializingStructure()        
        self.calculateStructureOffsets(structure)
        self.updateOffsets()        
        self.dataHeaders.construct({"offsets":self.calculateDataHeaders()})
        self.__serializationStructure__ = structure
        return
    
    def marshall(self,stream):
        #output_print = emptyPrint
        self.Header = TIML_Header().marshall(stream)
        if self.Header.count == 0: 
            self.data = []
            self.dataHeaders = []
            return self
        self.align(stream)
        #print(hex(stream.tell())+"\t :Offsets")
        
        self.dataHeaders = TIML_Data_Header(self.Header.count).marshall(stream)
        self.align(stream)
        #output_print(hex(stream.tell())+"\t DataStart")
        #self.data = []
        self.data = []
        for i,offset in enumerate(self.dataHeaders.offsets):
            data = self.marshallTIML(offset,stream) 
            if data:
                data.id = i
                self.data.append(data)
        #output_print()
        return self
    
    def serialize(self):
        if self.__serializationStructure__ is None:
            self.calculateOffsets()
        print()
        print()
        self.rprint()
        print()
        print()
        return b''.join(map(lambda x: x.serialize(),self.__serializationStructure__))

def parseTIML(filename):
    with open(filename,"rb") as inf:
        return TIML(inf)

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


def getTimlOffsets(file):
    timlOffset = []
    lastOffset = 0
    try:
        while(True):
            lastOffset = file.index(TIMLSIG,lastOffset)
            timlOffset.append(lastOffset)
            lastOffset += 1
    except:
        pass
    return timlOffset

def parseLength(file,offset):
    return CS.readBinary("int",Fl.FileLike(file[offset-4:offset]))
def writeLength(length):
    return CS.writeBinary("int",length)
def extractTIML(stream):
    timls = []    
    file = stream.read()
    timlOffset = getTimlOffsets(file)    
    for offset in timlOffset:
        length = parseLength(file,offset)
        #print(length)
        timls.append(TIML(fakeFile(file[offset:offset+length])))
    return timls,timlOffset

def parseEFX(filename):
    with open(filename,"rb") as inf:
        timls,_ = extractTIML(inf)
    return timls

def printTIML(timl):
    for h in timl.dataHeaders:
        if h.offset:
            h.data.print("")
            for typing in h.types:
                typing.print("    |")
                for transform in typing.transforms:
                    transform.print("    |    |")
                    for keyf in transform.keyframes:
                        keyf.print("    |    |    |")
                        print("    |    |    |------------")

if __name__ == "__main__":
    from pathlib import Path
    chunk = r"E:\MHW\chunk"
                
    for file in list(Path(chunk).rglob("*.timl")):
        print(file)
        with open(file,"rb") as inf:
            #pass
            #print(file)
            bind = inf.read()
            inf.seek(0)
            timl = TIML(inf)
            assert timl.serialize() == bind
            
    for file in list(Path(chunk).rglob("*.efx")):
        print(file)
        with open(file,"rb") as inf:
            timls,offsets = extractTIML(inf)
            if timls:
                pass
                #print(file)
            for timl in timls:                
                timl.serialize()