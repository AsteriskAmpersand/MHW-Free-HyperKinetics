# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 00:06:50 2021

@author: AsteriskAmpersand
"""
from pathlib import Path

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from ..blender.lmt_tools import TIMLControllerCheck
from ..blender.timl_controller import geometryitems
from ..blender.nodetree import freeHKNodeOps as nOps
from ..blender.timl_importer import TIMLFileLoad,EFXFileLoad,remapAnalyzer
from ..struct.TIML import parseTIML,parseEFX

importPropSetup = []
props = [(bname+axis.lower(),pname+" "+axis+" "+"Map") for bname,pname in zip(["trans","rot","scl"],["Translation","Rotation","Scale"]) 
     for axis in ["X","Y","Z"]]
defaults = "m8E8AFE06 mF98DCE90 m60849F2A mF105BBE3 m86028B75 m1F0BDACF m9486DF23 mE381EFB5 m7A88BE0F".split(" ")
importPropSetup.append("""advanced_remap = bpy.props.BoolProperty(name = "Estimate Remap",
                                            description = "Estimate remapping from actions present",
                                            default = True)""")
for (bname,pname),default in zip(props,defaults):
    importPropSetup.append('%s = EnumProperty(name = "%s",items = geometryitems,default = "%s")'%(bname,pname,default))
importPropSetup.append("""clear_scene = BoolProperty(
        name = "Clear actions before import.",
        description = "Clears all actions and the animation tree before importing",
        default = True)""")
importPropSetup.append("""reuse_tree = BoolProperty(
        name = "Use Selected Tree",
        description = "Uses currently selected tree for importing.",
        default = False)""")
importPropSetup.append("""hide = BoolProperty(
        name = "Collapse Tree Nodes",
        description = "Collapses Tree Nodes to Save Space.",
        default = True)""")

def parseRemap(settings):
    mapper = {}    
    propList = ["transx","transy","transz","rotx","roty","rotz","sclx","scly","sclz"]
    settingList = [getattr(settings,prop) for prop in propList]
    propTuples = [(string,i) for string in ["location","rotation_euler","scale"] for i in range(3) ]
    
    mapper = {s:p for s,p in zip(settingList,propTuples)}
    reverse_mapper = {p:s for s,p in zip(settingList,propList)}                                    
    return mapper,reverse_mapper

class ImporterBase():
    def draw(self,context):
        layout = self.layout
        layout.prop(self,"clear_scene")
        layout.prop(self,"reuse_tree")
        layout.prop(self,"advanced_remap")
        layout.prop(self,"hide")
        if not self.advanced_remap:
            for prop in ["trans","rot","scl"]:
                for axis in ["x","y","z"]:
                    layout.prop(self,prop+axis)
    def execute(self,context):
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = 1
        if self.filepath:
            if self.clear_scene:
                nOps.clearScene()
            if self.reuse_tree:
                tree = nOps.getCurrentTree(self.hide)
            else:
                tree = nOps.getNewTree(Path(self.filepath).stem,self.hide)
            timl = self.parser(self.filepath)
            if not self.advanced_remap:
                mapper,rmapper = parseRemap(self)
                remapper = lambda x: (mapper,rmapper)
            else:
                remapper = remapAnalyzer
            loaderResult = self.loader(self.filepath,timl,remapper,tree)
            self.checker(bpy.context,loaderResult)
        return {'FINISHED'}

class TIMLImporter(Operator,ImportHelper,ImporterBase):
    bl_idname = "freehk.import_timl"
    bl_label = "Import MHW TIML file (.timl)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Import TIML into FreeHK Tree"
    
    filename_ext = ".timl"
    filter_glob = StringProperty(default="*.timl", options={'HIDDEN'}, maxlen=255)
    
    for p in importPropSetup:
        exec(p)
    
    @staticmethod
    def parser(*args,**kwargs): return parseTIML(*args,**kwargs)
    @staticmethod
    def loader(*args,**kwargs): return TIMLFileLoad(*args,**kwargs)
    @staticmethod
    def checker(*args,**kwargs): return TIMLControllerCheck(*args,**kwargs)
   
class EFXImporter(Operator,ImportHelper,ImporterBase):
    bl_idname = "freehk.import_efx"
    bl_label = "Import MHW EFX TIML file (.efx)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}    
    bl_description = "Import TIML into FreeHK Tree"
    
    filename_ext = ".efx"
    filter_glob = StringProperty(default="*.efx", options={'HIDDEN'}, maxlen=255)
    
    for p in importPropSetup:
        exec(p)
        
    @staticmethod
    def parser(*args,**kwargs): return parseEFX(*args,**kwargs)
    @staticmethod
    def loader(*args,**kwargs): return EFXFileLoad(*args,**kwargs)
    @staticmethod
    def checker(*args,**kwargs): return TIMLControllerCheck(*args,**kwargs)

classes = [
    TIMLImporter,EFXImporter#,EFXExporter,TIMLExporter
]

def importer_menu_ops(self, context):
    self.layout.operator(TIMLImporter.bl_idname, text="MHW TIML (.timl)")    
    self.layout.operator(EFXImporter.bl_idname, text="MHW EFX (.efx)")
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
