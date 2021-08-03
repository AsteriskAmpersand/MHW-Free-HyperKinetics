# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 22:55:12 2021

@author: AsteriskAmpersand
"""

from collections import OrderedDict
from mathutils import Vector as BaseVec
import struct 
try:
    from ..common import Cstruct as C
    from ..common.BitUtils import QuantizedVals,structread
except:
    import sys
    sys.path.append('../common')
    import Cstruct as C
    from BitUtils import QuantizedVals,structread

class Vector(BaseVec):
    def __mul__(self,value,*args,**kwargs):
        if type(value) is Vector:
            return Vector([l*r for l,r in zip(self,value)])
        return super().__mul__(value,*args,**kwargs)        

class Basis():
    def __init__(self,a,ba):
        self.start = a
        self.end = ba + a
    def interpol(self,param):
        return self.start*(1-param)+self.end*param
    
    
vecMap = {"x":0,"y":1,"z":2}
angularMap = {"w":0,"x":1,"y":2,"z":3}
class Keyframe():
    def marshall(self,data):
        pass
    
    @staticmethod
    def raw(kf,root,basis):
        kf.vec = Vector([kf.x,kf.y,kf.z,kf.w])
        return kf
    
    @staticmethod
    def lerp(kf,root,basis):
        add,mul = Vector(basis.add),Vector(basis.mult)
        vec = Vector([kf.x,kf.y,kf.z,kf.w])
        kf.vec = vec*mul+add
        return kf
    
    @staticmethod
    def basisChoice(kf,root,basis):
        return Keyframe.lerp(kf,root,basis)
    
def signstrip(n):
    def signstripFunction(val):
        if val < 0:
            absval = round(abs(val)*(2**(n-1)-1))
            absval ^= (2**(n)-1)
            return absval
        else:
            return round (val*(2**(n-1)-1))
    return signstripFunction

def default(n):
    def defaultFunc(val):
        return n
    return defaultFunc

def signed(n):
    hibit = lambda x: x&(2**(n-1)) != 0
    def signedFunction(val):
        if hibit(val):
            mask = (2**(n)-1)
            absval = ((val&mask)^mask)+1
            return -(absval)/(2**(n-1))
        else:
            return val/(2**(n-1)-1)
    return signedFunction

def normalized(n,offset=0,mulmin=0):
    #offset = 0
    #mulmin = 0
    def normalizedFunction(val):
        if val is None:
            return 0
        return (val-offset)/((2**n)-1-mulmin-offset)
    return normalizedFunction


def denormalize(n,offset=0,mulmin=0):
    #offset = 0
    #mulmin = 0
    def denormalizedFunction(val):
        return int(val*((2**n)-1-mulmin-offset))+offset
    return denormalizedFunction

normalizePair = lambda x,off,ran: (normalized(x,off,ran),denormalize(x,off,ran))
#normalizePair = lambda x,off,ran: (lambda y: y,lambda y: y)

ilen = flen = 32
blen = 8
slen = 16

keyorder = ["x","y","z","w"]
floatType = "float"
nullType = "null"
uintType = "uint32"
shortType = "uint16"
byteType = "uint8"

idem = lambda x: x
class KeyframeParser(C.PyCStruct):
    normalizer = idem
    denormalizer = idem
    def marshall(self,*args,**kwargs):
        super().marshall(*args,**kwargs)
        for coordinate in keyorder:
            val = getattr(self,"raw_"+coordinate)
            val = self.__class__.normalizer(val) if val is not None else 0
            setattr(self,coordinate,val)
        return self
    def construct(self,data):
        for coordinate in keyorder:
            data["raw_"+coordinate] = self.__class__.denormalizer(data[coordinate])        
        return super().construct(data)
        

def field3d(cordinateType,frameType):
    return   OrderedDict([
            ("raw_x",cordinateType),
            ("raw_y",cordinateType),
            ("raw_z",cordinateType),
            ("raw_w",nullType),
            ("frame",frameType),
            ])

class floatVectorBase(KeyframeParser,Keyframe):
    datamap = vecMap
    algorithm = Keyframe.raw
    fields = field3d(floatType,nullType)
        
class floatVectorKey(KeyframeParser,Keyframe):
    datamap = vecMap
    algorithm = Keyframe.raw
    fields = field3d(floatType,uintType)
    
class floatRotKey(floatVectorBase):
    datamap = angularMap

norm16,denorm16 = normalizePair(16,8,7)
class shortVectorInterpolation(KeyframeParser,Keyframe):
    datamap = vecMap
    algorithm = Keyframe.lerp
    fields = field3d("uint16",shortType)
    normalizer,denormalizer = normalizePair(16,8,7)

class byteVectorInterpolation(KeyframeParser,Keyframe):
    datamap = vecMap
    algorithm = Keyframe.lerp
    fields = field3d("uint8",byteType)
    normalizer,denormalizer = normalizePair(8,8,7)

class BitKeyframe(Keyframe):
    correction = (0,0,0,0)
    muloffset = (0,0,0,0)
    def __init__(self):
        self.length = sum(self.fields.values())
        self.normalizers = {field:normalized(self.n,c,m) for field,c,m in zip(self.fields,self.correction,self.muloffset)}
        self.denormalizers = {field:denormalize(self.n,c,m) for field,c,m in zip(self.fields,self.correction,self.muloffset)}       
    def quantize(self,data):
        bitlen = 8*struct.calcsize(self.structFormat[0])
        values = QuantizedVals(structread(data,self.structFormat),bitlen)
        return values
    def marshall(self,data):
        values = self.quantize(data)
        for field, count in self.fields.items():
            setattr(self,field,values.takebits(count))
        for coordinate in keyorder:
            setattr(self,coordinate,self.normalizers["raw_"+coordinate](getattr(self,"raw_"+coordinate)))
        return self
    def insertBits(self,result,val,bitcount,bitoff):
        bitsize = 8*struct.calcsize(self.structFormat[0])
        mod = val
        while(bitcount):
            masklen = min(bitsize-bitoff,bitcount)
            mval = mod & (2**masklen-1)
            mod >>= masklen
            result = mval | (result<<masklen)
            bitcount -= masklen
            bitoff += masklen
            if bitoff == bitsize:
                bitoff = 0
        return result,bitoff
    def construct(self,data):
        self.frame = data["frame"]
        for coordinate in keyorder:
            setattr(self,coordinate,data[coordinate])
        for coordinate in keyorder:
            setattr(self,"raw_"+coordinate,round(self.denormalizers["raw_"+coordinate](data[coordinate])))  
        return self
    def __len__(self):
        return self.length//8
    def size(self):
        return len(self)
    def serialize(self):
        bitoff = 0
        val = 0
        for f,b in reversed(self.fields.items()):
            val,bitoff = self.insertBits(val,getattr(self,f),b,bitoff)
        bitsize = 8*struct.calcsize(self.structFormat[0])
        mask = (2**bitsize-1)
        return b''.join([((val>>(i*bitsize))&mask).to_bytes(bitsize//8,"little") for i in range(self.length//bitsize)])
    def __repr__(self):
        string = "("
        for axis in angularMap:
            if hasattr(self,axis):
                string += axis + ":" + str(getattr(self,axis))
            if hasattr(self,"raw_"+axis):
                string += "/"+str(getattr(self,axis))
            string += ", "
        string += "| "+str(self.frame)+" )"
        return string
        
def r_field4d(bitcount,framecount):
    return   OrderedDict([
            ("raw_w",bitcount),
            ("raw_z",bitcount),
            ("raw_y",bitcount),
            ("raw_x",bitcount),
            ("frame",framecount),
            ])
def field4d(bitcount,framecount):
    return   OrderedDict([
            ("raw_x",bitcount),
            ("raw_y",bitcount),
            ("raw_z",bitcount),
            ("raw_w",bitcount),
            ("frame",framecount),
            ])

def partialField4d(var,bitcount,framecount):
    return   OrderedDict([
            ("raw_x",bitcount if var == "x" else 0),
            ("raw_y",bitcount if var == "y" else 0),
            ("raw_z",bitcount if var == "z" else 0),
            ("raw_w",bitcount),
            ("frame",framecount),
            ])

sign14 = signed(14)
unsign14 = signstrip(14)
def doubleSign14(x):return min(1,2*sign14(x))
def doubleUnsign14(x):return unsign14(x/2)
class quaternion14Key(BitKeyframe):
    datamap = angularMap
    algorithm = Keyframe.raw
    structFormat = "Q"
    normalizer,denormalizer = doubleSign14,doubleUnsign14
    fields = r_field4d(14,8)
    def __init__(self):
        self.length = sum(self.fields.values())
        self.normalizers = {field:quaternion14Key.normalizer for field,c,m in zip(self.fields,self.correction,self.muloffset)}
        self.denormalizers = {field:quaternion14Key.denormalizer for field,c,m in zip(self.fields,self.correction,self.muloffset)}  
    
class quaternionInterpolationBase(BitKeyframe):
    datamap = angularMap
    algorithm = Keyframe.lerp
    structFormat = "I"    

#converters = iter(reversed([normalizePair(self.n,s,m) for s,m in zip(self.correction,self.muloffset)]))
#gernerator for normalizers
class quaternion7Interpolation(quaternionInterpolationBase):
    n = 7
    correction = (8,8,8,8)
    muloffset = (7,7,7,7)
    fields = r_field4d(7,4)
    
    
class quaternion9Interpolation(quaternionInterpolationBase):
    n = 9
    correction = (8,8,8,8)#(1,1,2,4)#(4,2,1,1)#
    muloffset = (7,7,7,7)#(1,1,2,4)#(4,2,1,1)#
    structFormat = "BBBBB"
    fields = field4d(9,4)
    
class quaternion11Interpolation(quaternionInterpolationBase):
    n = 11
    correction = (8,8,8,8)#(8,4,1,8)#(8,1,4,8)#
    muloffset = (7,7,7,7)#(7,4,1,7)#(7,1,4,7)#
    structFormat = "HHH"
    fields = field4d(11,4)
    
norm14 = normalized(14,8,7)
denorm14 = denormalize(14,8,7)
class WQuaternionUnion(quaternionInterpolationBase):
    correction = (8,8,8,8)
    muloffset = (0,0,0,0)
    datamap = angularMap
    algorithm = Keyframe.basisChoice
    normalizer,denormalizer = norm14,denorm14
    def __init__(self):
        self.fields = partialField4d(self.var,14,4)
        self.length = (14*2+4)
        self.normalizers = {"raw_"+key: self.__class__.normalizer if key == self.var or key == "w" else idem for key in keyorder}
        self.denormalizers = {"raw_"+key: self.__class__.denormalizer if key == self.var or key == "w" else idem for key in keyorder}
    
class XWQuaternionUnion(WQuaternionUnion):
    var = "x"
    datamap = angularMap#{var:angularMap[var],"w":angularMap["w"]}

class YWQuaternionUnion(WQuaternionUnion):
    var = "y"
    datamap = angularMap#{var:angularMap[var],"w":angularMap["w"]}
    
class ZWQuaternionUnion(WQuaternionUnion):    
    var = "z"
    datamap = angularMap#{var:angularMap[var],"w":angularMap["w"]}
    
typeMapping = {1:floatVectorBase,
                 2: floatRotKey,#4 coord
                 3: floatVectorKey,#3 coord
                 4: shortVectorInterpolation,#-8,+7
                 5: byteVectorInterpolation,#-8,+7
                 6: quaternion14Key,
                 7: quaternion7Interpolation,#-8,+7
                 11: XWQuaternionUnion,
                 12: YWQuaternionUnion,
                 13: ZWQuaternionUnion,
                 14: quaternion11Interpolation,#+-1
                 15: quaternion9Interpolation,#+-2
                 }

typeSize = {key:len(typing()) for key,typing in typeMapping.items()}

lerped = { **{no:False for no in [1,2,3,6]},**{yes:True for yes in [4,5,7,11,12,13,14,15]} }
#Whether it has a lerpOffset
buffered = { **{no:False for no in [1,2]},**{yes:True for yes in [3,4,5,6,7,11,12,13,14,15]}}
#Whether it gets a proper animation buffer
"""
usage = {0:"rotQLocal",1:"transLocal",2:"unknSclLocal?",3:"rotQ",4:"trans",5:"unknScl"}

["delta_rotation_quaternion","delta_location","delta_scale",
"rotation_quaternion","location","scale"]

rotQLocal - floatRotKey
rotQLocal - quaternion14Key
rotQLocal - quaternion7Interpolation
rotQLocal - XWQuaternionUnion
rotQLocal - YWQuaternionUnion
rotQLocal - ZWQuaternionUnion
rotQLocal - quaternion11Interpolation
rotQLocal - quaternion9Interpolation
transLocal - floatVectorBase
transLocal - floatVectorKey
transLocal - shortVectorInterpolation
transLocal - byteVectorInterpolation
unknSclLocal? - floatVectorBase
unknSclLocal? - floatVectorKey
unknSclLocal? - shortVectorInterpolation
unknSclLocal? - byteVectorInterpolation
rotQ - floatRotKey
rotQ - quaternion14Key
rotQ - quaternion7Interpolation
rotQ - XWQuaternionUnion
rotQ - YWQuaternionUnion
rotQ - ZWQuaternionUnion
rotQ - quaternion11Interpolation
rotQ - quaternion9Interpolation
trans - floatVectorBase
trans - floatVectorKey
trans - shortVectorInterpolation
trans - byteVectorInterpolation
unknScl - floatVectorBase
unknScl - byteVectorInterpolation

rotQLocal fKey0
rotQLocal q14ky
rotQLocal q7Ler
rotQLocal qXWLe
rotQLocal qYWLe
rotQLocal qZWLe
rotQLocal q11Le
rotQLocal q9Ler
transLocal fBase
transLocal fKey1
transLocal sLerp
transLocal bLerp
sclLocal fBase
sclLocal fKey1
sclLocal sLerp
sclLocal bLerp
rotQ fKey0
rotQ q14ky
rotQ q7Ler
rotQ qXWLe
rotQ qYWLe
rotQ qZWLe
rotQ q11Le
rotQ q9Ler
trans fBase
trans fKey1
trans sLerp
trans bLerp
scl fBase
scl bLerp

fBase transLocal
fBase sclLocal
fBase trans
fBase scl
fKey0 rotQLocal
fKey0 rotQ
fKey1 transLocal
fKey1 sclLocal
fKey1 trans
sLerp transLocal
sLerp sclLocal
sLerp trans
bLerp transLocal
bLerp sclLocal
bLerp trans
bLerp scl
q14ky rotQLocal
q14ky rotQ
q7Ler rotQLocal
q7Ler rotQ
qXWLe rotQLocal
qXWLe rotQ
qYWLe rotQLocal
qYWLe rotQ
qZWLe rotQLocal
qZWLe rotQ
q11Le rotQLocal
q11Le rotQ
q9Ler rotQLocal
q9Ler rotQ
"""