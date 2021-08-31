# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 21:52:30 2021

@author: Asterisk
"""
import bpy
from .binary_notes import NOTES_OT_actions, NOTES_OT_clearList, NOTES_UL_items, NOTES_PT_objectList
from .binary_notes import intToBin, binToInt

def and_op(x,y):
    return x & y
def or_op(x,y):
    return x | y
def xor_op(x,y):
    return x ^ y

def intInputUpdate(self,context):
    if self.binary_string != intToBin(self.int_input):
        self.binary_string  = intToBin(self.int_input)

def binaryInputUpdate(self,context):
    try:
        inbin = binToInt(self.binary_string)
        if self.int_input != inbin:
            self.int_input = inbin
        binstr = intToBin(inbin)
        if self.binary_string != binstr:
            self.binary_string = binstr
    except:
        self.binary_string = intToBin(0)
        self.int_input = 0


def binaryTargetUpdate(self,context):
    try:
        inbin = binToInt(self.binary_target)
        binstr = intToBin(inbin)
        if self.binary_target != binstr:
            self.binary_target = binstr
    except:
        self.binary_target = intToBin(0)

def calcResult(self):
    f = {"+":or_op,"x":and_op,"xor":xor_op}[self.operation]
    return f(self.int_input,binToInt(self.binary_target))

def calcBinaryResult(self):
    return intToBin(calcResult(self))

def calcIntResult(self):
    return calcResult(self)

def setBin(self,val=None):
    if val is None:
        return
    if val != self.binary_result:
        self.binary_result = val

def setInt(self,val=None):
    if val is None:
        return
    if val != self.int_result:
        self.int_result = val

class BitToolsProperties(bpy.types.PropertyGroup):
    #nextAction = bpy.props.PointerProperty(name = "Next Animation", type="Action")
    name = bpy.props.StringProperty(name = "Operation Label",default = "")
    int_input = bpy.props.IntProperty(name = "Integer Input",update = intInputUpdate,default = 0)
    binary_string = bpy.props.StringProperty(name = "Binary Input", update = binaryInputUpdate, default = intToBin(0))
    operation = bpy.props.EnumProperty(name = "Binary Operation",
                                       items = [("+","Or","Or"),
                                                ("x","And","And"),
                                                ("xor",'Xor',"Xor"),
                                                ],default = "+")
    binary_target = bpy.props.StringProperty(name = "Binary Operator",update = binaryTargetUpdate, default = intToBin(0))
    binary_result = bpy.props.StringProperty(name = "Binary Result", get = calcBinaryResult,set = lambda s,y: setBin(calcBinaryResult(s)))
    int_result = bpy.props.IntProperty(name = "Integer Result", get = calcIntResult,set = lambda s,y: setInt(calcIntResult(s)))
    #bool_test = bpy.props.BoolVectorProperty(name="Test",size=8)
    
class BitTools(NOTES_PT_objectList,bpy.types.Panel):
    bl_category = "MHW Tools"
    bl_idname = "panel.bitutils"
    bl_label = "Bit Edit Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    addon_key = __package__.split('.')[0]
    def draw(self, context):
        layout = self.layout
        
        layout.prop(context.scene.freehk_binary,"int_input")
        c = layout.column(align=True)
        c.prop(context.scene.freehk_binary,"binary_string")        
        c.prop(context.scene.freehk_binary,"operation")
        c.prop(context.scene.freehk_binary,"binary_target")
        
        c = layout.column(align=True)
        r = c.row(align=True)
        r.prop(context.scene.freehk_binary,"binary_result")
        r = c.row(align=True)
        r.prop(context.scene.freehk_binary,"int_result")
        layout.separator()
        super().draw(context)
        
classes = [BitToolsProperties,BitTools,
           NOTES_OT_actions, NOTES_OT_clearList, NOTES_UL_items]


def register():    
    for cl in classes:
        bpy.utils.register_class(cl)
    bpy.types.Scene.freehk_binary = bpy.props.PointerProperty(type = BitToolsProperties)
    bpy.types.Scene.freehk_notes = bpy.props.CollectionProperty(type=BitToolsProperties)
    bpy.types.Scene.freehk_notes_index = bpy.props.IntProperty()
    bpy.types.Scene.freehk_notes_compact = bpy.props.BoolProperty(name = "Compact")
    
def unregister(): 
    del bpy.types.Scene.freehk_notes_compact
    del bpy.types.Scene.freehk_binary
    del bpy.types.Scene.freehk_notes_index
    for cl in classes:
        bpy.utils.unregister_class(cl)