# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 18:56:59 2020

@author: AsteriskAmpersand
"""
from ..struct.freedomUniteAnim import (BlockHeader, AnimDataUnkn, KeyframeShort,
                                 KeyframeShortExtended, KeyframeFloat)
from ..common import Constants as ct
from ..common import Interpolation
import struct
import bpy
from math import pi

transformStartHash = {ct.ROT_E:0x08, ct.POS:0x40, ct.SCL:0x0200}
transformStruct = {0:KeyframeShort,1:KeyframeFloat,2:KeyframeShortExtended}

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    
class UnknownTypeError(Exception):
    pass

class FreedomUniteBlock():
    def __init__(self,header,data):
        self.header = header
        self.data = data
    def serialize(self):
        return self.header.serialize()+b''.join(map(lambda x: x.serialize(),self.data))

class FreedomUniteTransform(FreedomUniteBlock):
    pass

class FreedomUniteBone(FreedomUniteBlock):
    pass

dummyBone = FreedomUniteBone(BlockHeader().construct({"blockType":0x80000000,"blockCount":0,"blockSize":12}),[])

class FreedomUniteFormat():
    def __init__(self,freedomUniteSignatureRot,freedomUniteSignaturePos,freedomUniteSignatureScl, correction = False):
        self.playerBodyCorrection = correction
        
        self.FreedomUniteFrameSignatureRot = {0:0x80120000,1:0x80220000,2:80130000}[freedomUniteSignatureRot]
        self.FreedomUniteFrameSignaturePos = {0:0x80120000,1:0x80220000,2:80130000}[freedomUniteSignaturePos]
        self.FreedomUniteFrameSignatureScl = {0:0x80120000,1:0x80220000,2:80130000}[freedomUniteSignatureScl]
        self.FreedomUniteFrameSignature = {ct.ROT_E:self.FreedomUniteFrameSignatureRot,
                                       ct.POS:self.FreedomUniteFrameSignaturePos,
                                       ct.SCL:self.FreedomUniteFrameSignatureScl}
        
        self.FreedomUniteFrameTypeRot = transformStruct[freedomUniteSignatureRot]
        self.FreedomUniteFrameTypePos = transformStruct[freedomUniteSignaturePos]
        self.FreedomUniteFrameTypeScl = transformStruct[freedomUniteSignatureScl]
        self.FreedomUniteFrameType = {ct.ROT_E:self.FreedomUniteFrameTypeRot,
                                    ct.POS:self.FreedomUniteFrameTypePos,
                                    ct.SCL:self.FreedomUniteFrameTypeScl}
                
        self.FreedomUniteRotCast = {ct.ROT_E:int,ct.POS:float,ct.SCL:int}[freedomUniteSignatureRot]
        self.FreedomUnitePosCast = {ct.ROT_E:int,ct.POS:float,ct.SCL:int}[freedomUniteSignaturePos]
        self.FreedomUniteSclCast = {ct.ROT_E:int,ct.POS:float,ct.SCL:int}[freedomUniteSignatureScl] 
        self.FreedomUniteCast = {ct.ROT_E:self.FreedomUniteRotCast,
                                ct.POS:self.FreedomUnitePosCast,
                                ct.SCL:self.FreedomUniteSclCast}
        
        self.FreedomUniteRotValueCast = {0:lambda x:round(x*4096*2/pi),
                                  1:lambda x:x/pi,
                                  2:lambda x:round(x*4096*2/pi)}[freedomUniteSignatureRot]
        self.FreedomUniteTransValueCast = {0:lambda x:round(x*15.22),
                                  1:lambda x:x,
                                  2:lambda x:round(x*15.22)}[freedomUniteSignatureRot]
    def interpolate(self,lframe,frame,rframe):
        if lframe is None:
            lInterpol = 0
        else:
            lInterpol = Interpolation.interpolation(lframe,frame,2/3)
        if rframe is None:
            rInterpol = 0
        else:
            rInterpol = Interpolation.interpolation(frame,rframe,1/3)
        return lInterpol, rInterpol
    
    def FreedomUniteFrame(self,transform,lframe,frame,rframe):
        lInterpol, rInterpol = self.interpolate(lframe,frame,rframe)
        if transform.transform == ct.ROT_E:
            if lframe is not None: lInterpol = round((lInterpol)*180/pi)
            if rframe is not None: rInterpol = round((rInterpol)*180/pi)
            value = self.FreedomUniteRotValueCast(frame.value)
        elif transform.transform == ct.POS:
            #if transform.dimension == 2:
            if lframe is not None: lInterpol -= lframe.value
            if rframe is not None: rInterpol -= frame.value
            value = self.FreedomUniteTransValueCast(frame.value)
            if transform.dimension == 1:
                #lInterpol -= 110
                #rInterpol -= 110
                value = self.FreedomUniteTransValueCast(frame.value+110*self.bodyCorrection)
        elif transform.transform == ct.SCL:
            if lframe is not None: lInterpol -= lframe.value
            if rframe is not None:rInterpol -= frame.value      
            value = frame.value
        return self.FreedomUniteFrameType[transform.transform]().construct({
                                "keyvalue": self.FreedomUniteCast[transform.transform](value),
                                "frameIndex":self.FreedomUniteCast[transform.transform](frame.index),
                                "lInterpol":self.FreedomUniteCast[transform.transform](lInterpol),
                                "rInterpol":self.FreedomUniteCast[transform.transform](rInterpol)
                                })
    def createFreedomUniteTransform(self,transform):        
        signature = transformStartHash[transform.transform]
        signature = (signature << transform.dimension) | self.FreedomUniteFrameSignature[transform.transform]
        count = len(transform.keyframes)
        frames = [self.FreedomUniteFrame(transform,lframe,frame,rframe) 
                  for lframe,frame,rframe in zip([None]+list(transform.keyframes[:-1]),
                                                 transform.keyframes,
                                                 list(transform.keyframes[1:]+[None]))]
        data = b''.join(map(lambda x: x.serialize(),frames))
        header = BlockHeader()
        size = len(header) + len(data)
        header.construct({"blockType":signature,"blockCount":count,"blockSize":size})
        return FreedomUniteTransform(header,frames)
    def createFreedomUniteBone(self,obj):
        transforms = []
        for transform in obj:
            if transform.transform not in transformStartHash:
                raise UnknownTypeError("Transform Type %s in %s Not Compatible with FreedomUnite"%
                                       (ct.inverse_transform[transform.transform]),obj.name)
            transforms.append(self.createFreedomUniteTransform(transform))
        count = len(transforms)
        data = b''.join(map(lambda x:x.serialize(),transforms))        
        r = 0x80000000
        for t in transforms:r |= t.header.blockType&0xFFFF
        ortype = r
        header = BlockHeader()
        size = len(data)+len(header)
        header.construct({"blockType":ortype,"blockCount":count,"blockSize":size})
        return FreedomUniteBone(header,transforms)
    def serializeAnimation(self,animation,skeletonSize,startingBone):
        result = b''        
        before = []
        after = []
        currentLow = 0
        current = startingBone
        for obj in animation:
            ix = obj.boneName
            if type(ix) is int and ix > 0:#>= if this should be exported
                self.bodyCorrection = self.playerBodyCorrection*(ix==2)# Re-Enable if correction should be local
                if ix < startingBone:
                    for i in range(currentLow,ix):
                        before.append(dummyBone)
                    before.append(self.createFreedomUniteBone(obj))
                    currentLow = ix+1
                else:
                    for i in range(current,ix):
                        after.append(dummyBone)
                    after.append(self.createFreedomUniteBone(obj))
                    current = ix+1
        if before:
            for i in range(current,skeletonSize):
                after.append(dummyBone)
            current = currentLow
        bones = before+after
        count = len(bones)
        data = b''.join(map(lambda x: x.serialize(),bones))
        header = BlockHeader()
        unkn = AnimDataUnkn()
        size = len(data)+len(header)+len(unkn)  
        result+=header.construct({"blockType":0x80000002,"blockCount":count,"blockSize":size}).serialize()
        result+=unkn.construct({"unknown":[0,0]}).serialize()
        result+=data
        return current, result
    def serializeExchangeFormat(self,exchangeAnimation,skeletonSize,startingBone = 0):
        exception = False
        animationResult = b''
        offset = 0
        offsets = []
        exchangeAnimation.sort()
        for animation in exchangeAnimation:
            try:
                startingBone,animation = self.serializeAnimation(animation,skeletonSize,startingBone)                
                offset += len(animation)
                offsets.append(offset)
                animationResult += animation
            except UnknownTypeError as e:
                exception = True
                print("Animation %s: %s"%(animation.name,str(e)))
        if exception:
            ShowMessageBox("Partial Errors found during Export", "Errors exporting", 'ERROR')
        return animationResult, struct.pack("i"*len(offsets),*offsets)
    def getSkeletonSize(self,skeleton):
        return len(skeleton.data.bones)-1
#08 00 00 02 - Animation Header
# > 08 00 XX XX - Bone Animation: 
#                                   OR of all Transform Bitflags
# >     > 08 00 YY YY - Transform Listing
#                                   00 08/00 10/00 20 Rotation 
#                                   00 40/00 80/01 00 Translation 
#                                   02 00/04 00/08 00 Scaling 