# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 13:47:06 2020

@author: AsteriskAmpersand
"""
from collections import OrderedDict
from common import Cstruct as C

class LMTVec3(C.PyCStruct): 
    fields = OrderedDict([
    	("x","float"),
    	("y","float"),
    	("z","float"),
    ])

class LMTQuadraticVector3(C.PyCStruct): 
    fields = OrderedDict([
    	("addcount","byte"),
    	("flags","byte"),
    	("s","short"),
    	("vx","float"),
    	("vy","float"),
    	("vz","float"),
    	("f","float[8]"),
    ])

class LMTVec3Frame(C.PyCStruct): 
    fields = OrderedDict([
    	("x","float"),
    	("y","float"),
    	("z","float"),
    ])

class LMTQuatized8Vec3(C.PyCStruct): 
    fields = OrderedDict([
    	("f","byte[3]"),
    	("reframe","byte"),
    ])

class LMTQuatized16Vec3(C.PyCStruct): 
    fields = OrderedDict([
    	("f","ushort[3]"),
    	("relframe","short"),
    ])

class LMTQuat3Frame(C.PyCStruct): 
    fields = OrderedDict([
    	("f","float[3]"),
    	("l","long"),
    ])

class LMTQuatFramev14(C.PyCStruct): 
    fields = OrderedDict([
    	("l1","long"),
    	("l2","long"),
    ])

class LMTQuatized32Quat(C.PyCStruct): 
    fields = OrderedDict([
    	("l","long"),
    ])

class LMTXWQuat(C.PyCStruct): 
    fields = OrderedDict([
    	("l","long"),
    ])

class LMTYWQuat(C.PyCStruct): 
    fields = OrderedDict([
    	("l","long"),
    ])

class LMTZWQuat(C.PyCStruct): 
    fields = OrderedDict([
    	("l","long"),
    ])

class LMTQuatized11Quat(C.PyCStruct): 
    fields = OrderedDict([
    	("s","short[3]"),
    ])

class LMTQuatized9Quat(C.PyCStruct): 
    fields = OrderedDict([
    	("b","byte[5]"),
    ])