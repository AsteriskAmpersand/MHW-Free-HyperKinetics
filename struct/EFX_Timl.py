# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 01:17:45 2020

@author: AsteriskAmpersand
"""
import construct as C

TIMLSIG = b"timl" 
MeshTransform = ("nEffect::nTimelineParam::TypeMesh",3549099559,1401615911)
Subtransform = {2391473670:("Pos","X"),
                4186820240:("Pos","Y"),
                1619304234:("Pos","Z"),                
                3142917:("Rot","X"),
                1999160723:("Rot","Y"),
                3995178025:("Rot","Z"),
                605859538:("Scl","X"),
                1394318916:("Scl","Y"),
                3390230526:("Scl","Z"),
                247131191:("Scl","All"),
                415594462:("Color","EmissiveRate"),
                1483249682:("Color","All"),
                1619906445:("Color","Emissive"),
                2669543726:("Color","Rate")                
                }
MESHTYPE = MeshTransform[1]

TIML_Keyframe = C.Struct(
        "data" / C.Switch(C.this._.dataType,{0:C.Int32sl,1:C.Int32ul,2:C.Float32l,3:C.Int8ul[4],4:C.Int32ul}),#"data"
        "interpolationStart" / C.Switch(C.this._.dataType,{0:C.Int32sl,1:C.Int32ul,2:C.Float32l,3:C.Float32l,4:C.Int32ul}),#"interpolationStart"
        "interpolationEnd" / C.Switch(C.this._.dataType,{0:C.Int32sl,1:C.Int32ul,2:C.Float32l,3:C.Float32l,4:C.Int32ul}),#"interpolationEnd"
        "frameTime" / C.Float32l,
        "interpolation" / C.Int16sl,
        "dataType" / C.Int16sl,
        )

TIML_Transform = C.Struct(
        "offset" / C.Int64sl,
        "count" / C.Int64sl,
        "datatypeHash" / C.Int32ul,#Rot:Z
        "dataType" / C.Int32sl,        
        "keyframes" / C.Pointer(C.this._._._._.base+C.this.offset,TIML_Keyframe[C.this.count])
        )

TIML_Type = C.Struct(
        "offset" / C.Int64sl,
        "count" / C.Int64sl,
        "nTimelineParamHash" / C.Int32ul,        
        "null" / C.Const(0,C.Int32sl),
        "transform" / C.Pointer(C.this._._._.base+C.this.offset,TIML_Transform[C.this.count])
        )
#Type and below are grouped as an action, the transform is the property that's customed var-ed and type is a stand in object
TIML_Data = C.Struct(              
        "offset" / C.Int64sl,
        "count" / C.Int64sl,
        "typeIndex" / C.Int32sl,#Takes any positive value
        "metadataIndex" / C.Int32sl,#Test
        "animationLength" / C.Float32l,
        "loopStartPoint" / C.Float32l,
        "loopControl" / C.Int32sl,#0 no loop, 1 loop
        "labelHash" / C.Int32ul,#Does Nothing        
        "type" / C.Pointer(C.this._._.base+C.this.offset,TIML_Type[C.this.count])
        )

TIML_Body = C.Struct(         
        "offset" / C.Int64sl,        
        "data" / C.IfThenElse(C.this.offset != 0, C.Pointer(C.this._.base + C.this.offset,TIML_Data),C.Int32sl[0])
        )

TIML = C.Struct(
        "base" / C.Tell, 
        "type" / C.Const("timl",C.PaddedString(4,"utf-8")),
        "const" / C.Const([402786304,402786304,0],C.Int32sl[3]),
        "enabled" / C.Int32sl,#0x20 if enabled
        "NULL" / C.Const(0,C.Int32sl),
        "count" / C.Int32sl,
        "countNull" / C.If(C.this.count,C.Const(0,C.Int32sl)),        
        "animations" / TIML_Body[C.this.count]     
        )
 
TIML = TIML.compile()

#Body > Data(LabelHash) > Type(TimelineParamHash) > Transform(DatatypeHash) > Keyframe
def extractTIML(file):
    timlOffset = []
    lastOffset = 0
    try:
        while(True):
            lastOffset = file.index(TIMLSIG,lastOffset)
            timlOffset.append(lastOffset)
            lastOffset += 1
    except:
        pass
    timl = []
    for offset in timlOffset:
        timl.append(TIML.parse(file[offset:]))
    return timl

if __name__ == "__main__":
    import csv
    def loadHashes():    
        from crccheck.crc import CrcJamcrc
        generalhash =  lambda x:  CrcJamcrc.calc(x.encode())
        
        pathing = r"E:\MHW EFX Analysis\HashedStrings.csv"
        hashes = {}
        maskedhashes = {}
        with open(pathing,"r") as hashfile:
            for line in hashfile:
                line.strip()
                line = line.replace("\n","")
                hexhash,maskedhash,inthash,maskedinthash = line.split(",")[-4:]
                text = ",".join(line.split(",")[:-4])
                hashes[int(inthash)] = text
                maskedhashes[int(maskedinthash)] = text
        materialHashes = r"G:\Tools\MaterialEditor\MaterialEditing\IBHashToMaterial.ryo"
        with open(materialHashes,"r") as matfile:
            for line in matfile.read().replace("\n","").split(","):
                hashes[generalhash(line)] = line
                maskedhashes[generalhash(line)&0x0FFFFFFF] = line
        labelHashes = r"E:\MHW EFX Analysis\LabelHashes.txt"
        with open(labelHashes,"r") as labelfile:
            for line in labelfile:
                string = line.replace("\n","").replace(" ","").split(",")[-1]
                hashes[generalhash(string)] = string
                maskedhashes[generalhash(string)&0x0FFFFFFF] = string
        classHashes = r"E:\MHW EFX Analysis\DTI_Props.h"
        with open(classHashes,"r",encoding = 'utf-8') as classfile:
            for line in classfile:
                if "class" in line:
                    string = line.replace("/*"," ").replace("//"," ").split(" ")[1]
                    hashes[generalhash(string)] = string
                    maskedhashes[generalhash(string)&0x0FFFFFFF] = string
        forcedHashes = r"E:\MHW EFX Analysis\HashForcedDump.txt"
        with open(forcedHashes,"r",encoding = 'utf-8') as hashfile:
            hashReader = csv.reader(hashfile)
            for line in hashReader:
                string = line[3]
                hashes[generalhash(string)] = string
                maskedhashes[generalhash(string)&0x0FFFFFFF] = string
        forcedHashes = r"E:\MHW EFX Analysis\HashForcedExtended.txt"
        with open(forcedHashes,"r",encoding = 'utf-8') as hashfile:
            hashReader = csv.reader(hashfile)
            for line in hashReader:
                string = line[3]
                hashes[generalhash(string)] = string
                maskedhashes[generalhash(string)&0x0FFFFFFF] = string
        return hashes,maskedhashes
    hashes,maskedhashes = loadHashes()
    
    def solveHash(sig):
        if sig in hashes:
            return hashes[sig]
        if sig&0x0FFFFFFF in maskedhashes:
            return maskedhashes[sig&0x0FFFFFFF]
        return sig

    from pathlib import Path
    chunk = r"E:\MHW\ChunkG0"
    
    def checkAdd(var,key,val):
        if key not in var:
            var[key] = set()
        var[key].add(val)
    
    u1,u2 = {},{}
    uu1 = {}
    easing = {}
    datatypeHash = {}
    timelineParamHashes = {}
    labelHash = {}
    
    typeData = {}
    
    for file in list(Path(chunk).rglob("*.efx"))+list(Path(chunk).rglob("*.timl")):
        with open(file,"rb") as inf:
            data = inf.read()
            timls = extractTIML(data)
    
            if timls:
                #print(file)
                #print("=============================================")
                pass
            for timl in timls:
                for anim in timl.animations:                
                    if anim.data:
                        #print("\t%d"%anim.body.unkn1)
                        #print("\t%d"%anim.body.unkn2)
                        #checkAdd(u1,anim.data.unkn1,file)
                        #checkAdd(u2,anim.data.unkn2,file)
                        #checkAdd(labelHash,anim.data.labelHash,file)
                        #if len(anim.data.type)>1:
                            #print("%d: %s"%(len(anim.data.type),file))
                        #    pass
                        for typing in anim.data.type:
                            #checkAdd(timelineParamHashes,typing.nTimelineParamHash,file)
                            for t in typing.transform:
                                #print("\t\t%d"%t.unkn1)
                                #checkAdd(uu1,t.unkn1,file)
                                #checkAdd(transformType,t.datatypeHash,file)
                                #checkAdd(datatypeHash,t.datatypeHash,file)
                                for frame in t.keyframes:
                                    #checkAdd(easing,(frame.interpolation,frame.easing),t.datatypeHash)
                                    pass
                                    var = frame.interpolation
                                    tar = anim.data.loopControl
                                    if var not in typeData:
                                        typeData[var] = set()
                                    typeData[var].add(tar)
                                
            if timls:
                #print("=============================================")
                #print()
                #print()
                pass
    print()
    for t in sorted(typeData.keys(),key = lambda x: x):
        #print("%s,%d,%d"%(solveHash(t),t,list(typeData[t])[0]))
        #if len(typeData[t])>1:raise ValueError
        print(t)
        print(sorted(list(typeData[t]),key = lambda x: x))
    raise
    def printVar(dic):
        for var in sorted(dic.keys()):
            print("\n\t%s"%str(var))
            print("========================")
            for entry in dic[var]:
                #print("\t" + str(entry.relative_to(chunk)))
                print("\t"+str(solveHash(entry)))
    
    print("Anim > Body > Unkn1")
    print("================================================")
    print("================================================")
    #printVar(u1)
    print("================================================")
    print()
    print()
    print("Anim > Body > Unkn2")
    print("================================================")
    print("================================================")
    #printVar(u2)
    print("================================================")
    print()
    print()
    print("Anim > Body > Transform > Unkn1")
    print("================================================")
    print("================================================")
    #printVar(uu1)
    print("================================================")
    print()
    print()
    print("Anim > Body > Transform > Keyframe > Easing-Easing")
    print("================================================")
    print("================================================")
    printVar(easing)
    print("================================================")
    
    params = []
    types = []
    print("Timeline Parameter Hash")
    for h in sorted(timelineParamHashes.keys()):
        if solveHash(h) != h:
            params.append(solveHash(h))
            #print(solveHash(h))
    for i in sorted(params):print(i)
    print()
    print("Data Type Hash")
    for h in sorted(datatypeHash.keys()):
        if solveHash(h) != h:
            types.append(solveHash(h))
            #print(solveHash(h))
            #print(datatypeHash[h]) 
    for i in sorted(types):print(i)
    print()
    print("Label Hash")
    for h in labelHash.keys():
        if solveHash(h) != h:
            print(solveHash(h))
            print(h)
    print()