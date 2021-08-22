# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 11:52:09 2021

@author: AsteriskAmpersand
"""

import bpy
from bpy.types import Node
from .freeHKNodes import FreeHKNode
from ...struct import TIML,EFX,Lmt,ExtensibleList

try:
    from ...app_license.license import signature
    licensed = True
    print("FreeHK Commercial License")
except:
    signature = lambda: True
    licensed = False
    print("FreeHK Free License")

class TIMLDataNode(Node, FreeHKNode):
    '''TIML Data Node'''
    bl_idname = 'TIMLDataNode'
    bl_label = "TIML Data Node"
    bl_icon = 'LAMP_DATA'
    __mainInput__ = "TIML Animation"
    
    name = bpy.props.StringProperty(name="Name")
    unkn1 = bpy.props.IntProperty(name="Unknown 1")
    unkn2 = bpy.props.IntProperty(name="Unknown 2")
    animLength = bpy.props.IntProperty(name="Animation Length",min = 0)
    loopStartPoint = bpy.props.IntProperty(name="Loop Start Point")
    loopControl = bpy.props.EnumProperty(name="Loop Control",
		description="Decide to install, ignore, or defer new addon update",
		items=[
			("0","No Loop","Don't Loop"),
			("1","Loop", "Loop"),
            ("2","Unkn", "????"),
			("3","UnknLoop","????")
		],)
    def init(self, context):
        #self.inputs.new('CustomSocketType', "Hello")
        inputs = self.inputs.new('FreeHKTimlSocket',"TIML Animation","TIML_Animation")
        inputs.link_limit = 0
        self.outputs.new('FreeHKTimlDataSocket', "TIML Data","TIML_Data")
    def draw_buttons(self, context, layout):
        layout.prop(self, "name")
        layout.prop(self, "unkn1")
        layout.prop(self, "unkn2")
        layout.prop(self, "animLength")
        layout.prop(self, "loopStartPoint")
        layout.prop(self, "loopControl")
    def basicStructure(self):
        return TIML.TIML_Data().construct({"offset":None,"count":None,
                                     "dataIx0":self.unkn1,"dataIx1":self.unkn2,
                                     "animationLength":self.animLength,"loopStartPoint":self.loopStartPoint,
                                     "loopControl":int(self.loopControl),
                                     "labelHash":0x8F64576D if not licensed else signature()})

class TIMLEntryNode(Node, FreeHKNode):
    '''TIML Entry Node'''
    bl_idname = 'TIMLEntryNode'
    bl_label = "TIML Entry Node"
    bl_icon = 'LAMP_DATA'
    __mainInput__ = "TIML Data"

    entryNum = bpy.props.IntProperty(name="Entry Number")
    def init(self, context):
        self.inputs.new('FreeHKTimlDataSocket',"TIML Data","TIML_Data")
        #inputs.link_limit = 0
        self.outputs.new('FreeHKTimlEntrySocket', "TIML Entry","TIML_Entry")
        #TODO - Count existing TIML nodes and set the sstarting value of entryNum to that
    def draw_buttons(self, context, layout):
        layout.prop(self, "entryNum")
    def basicStructure(self):
        return self
    def extend(self,data):
        if not data:
            return None
        data = data[0]
        data.id = self.entryNum
        return data

class EFXEntryNode(Node, FreeHKNode):
    '''EFX Data Node'''
    bl_idname = 'EFXEntryNode'
    bl_label = "EFX Entry Node"
    bl_icon = 'LAMP_DATA'
    __mainInput__ = "TIML Data"

    entryNum = bpy.props.IntProperty(name="EFX Entry Number")
    def init(self, context):
        #self.inputs.new('CustomSocketType', "Hello")
        inputs = self.inputs.new('FreeHKTimlDataSocket',"TIML Data","TIML_Data")
        inputs.link_limit = 0
        self.outputs.new('FreeHKEFXEntrySocket', "EFX Entry","EFX_Entry")
        #TODO - Count existing EFX nodes and set the sstarting value of entryNum to that
    def draw_buttons(self, context, layout):
        layout.prop(self, "entryNum")
    def basicStructure(self):
        l = ExtensibleList.ExtensibleList()
        l.id = self.entryNum
        return l

def flagMake(flags):
    return sum((f<<(7-ix) for ix,f in enumerate(flags)))

class LMTEntryNode(Node, FreeHKNode):
    '''LMT Data Node'''
    bl_idname = 'LMTEntryNode'
    bl_label = "LMT Entry Node"
    bl_icon = 'LAMP_DATA'
    __mainInput__ = None

    entryNum = bpy.props.IntProperty(name="Id")
    #transVec = bpy.props.FloatVectorProperty(size=3,name="Trans",subtype = 'TRANSLATION')
    #quatLerpVec = bpy.props.FloatVectorProperty(size=4,name="Quat",subtype = 'QUATERNION')
    loopFrame = bpy.props.IntProperty(name="Looping Frame",default = 0  )
    byteflag = bpy.props.BoolVectorProperty(size=8,name="Flags")
    byteflag2 = bpy.props.BoolVectorProperty(size=8,name="Flags")
    def init(self, context):
        #self.inputs.new('CustomSocketType', "Hello")
        self.inputs.new('FreeHKAnimationSocket',"LMT Animation","LMT_Animation")
        self.inputs.new('FreeHKTimlDataSocket',"TIML Data","TIML_Data")
        self.outputs.new('FreeHKAnimationEntrySocket', "LMT Entry","LMT_Entry")
        #TODO - Count existing EFX nodes and set the sstarting value of entryNum to that
    def draw_buttons(self, context, layout):        
        layout.prop(self, "entryNum")
        #layout.prop(self, "frameCount")
        layout.prop(self, "loopFrame")
        #layout.prop(self, "transVec")
        #layout.prop(self, "quatLerpVec")
        layout.prop(self, "byteflag")
        layout.prop(self, "byteflag2")
    def basicStructure(self):
        entry = Lmt.LMTActionHeader()
        entry.construct({"fcurveOffset":None,"fcurveCount":None,"frameCount":None,
                         "loopFrame":self.loopFrame,"Flags":flagMake(self.byteflag),"Flags2":flagMake(self.byteflag2),
                         "NULL0":[0,0,0],"Vec0":[0,0,0,0],"Vec2":[0,0,0,1],"NULL2":[0,0],"NULL3":[0,0,0,0,0],
                         "timlOffset":None
                         })
        return entry
    def export(self,error_handler):
        self.error_handler = error_handler
        self.error_handler.takeOwnership(self)
        if self.inputs["LMT Animation"]:
            actionNodes,error_handler = self.validSocketInputs(self.inputs["LMT Animation"],error_handler)
        else:
            actionNodes = []            
        if self.inputs["TIML Data"]:
            timl,error_handler = self.validSocketInputs(self.inputs["TIML Data"],error_handler)
        else:
            timl = None
            
        self.structure = self.basicStructure()
        #Stop if Graph error_handler found
        if not error_handler.verifyGraph():
            return []
        if timl:
            timl = next(iter(timl)).export(error_handler)
        if actionNodes:
            actionNode = next(iter(actionNodes)).export(error_handler)
        self.structure = self.structure.extend(actionNode,timl)
        #Stop if FCurve or Action error_handler found
        if not error_handler.verifyAnimations():
            return []  
        return self.structure

classes = [
    TIMLDataNode, LMTEntryNode, EFXEntryNode,  TIMLEntryNode, 
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
