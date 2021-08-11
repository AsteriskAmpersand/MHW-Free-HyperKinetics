# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 07:11:51 2020

@author: AsteriskAmpersand
"""

from collections import OrderedDict
from pathlib import Path
try:
    from ..common import Cstruct as C
    from ..common import FileLike as FL
    from .LmtBuffers import typeMapping,typeSize
    from . import TIML    
    from .ExtensibleList import ExtensibleList
    blenderEntry = True
except:
    from common import Cstruct as C
    from common import FileLike as FL
    from LmtBuffers import typeMapping,typeSize
    import TIML
    from ExtensibleList import ExtensibleList
    blenderEntry = False


class LMTHeader(C.PyCStruct):
    fields = OrderedDict([
        ("signature", "char[4]"),
        ("version", "short"),
        ("entryCount", "short"),
        ("unkn", "byte[8]"),
    ])
    defaultProperties = {"signature":"LMT\x00",
                         "version":95,
                         "unkn":[0x00,0x08,0x02,0x18,0x00,0x00,0x00,0x00]}
    requiredProperties = set(["entryCount"])
    
class LMTOffsets(C.PyCStruct):
    def __init__(self,size,*args,**kwargs):
        self.fields = OrderedDict([("offsets", "uint64[%d]"%size)])
        super().__init__(*args,**kwargs)
        
#LMT Ani Header
class LMTActionHeader(C.PyCStruct):
    fields = OrderedDict([
        ("fcurveOffset", "uint64"),
        ("fcurveCount", "int"),
        ("frameCount", "int"),
        ("loopFrame", "int"),
        ("NULL0", "int[3]"),
        ("Vec0", "float[4]"),#translation vector
        ("Vec2","float[4]"),#Lerp Values
        ("Flags","ubyte"),#{0, 1, 8, 9, 16, 17}
        ("NULL2","byte[2]"),
        ("Flags2","ubyte"),#{0, 1, 2}
        ("NULL3","int[5]"),       
        ("timlOffset", "uint64")
    ])
    #defaultProperties = {"fcurveOffset":None,"timlOffset":None}
    def extend(self,boneList,timl):
        self.fcurveCount = len(boneList)
        self.frameCount = boneList.frameCount
        self.bones = boneList
        self.timl = timl
        self.Vec0 = boneList.translation
        self.Vec2 = boneList.rotation
        return self
#        entry.construct({"fcurveOffset":None,"fcurveCount":None,"frameCount":None,
#                         "loopFrame":self.loopFrame,"Flags":flagMake(self.byteflag),"Flags2":flagMake(self.byteflag2),
#                         "NULL0":[0,0,0],"Vec0":[0,0,0,0],"Vec2":[0,0,0,1],"NULL2":[0,0],"NULL3":[0,0,0,0,0],
#                         "timlOffset":None
#                         })

class LMTBasis(C.PyCStruct):
    fields = OrderedDict([
        ("mult", "float[4]"),#
        ("add", "float[4]")
    ])

#Looks like it's not delta it simply is the root transform vs relative transforms
#transforms are simply <3 for normal bones and >3 for the root bone
transformMap = ["delta_rotation_quaternion","delta_location","delta_scale",
                "rotation_quaternion","location","scale"]

#kbrs
class LMTBoneDataHeader(C.PyCStruct):
    fields = OrderedDict([
        ("bufferType", "ubyte"),
        ("usage", "ubyte"),
        ("jointType", "ubyte"),#0
        ("205", "ubyte"),#205
        ("boneId", "int"),
        ("weight", "float"),#1
        
        ("bufferSize", "int"),        
        ("bufferOffset", "int64"),
        ("basis", "float[4]"),
        ("lerpOffset", "int64"),
    ])
    #defaultProperties = {"bufferOffset":None,"lerpOffset":None}
    def marshall(self,stream):
        super().marshall(stream)
        pos = stream.tell()
        keyframes = ExtensibleList()
        lerp = None
        self.bufferTypeClass = typeMapping[self.bufferType]
        if self.bufferOffset:            
            stream.seek(self.bufferOffset)
            length = len(self.bufferTypeClass())
            keyframes = ExtensibleList([self.bufferTypeClass().marshall(stream) for _ in range(self.bufferSize//length)])
        if self.lerpOffset:
            stream.seek(self.lerpOffset)
            lerp = LMTBasis().marshall(stream)
        stream.seek(pos)
        self.lerp = lerp
        self.keyframes = keyframes
        for kf in self.keyframes:
            kf.algorithm(self.basis,self.lerp)
        return self
    def construct(self,data):
        super().construct(data)
        if "lerp" in data:
            self.lerp = data["lerp"]
        if "keyframes" in data:
            self.keyframes = ExtensibleList(data["keyframes"])
    #def serialize(self):
    #    data = super().serialize()
    #    keys = b''.join([keyframe.sserialize() for keyframe in self.keyframes])
    #    lerp = self.lerp.serialize() if self.lerp else b''
    #    return data,keys,lerp
    def channelNames(self):
        #datapath_index,letter
        basisPath = transformMap[self.usage if self.usage >= 3 else self.usage+3]
        transformPath = transformMap[self.usage%3]
        #indices = self.bufferTypeClass.datamap.values()
        #var = self.bufferTypeClass.datamap.keys()
        return [(basisPath,transformPath,i,v) for v,i in self.bufferTypeClass.datamap.items()]
    def channels(self):
        return [[(getattr(k.vec,channel),k.frame) for k in self.keyframes] for channel in self.bufferTypeClass.datamap.keys()]
    def extendRoot(self,rot,trans):
        if self.usage %3 == 2:
            return
        #if self.bufferOffset:
        self.tail = [rot,trans][self.usage%3]
        #else:
        #    self.tail = self.basis
    def __len__(self):
        return len(self.keyframes)

class LMTEventParameter(C.PyCStruct):
    fields = OrderedDict([
        ("offset", "uint64"),
        ("count", "uint64" ),
        ("type", "uint32[2]")
    ])
    defaultProperties = {"offset":None}
    
class LMTData(C.PyCStruct):
        fields = OrderedDict([
            ("values","byte[20]")
            #("floatValues", "float[4]"),
            #("shortValues","short[2]")
        ])
        
class LMTEvents(C.PyCStruct):
    fields = OrderedDict([
        ("events_offset", "uint64"),
        ("event_count", "uint64"),
        ("unkn", "int[8]")
    ])
    defaultProperties = {"events_offset":None}
    
def Padding(data,alignment):
    pad = (-data.tell())%alignment
    pad = min(pad,len(data)-data.tell())
    data.read(pad)
    
def Align(offset,alignment):
    pad = (-offset%alignment)
    return offset+pad

class ActionCapsule(list):
    pass

class hollowChannelMap(list):
    def channels(self):
        return [[],[],[],[]]

class LMT():
    def __init__(self):
        self.Header = LMTHeader()
        self.ActionHeaders = []
        self.Keyframes  = []
        self.Metadata = []
        self.__serializationStructure__ = None
    @classmethod
    def parseFile(cls,filepath,*args,**kwargs):
        self = cls()
        with open(filepath,"rb") as inf:
            fl = inf
            fl = FL.FileLike(inf.read())
            return self.marshall(fl)
    @classmethod
    def parseFileSectional(cls,filepath,indexSet,parents=True,siblings=True,*args,**kwargs):
        self = cls()
        with open(filepath,"rb") as inf:
            fl = inf
            fl = FL.FileLike(inf.read())
            self.marshallHeader(fl)
            indexSet = self.expandIndexSet(indexSet,parents,siblings)
            self.marshallBody([action for action in self.ActionHeaders if action.id in indexSet],fl,*args,**kwargs)
            self.ActionHeaders = [action for action in self.ActionHeaders if action.id in indexSet]
            return self
    def expandIndexSet(self,indexSet,includeParents,includeSiblings):
        if not includeParents:
            return indexSet
        relevantOffsets = set((header.fcurveOffset for header in self.ActionHeaders if header.id in indexSet))
        for header in self.ActionHeaders:
            if header.fcurveOffset in relevantOffsets:
                indexSet.add(header.id)
                if not includeSiblings:
                    relevantOffsets.pop(header.fcurveOffset)
        return indexSet        
        
    def loadAction(self,data,action,KbrBodies):
        data.seek(action.fcurveOffset)
        bones = ActionCapsule()
        existing_ids = {}
        #action.fold = -1
        for _ in range(action.fcurveCount):
            bone = LMTBoneDataHeader().marshall(data)
            bone.parent = action
            #bone.fold = hollowChannelMap()            
            bone.fold = (bone.usage,bone.boneId) in existing_ids
            #if (bone.usage,bone.boneId) in existing_ids:
            #    action.fold = action.frameCount + 1
            #    existing_ids[(bone.usage,bone.boneId)].fold = bone
            #    if not blenderEntry: bones.append(bone)#TODO - Delete for plugin this is just for offset calculation
            bones.append(bone)
            existing_ids[(bone.usage,bone.boneId)] = bone            
            if bone.boneId == -1:
                bone.extendRoot(action.Vec2,action.Vec0)
        actionc = bones
        KbrBodies[action.fcurveOffset] = actionc
    def loadTIML(self,data,action,TIMLOffsets):
        data.seek(action.timlOffset)
        timl_data = TIML.TIML.marshallTIML(action.timlOffset,data)
        ctiml = timl_data
        #ctiml.parent = action                
        TIMLOffsets[action.timlOffset] = ctiml
    def marshall(self,data):
        self.marshallHeader(data)
        self.marshallBody(self.ActionHeaders,data,)
        return self
    def marshallHeader(self,data):
        self.Header.marshall(data)
        self.Offsets = LMTOffsets(self.Header.entryCount).marshall(data)
        Padding(data,16)
        for ix,offset in enumerate(self.Offsets.offsets):    
            if offset:
                action = LMTActionHeader()
                self.ActionHeaders.append(action.marshall(data))
                action.id = ix
        Padding(data,16)
    def marshallBody(self,entries,data):
        KbrBodies = {}
        TIMLOffsets = {}
        for action in entries:
            action.bones = []
            if action.fcurveOffset and action.fcurveOffset not in KbrBodies:
                self.loadAction(data,action,KbrBodies)
            if action.fcurveOffset:
                action.bones = KbrBodies[action.fcurveOffset]            
            action.timl = None
            if action.timlOffset and action.timlOffset not in TIMLOffsets:
                self.loadTIML(data,action,TIMLOffsets)
            if action.timlOffset:
                action.timl = TIMLOffsets[action.timlOffset]#replace for an action that tracks if its been converted
    def __setVisitFlags__(self,field):
        field.__visited__ = False
        field.__selfOffset__ = None
    def setVisitFlags(self):
        #recursive .__visited__ = False
        #recursive .__selfOffset__ = None
        for actionHeader in self.ActionHeaders:
            self.__setVisitFlags__(actionHeader)
            self.__setVisitFlags__(actionHeader.bones)
            for bone in actionHeader.bones:
                self.__setVisitFlags__(bone)
                if bone.lerp:
                    self.__setVisitFlags__(bone.lerp)
                if bone.keyframes:
                    self.__setVisitFlags__(bone.keyframes)
            if actionHeader.timl:
                actionHeader.timl.setVisitFlags()
    def calculateSerializingStructure(self):
        actionHeaderSize = len(LMTActionHeader())
        offsets = [0 for i in range(self.Header.entryCount)]
        structure = [self.Header,self.Offsets]
        animHeaderOffset = len(self.Header)+len(self.Offsets)
        headerPadding = C.DeferredPadding(16).pad(animHeaderOffset)
        structure.append(headerPadding)
        animHeaderOffset += headerPadding.size()
        substructures = []
        for actionHeader in self.ActionHeaders:
            structure.append(actionHeader)
            kbrsubstructure = []
            lerpsubstructure = []
            buffersubstructure = []
            timlsubstructure = []            
            offsets[actionHeader.id] = animHeaderOffset
            animHeaderOffset += actionHeaderSize            
            actionHeader.__visited__ = True
            if not actionHeader.bones.__visited__:
                actionHeader.bones.__visited__ = True
                for bone in actionHeader.bones:
                    kbrsubstructure.append(bone)
                    if bone.lerp is not None and not bone.lerp.__visited__:
                        bone.lerp.__visited__ = True
                        lerpsubstructure.append(bone.lerp)
                    if bone.keyframes and not bone.keyframes.__visited__:
                        bone.keyframes.__visited__ = True
                        buffersubstructure+=bone.keyframes
                        buffersubstructure.append(C.DeferredPadding(4))
            if actionHeader.timl and not actionHeader.timl.__visited__:
                actionHeader.timl.__visited__ = True
                timlsubstructure += actionHeader.timl.structure()
            C.ifpad(substructures,kbrsubstructure,0)
            C.ifpad(substructures,lerpsubstructure,16)
            C.ifpad(substructures,buffersubstructure,4)
            C.ifpad(substructures,timlsubstructure,4)
        #while(type(substructures[-1]) is C.DeferredPadding):substructures.pop(-1)
        return offsets,structure+substructures
    
    def calculateStructureOffsets(self,structure):
        runningCount = 0
        for entry in structure:
            if type(entry) is C.DeferredPadding:
                entry.pad(runningCount)
            entry.__selfOffset__ = runningCount
            runningCount += entry.size()
        return

    def updateOffsets(self):
        for ix,action in enumerate(self.ActionHeaders):
            action.fcurveOffset = C.offsetVisitCollection(action.bones)
            if action.bones: 
                for bone in action.bones:
                    bone.bufferOffset = C.offsetVisitCollection(bone.keyframes)
                    bone.lerpOffset = C.offsetVisit(bone.lerp)
            action.timlOffset = C.offsetVisit(action.timl)
            if action.timl:
                action.timl.updateOffsets()
        
    def calculateOffsets(self):        
        self.setVisitFlags()
        #self.Header = LMTHeader()
        self.Offsets = LMTOffsets(self.Header.entryCount)        
        offsets,structure = self.calculateSerializingStructure()        
        self.Offsets.construct({"offsets":offsets})
        self.calculateStructureOffsets(structure)
        self.updateOffsets()        
        self.__serializationStructure__ = structure
        return
    def construct(self,data):
        pass
    def extend(self,actionEntries):
        self.Header.construct({"entryCount":len(actionEntries)})
        for ix,action in enumerate(actionEntries):
            if action is not None:
                action.id = ix
        self.ActionHeaders = list(filter(lambda x: x is not None,actionEntries))
        return self
    def injectFile(self,lmt):
        used = set()
        injection = {action.id:action for action in lmt.ActionHeaders}
        existent = {action.id:action for action in self.ActionHeaders}
        if max(injection) >= self.entryCount():
            raise KeyError("Injection IDs exceed entry Count")
        existent.update(injection)
        self.ActionHeaders = [existent[e] for e in sorted(existent)]
    def serialize(self):
        if self.__serializationStructure__ is None:
            self.calculateOffsets()
        return b''.join(map(lambda x: x.serialize(),self.__serializationStructure__))
    def entryCount(self):
        return self.Header.entryCount
    
def parseSectionalLMT(filepath,indexSet,parents,siblings,*args,**kwargs):
    return LMT.parseFileSectional(filepath, indexSet,parents,siblings)

def parseLMT(filepath,*args,**kwargs):
    return LMT.parseFile(filepath,*args,**kwargs)

if __name__ in '__main__':
    from LmtBuffers import Vector
    from mathutils import Quaternion
    import numpy as np
    import time
    chunk = Path(r"E:\MHW\chunk")
    lerpCode = {}
    bufferCode = {}
    basis = {}
    flags1 = set()
    flags2 = set()
    nulls = set()
    quatLerp = set()#{}
    typePairs = set()
    
    endframe = set()
    lerps = {}
    typeMax = {}
    typeMin = {}
    
    lerpData = []
    
    print("Analysis Started")
    import numpy as np
    
    def gt(l,r):
        return r>l
    def lt(l,r):
        return r<l
    def compareUpdate(maxdic,key,comparator):
        for i,(k,val) in enumerate(zip(maxdic,[key.x,key.y,key.z,key.w])):
            if val is None: val = 0
            if comparator(k,val):
                maxdic[i] = val
        return
    
    filelist = list(chunk.rglob("*.lmt"))[:200]#[:200]#[:200]
    start = time.time()
    for ix,file in enumerate(filelist):
        l = LMT.parseFile(file)
        print(ix,file)
        print(l.Header.entryCount)
        print(len(l.ActionHeaders))
        print(len([a for a in l.ActionHeaders if a is not None]))
        continue
        
        #l = LMT.parseFileSectional(file,set([1,2,3]),parents=True,siblings=True)
        #raise
        #continue
        for jx,action in enumerate(l.ActionHeaders):
            #flags1.add(action.Flags)
            #flags2.add(action.Flags2)
            #nulls.add(tuple(action.NULL2))
            #quatLerp.add(Vector(action.Vec2).freeze())
            rootrot = False
            roottrans = False
            if action.bones:
                trans = action.Vec0
                rot = action.Vec2
                for ix,bone in enumerate(action.bones):
                    t = Vector# if bone.usage%3 != 0 else Quaternion                                                  
                    if bone.lerp:                        
                        lerpData.append((bone.usage,bone.bufferType,t(bone.lerp.mult)))
                    elif bone.keyframes:
                        minVec = t(tuple(map(min,zip(*map(lambda x: x.vec, bone.keyframes)))))
                        maxVec = t(tuple(map(max,zip(*map(lambda x: x.vec, bone.keyframes)))))
                        lerpData.append((bone.usage,bone.bufferType,maxVec-minVec))                     
                        
    print( (time.time()-start)*(5774/len(filelist)) )
    udict = {}   
    for usage,u,vec in lerpData:
        if (usage,u) not in udict:
            udict[(usage,u)] = []        
        udict[(usage,u)].append(vec)
    for usage,u in sorted(udict):
        vecs = list(map(lambda x: max(x) if usage%3 else max(x),udict[(usage,u)]))#abs(x.angle)
        print("%d/%d avg %.2f std %.2f max %.2f min %.2f"%(usage,u,np.mean(vecs),np.std(vecs),max(vecs),min(vecs)) )
         
        
    import matplotlib.pyplot as plt
    j = 0
    prev = None
    for usage,u in sorted(udict):
        if prev != usage:
            j = 0
            plt.title(str(prev))
            plt.xscale('log')
            plt.legend()
            plt.show()
            plt.close()            
        vecs = list(map(lambda x: max(x),udict[(usage,u)]))
        plt.scatter(vecs, [j for i in range(len(vecs))],s=1,label=u)    
        j+=1
        prev = usage
    plt.show()
    plt.close()
        
                    #key = bone.bufferType,bone.usage
                    #if bone.bufferType not in lerps:
                    #    lerps[bone.bufferType] = set()
                    #typePairs.add(key)
                    #ef = 0
                    
                    #if 11 <= bone.bufferType <= 13:
                    #    if bone.boneId == 14 and jx == 1:
                    #        print(bone.lerpOffset)
                    #        for ax,kf in enumerate(bone.keyframes):
                    #            if ax == 7:
                    #                print(ax)
                    #                print(kf.raw_w,kf.raw_x,kf.raw_y,kf.raw_z)
                    #                normf = 2**14-1
                    #                print(Vector((kf.raw_x/normf,kf.raw_y/normf,kf.raw_z/normf,kf.raw_w/normf))*
                    #                      Vector(bone.lerp.mult)+
                    #                      Vector(bone.lerp.add))
                    #                print(kf.vec)
                    #                print()
                    #                raise
                    #if bone.usage == 1:
                    #    print(file)
                    #    print(jx)
                    #    print(ix)
                    #    raise
                    #refM = list(map(max,zip(*(frame.vec for frame in bone.keyframes))))
                    #refm = list(map(min,zip(*(frame.vec for frame in bone.keyframes))))
                    #refU = sorted(bone.keyframes, key = lambda x: x.vec.length,reverse=True)
                    #if refM:
                    #    print("Basis",bone.basis)
                    #    #print("TheoryM",refM)
                    #    #print("Theorym",refm)
                    #    print("TheoryU",list(refU[0].vec))
                    #    print()
                    #for frame in bone.keyframes:
                    #    
                    #    pass
                        #if bone.bufferType == 3:
                        #    print(Vector([val for val in [frame.x,frame.y,frame.z,frame.w] if val is not None]))
                        #lerps[bone.bufferType].add(Vector([val for val in [frame.x,frame.y,frame.z,frame.w] if val is not None]).freeze())
                        #ef = frame.frame
                    #endframe.add(ef)
                    #if bone.usage > 2 and bone.boneId != -1:
                    #    print(hex(bone.fcurveOffset))
                    #    print(bone.usage)
                    #    print(bone.boneId)
                    #    raise
                    #if bone.usage <3 and bone.boneId == -1:
                    #    print(hex(bone.fcurveOffset))
                    #    print(bone.usage)
                    #    print(bone.boneId)
                    #    raise
                        
                    #for s in [lerpCode,bufferCode,basis]:
                    #    if key not in s:
                    #        s[key] = set()
                    #lerpCode[key].add( bone.lerpOffset != 0)
                    #bufferCode[key].add( bone.bufferSize != 0)
                    #basis[key].add(Vector(bone.basis).freeze())
    #print(nulls)
    #minima = lambda x: tuple(map(min,zip(*x)))
    #maxima = lambda x: tuple(map(max,zip(*x)))
    #leread = lambda x: (minima(lerps[x]),maxima(lerps[x]))
    #for ix in [4,5,7,11,12,13,14,15]:
    #    print(leread(ix))
    
        #for file in [r"E:\MHW\chunk\em\em113\00\mot\em113_00\em113_00.lmt"]:#r"E:\MHW\chunkG0\Assets\gm\gm015\gm015_000\mot\gm015_000\gm015_000.lmt"]:
    #             r"E:\MHW\chunkG0\npc\npc706\mot\npc706_09\npc706_09.lmt", 
    #             r"E:\MHW\chunkG0\npc\npc018\mot\npc018_09_st\npc018_09_st.lmt",
    #             r"E:\MHW\chunkG0\npc\common\mot\ncom151_09\ncom151_09.lmt",
    #             r"E:\MHW\chunkG0\npc\npc016\mot\npc016_09\npc016_09.lmt"]:
        # #known_pointers = set()
        # #print(file)
        # #if str(file)==r"E:\MHW\chunkG0\Assets\gm\gm006\gm006_000\mot\gm006_000_fs\gm006_000_fs.lmt": raise

        # #l.calculateOffsets()
        # continue
        # bindata = file.open("rb").read()
        # bincomp = l.serialize()
        # with open(r"C:\Users\AsteriskAmpersand\AppData\Roaming\Blender Foundation\Blender\2.79\scripts\addons\MHW-FreeHK\tests\Output"+"\\"+file.stem+".lmt","wb") as outf:
        #     outf.write(bincomp)
        # if bindata != bincomp:
        #     raise
        # continue
        # prev = set()
        # for o in l.Offsets.offsets:
        #     if o != 0 and o in prev:
        #         print(file)
        #         raise
        #     prev.add(o)
        # continue
        # print()