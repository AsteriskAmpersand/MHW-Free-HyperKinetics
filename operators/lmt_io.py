# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 05:56:32 2021

@author: AsteriskAmpersand
"""
import bpy 
from bpy.props import StringProperty,BoolProperty,EnumProperty
from bpy_extras.io_utils import ImportHelper,ExportHelper
from bpy.types import Operator

import re

from .timl_io import ImporterBase,importPropSetup
from ..struct.Lmt import parseLMT,parseSectionalLMT
from ..blender.timl_controller import geometryitems
from ..blender.lmt_importer import LMTFileLoad
from ..blender.lmt_tools import TIMLControllerCheck
from ..blender.blenderOps import stripBuffers
from ..blender.tetherOps import transferTether
from ..blender.nodetree.freeHKNodeOps import LMTACTION
from ..blender.nodetree.freeHKNodeTools import fetchTerminalParents

class LMTImporter(Operator,ImportHelper,ImporterBase):
    bl_idname = "freehk.import_lmt"
    bl_label = "Import MHW LMT file (.lmt)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}    
    bl_description = "Import LMT into FreeHK Tree"
    
    filename_ext = ".lmt"
    filter_glob = StringProperty(default="*.lmt", options={'HIDDEN'}, maxlen=255)
    
    for p in importPropSetup:exec(p)
    
    anim_filter = BoolProperty(name="Filter Animation Range",
                               description="Only imports a specified subset of the animations in the file",
                               default = False)
    anim_filter_string = StringProperty(name="Animation Filter",
                                        description="Range of animations ids given with a dash and split by commas. (E.g. '1-12,33-44')",
                                        default = "")
    include_parents = BoolProperty(name="Include Parents of Filtered Entries",
                               description="Include the parent entry of implicit animation blocks instead of creating new instances",
                               default = False)
    include_siblings = BoolProperty(name="Include Siblings and Children of Filtered Entries",
                               description="Include the sibling and children entries of implicit animation blocks",
                               default = False)
    anim_skeleton = BoolProperty(name="Tether to Skeleton",
                                 description="Tether all imported animations to existing skeleton",
                                 default=False)
    strip_buffer = BoolProperty(name="Remove Buffer Type",
                                 description="Set all buffer types to be recalculated",
                                 default=False)
    
    def parseFilter(self):
        flt = re.compile("[0-9]+(\-[0-9]+)?(,[0-9]+(\-[0-9]+)?)*")
        filterString = self.anim_filter_string.replace(" ","")
        matches = flt.match(filterString)
        if not matches:
            raise ValueError("Improper Filter String")
        base = set()
        for s in (set(range(int(group.split("-")[0]),int(group.split("-")[-1])+1)) for group in filterString.split(",")):
            base = base.union(s)
        return sorted(base)
    
    #Skeleton target is scene wide property and has to be drawn explicitly (coincidentally this allows "remembering")
    def draw(self,context):
        super().draw(context)
        layout = self.layout
        #layout.prop(self,"angle_convert")
        layout.prop(self,"anim_filter")
        layout.prop(self,"strip_buffer")
        if self.anim_filter:
            r = layout.row()
            r.prop(self,"include_parents")
            r.prop(self,"include_siblings")            
            layout.prop(self,"anim_filter_string")
            
        layout.prop(self,"anim_skeleton")
        if self.anim_skeleton:
            layout.prop(context.scene,"freehk_tether")
    def parser(self,filepath): 
        if self.anim_filter:
            indexSet = self.parseFilter()
            return parseSectionalLMT(filepath,indexSet,self.include_parents,self.include_siblings)
        else:
            return parseLMT(filepath)
    
    def collectActions(self,node):
        actionNodes = fetchTerminalParents(node,lambda x: "LMT" in x.bl_idname)
        return set((node.input_action for node in actionNodes if node.bl_idname == LMTACTION and node.input_action is not None))
        
    
    @staticmethod
    def loader(*args,**kwargs): return LMTFileLoad(*args,**kwargs)
    def checker(self,context,node,*args,**kwargs): 
        TIMLControllerCheck(context)
        if self.anim_skeleton:
            target_tether = context.scene.freehk_tether    
            target_actions = self.collectActions(node)
            transferTether(target_actions,target_tether)
        node.inject = self.anim_filter
        if self.strip_buffer:
            target_actions = self.collectActions(node)
            for action in target_actions:
                stripBuffers(action)
        return 


classes = [
    LMTImporter
]

def importer_menu_ops(self, context):
    self.layout.operator(LMTImporter.bl_idname, text="MHW LMT (.lmt)")   
def exporter_menu_ops(self, context):
    pass
#    self.layout.operator(TIMLExporter.bl_idname, text="MHW TIML (.timl)")
#    self.layout.operator(EFXExporter.bl_idname, text="MHW EFX (.efx)")

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.INFO_MT_file_import.append(importer_menu_ops)
    bpy.types.INFO_MT_file_export.append(exporter_menu_ops)
    
def unregister():
    bpy.types.INFO_MT_file_import.remove(importer_menu_ops)
    bpy.types.INFO_MT_file_export.remove(exporter_menu_ops)
    for cls in classes:
        bpy.utils.unregister_class(cls)
