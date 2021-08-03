# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 05:24:15 2020

@author: AsteriskAmpersand
"""

from ..common.Cstruct import PyCStruct
from collections import OrderedDict

FrontierTransforms = {()}

class BlockHeader(PyCStruct):
    fields = OrderedDict([
                        ("blockType","uint"),
                        ("blockCount","uint"),
                        ("blockSize","uint"),
                          ])
class AnimDataUnkn(PyCStruct):
    fields = OrderedDict([("unknown","uint[2]")])
baseFields = ["keyvalue","frameIndex","lInterpol","rInterpol"]
class KeyframeShort(PyCStruct):
    fields = OrderedDict([(field,"short") for field in baseFields])
class KeyframeShortExtended(PyCStruct):
    fields = OrderedDict([(field,"short") for field in baseFields]+
                         [("unkn5","short"),("unkn6","short")])    
    def construct(self,data):
        if "unkn5" not in data:
            data["unkn5"] = 0
        if "unkn6" not in data:
            data["unkn6"] = 0  
        return super().construct(data)
class KeyframeFloat(PyCStruct):
    fields = OrderedDict([(field,"float") for field in baseFields])    

#08 00 00 02 - Animation Header
# > 08 00 XX XX - Bone Animation: 
#                                   OR of all Transform Bitflags
# >     > 08 00 YY YY - Transform Listing
#                                   00 08/00 10/00 20 Rotation 
#                                   00 40/00 80/01 00 Translation 
#                                   02 00/04 00/08 00 Scaling 
"""
typedef struct{
    uint unknown[2];
}AnimDataUnkn;

typedef struct {
    uint blockType; 
    uint blockCount; 
    uint blockSize; 
} BlockHeader;

typedef struct{
    short keyvalue;// x/4096*4/Pi rad => 4096*Pi/4
    short frameIndex;
    short easingInterpol;//Does easing but mechanism is insane and not meant for humans
    short interpolEasing;//Does easing but mechanism is insane and not meant for humans
}MiniDataBlock1;

typedef struct{
    float keyvalue;// Half turns: keyvalue * 3.14159265358979323
    float frameIndex;
    float easingInterpol;
    float interpolEasing;
}MiniDataBlock2;

typedef struct{
    short keyvalue;// x/4096*4/Pi rad => 4096*Pi/4
    short frameIndex;
    short easingInterpol;//Does easing but mechanism is insane and not meant for humans
    short interpolEasing;//Does easing but mechanism is insane and not meant for humans
    short unkn5;
    short unkn6;
}MiniDataBlock3;
"""