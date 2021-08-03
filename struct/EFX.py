# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 05:39:52 2020

@author: AsteriskAmpersand
"""


import construct as C
#from EFX_Subtypes import typeHash

EFXHeader = C.Struct(
        "signature" / C.Const(b"EFX\x00"),
        "version" / C.Const(b"\x78\xDC\x0A\x00"),
        "constant" / C.Const([402786304,0,1254190883,402786304,402786304],
                             C.Int32sl[5]),
        "EFXR" / C.Const(b"efxr"),
        "unkn0" / C.Int32sl,#1 is the usual but other values exist
        "unkn1" /  C.Int32sl,#-1
        "countBody" / C.Int32sl,
        "labelSize" / C.Int32sl,
        "countPlay" / C.Int32sl,
        "countExtern" / C.Int32sl,
        "countSubselection" / C.Int32sl,
        "subselectionSize" / C.Int32sl,
        "countEOF" / C.Int32sl,
        "doubleBuffer" / C.Int32sl,
        )

floatJitterXYZ = C.Struct("x" / C.Float32l,
                       "x_j" / C.Float32l,
                       "y" / C.Float32l,
                       "y_j" / C.Float32l,
                       "z" / C.Float32l,
                       "z_j" / C.Float32l,
                       )
floatXYZ = C.Struct("x" / C.Float32l,
                       "y" / C.Float32l,
                       "z" / C.Float32l,      
        )
intXYZ = C.Struct("x" / C.Int32sl,
                  "y" / C.Int32sl,
                  "z" / C.Int32sl,      
        )
byteXYZ = C.Struct("x" / C.Byte,
                   "y" / C.Byte,
                   "z" / C.Byte,  
                   "NULL" / C.Byte,  
        )

def XYZ(typing):
    return [floatJitterXYZ,intXYZ,byteXYZ,floatXYZ][typing]

PlayEFX = C.Struct(
        "unkn0" / C.Int32ul,
        "pathLen" / C.Int32ul,
        "type" / C.Int32ul,
        "unkn1" / C.Int32ul[7],
        "xyz" / XYZ(3),
        "NULL" / C.Int32ul[3],
        "path" / C.PaddedString(C.this.pathLen,"utf-8")
        )

PlayEmitter = C.Struct(
        "unkn" / C.Int32ul[7],
        "xyz" / XYZ(3),
        "NULL" / C.Int32sl[3],
        "targetCount" / C.Int32ul,
        "targets" / C.Int32sl[C.this.targetCount]        
        )

PlayType = {1965813039:PlayEFX,1152332069:PlayEmitter}

PlayEntry = C.Struct(
        "labelHash" / C.Int32ul,
        "count" / C.Int32sl,
        "data" / C.Struct(
            "type" / C.Int32ul,
            "data" / C.Switch(C.this.type, PlayType),
            )[C.this.count]
        )

ExternEntry = C.Struct()
MainEntry = C.Struct()

SubselectionEntry = C.Struct(
        "type" / C.Int32sl,
        "unkn0" / C.Int32sl,
        "count" / C.Int32sl,
        "entries" / C.Int32sl[C.this.count],
        )

EFXStruct = C.Struct(
        "header" / EFXHeader,
        "labels" / C.PaddedString(C.this.header.labelSize,"utf-8"),        
        "play" / PlayEntry[C.this.header.countPlay],
        )

if __name__ in '__main__':
    from pathlib import Path
    chunk = r"E:\MHW\Chunk"
    efxtype = {}
    efxkind = {}
    for path in Path(chunk).rglob("*.efx"):
        #print(path)
        with open(path,"rb") as inf:
            efx = EFXStruct.parse_stream(inf)
            
            typing = efx.Header.unkn0
            if typing not in efxtype:
                efxtype[typing] = []
            efxtype[typing].append(path)
            
            kind = efx.Header.unkn1
            if kind not in efxkind:
                efxkind[kind] = []
            efxkind[kind].append(path)              
            
            #print()
            #for p in efx.play:
            #    for block in p.data:
            #        if PlayType[block.type] is PlayEFX:
            #            print("%X"%block.data.type)
    for t in efxtype:
        print(t)
        print(efxtype[t][0])
        print()