# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 18:56:59 2020

@author: AsteriskAmpersand
"""
from ..struct.frontierAnim import (BlockHeader, AnimDataUnkn, KeyframeShort,
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

class FrontierBlock():
    def __init__(self,header,data):
        self.header = header
        self.data = data
    def serialize(self):
        return self.header.serialize()+b''.join(map(lambda x: x.serialize(),self.data))

class FrontierTransform(FrontierBlock):
    pass

class FrontierBone(FrontierBlock):
    pass

dummyBone = FrontierBone(BlockHeader().construct({"blockType":0x80000000,"blockCount":0,"blockSize":12}),[])

class FrontierFormat():
    def __init__(self,frontierSignatureRot,frontierSignaturePos,frontierSignatureScl, correction = False):
        self.playerBodyCorrection = correction
        
        self.FrontierFrameSignatureRot = {0:0x80120000,1:0x80220000,2:80130000}[frontierSignatureRot]
        self.FrontierFrameSignaturePos = {0:0x80120000,1:0x80220000,2:80130000}[frontierSignaturePos]
        self.FrontierFrameSignatureScl = {0:0x80120000,1:0x80220000,2:80130000}[frontierSignatureScl]
        self.FrontierFrameSignature = {ct.ROT_E:self.FrontierFrameSignatureRot,
                                       ct.POS:self.FrontierFrameSignaturePos,
                                       ct.SCL:self.FrontierFrameSignatureScl}
        
        self.FrontierFrameTypeRot = transformStruct[frontierSignatureRot]
        self.FrontierFrameTypePos = transformStruct[frontierSignaturePos]
        self.FrontierFrameTypeScl = transformStruct[frontierSignatureScl]
        self.FrontierFrameType = {ct.ROT_E:self.FrontierFrameTypeRot,
                                    ct.POS:self.FrontierFrameTypePos,
                                    ct.SCL:self.FrontierFrameTypeScl}
                
        self.FrontierRotCast = {ct.ROT_E:int,ct.POS:float,ct.SCL:int}[frontierSignatureRot]
        self.FrontierPosCast = {ct.ROT_E:int,ct.POS:float,ct.SCL:int}[frontierSignaturePos]
        self.FrontierSclCast = {ct.ROT_E:int,ct.POS:float,ct.SCL:int}[frontierSignatureScl] 
        self.FrontierCast = {ct.ROT_E:self.FrontierRotCast,
                                ct.POS:self.FrontierPosCast,
                                ct.SCL:self.FrontierSclCast}
        
        self.FrontierRotValueCast = {0:lambda x:round(x*4096*2/pi),
                                  1:lambda x:x/pi,
                                  2:lambda x:round(x*4096*2/pi)}[frontierSignatureRot]
        self.FrontierTransValueCast = {0:lambda x:round(x*15.22),
                                  1:lambda x:x,
                                  2:lambda x:round(x*15.22)}[frontierSignatureRot]
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
    
    def FrontierFrame(self,transform,lframe,frame,rframe):
        lInterpol, rInterpol = self.interpolate(lframe,frame,rframe)
        if transform.transform == ct.ROT_E:
            if lframe is not None: lInterpol = round((lInterpol)*180/pi)
            if rframe is not None: rInterpol = round((rInterpol)*180/pi)
            value = self.FrontierRotValueCast(frame.value)
        elif transform.transform == ct.POS:
            #if transform.dimension == 2:
            if lframe is not None: lInterpol -= lframe.value
            if rframe is not None: rInterpol -= frame.value
            value = self.FrontierTransValueCast(frame.value)
            if transform.dimension == 1:
                #lInterpol -= 110
                #rInterpol -= 110
                value = self.FrontierTransValueCast(frame.value+110*self.bodyCorrection)
        elif transform.transform == ct.SCL:
            if lframe is not None: lInterpol -= lframe.value
            if rframe is not None:rInterpol -= frame.value      
            value = frame.value
        return self.FrontierFrameType[transform.transform]().construct({
                                "keyvalue": self.FrontierCast[transform.transform](value),
                                "frameIndex":self.FrontierCast[transform.transform](frame.index),
                                "lInterpol":self.FrontierCast[transform.transform](lInterpol),
                                "rInterpol":self.FrontierCast[transform.transform](rInterpol)
                                })
    def createFrontierTransform(self,transform):        
        signature = transformStartHash[transform.transform]
        signature = (signature << transform.dimension) | self.FrontierFrameSignature[transform.transform]
        count = len(transform.keyframes)
        frames = [self.FrontierFrame(transform,lframe,frame,rframe) 
                  for lframe,frame,rframe in zip([None]+list(transform.keyframes[:-1]),
                                                 transform.keyframes,
                                                 list(transform.keyframes[1:]+[None]))]
        data = b''.join(map(lambda x: x.serialize(),frames))
        header = BlockHeader()
        size = len(header) + len(data)
        header.construct({"blockType":signature,"blockCount":count,"blockSize":size})
        return FrontierTransform(header,frames)
    def createFrontierBone(self,obj):
        transforms = []
        for transform in obj:
            if transform.transform not in transformStartHash:
                raise UnknownTypeError("Transform Type %s in %s Not Compatible with Frontier"%
                                       (ct.inverse_transform[transform.transform]),obj.name)
            transforms.append(self.createFrontierTransform(transform))
        count = len(transforms)
        data = b''.join(map(lambda x:x.serialize(),transforms))        
        r = 0x80000000
        for t in transforms:r |= t.header.blockType&0xFFFF
        ortype = r
        header = BlockHeader()
        size = len(data)+len(header)
        header.construct({"blockType":ortype,"blockCount":count,"blockSize":size})
        return FrontierBone(header,transforms)
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
                    before.append(self.createFrontierBone(obj))
                    currentLow = ix+1
                else:
                    for i in range(current,ix):
                        after.append(dummyBone)
                    after.append(self.createFrontierBone(obj))
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