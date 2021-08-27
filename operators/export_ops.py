# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 03:13:08 2021

@author: AsteriskAmpersand
"""

import bpy
import os
from bpy.props import EnumProperty
from ..struct import TIML
from ..blender.nodetree.freeHKNodeOps import LMTFILE,EFXFILE,TIMLFILE,FILE
from ..blender.nodetree.freeHKNodes import globalCacheClear

class TreeExporter(bpy.types.Operator):
    bl_idname = "freehk.export"
    bl_label = "Export MHW Free HK Tree (.timl/.efx/.lmt)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Export FreeHK Tree"
    addon_key = __package__.split('.')[0]
    
    mode = EnumProperty(name = "Exporter Modes",
                        description = "Exporter Operation Mode",
                        items = [
                            ("all","All","Export all Nodes",),
                            ("selected","Selection","Export only Selected Nodes"),
                            ("lmt","LMT","Export only LMT Nodes"),
                            ("efx","EFX","Export only EFX Nodes"),
                            ("timl","TIML","Export only TIML Nodes"),
                            ("json","JSON","Export only JSON Nodes"),
                            ],
                        default = "all")
    @classmethod
    def poll(cls,context):
        return context.space_data and hasattr(context.space_data,"node_tree") and context.space_data.node_tree
    def LMTExport(self,node):
        self.FileExport(node)
    def TIMLExport(self,node):
        self.FileExport(node)
    def FileExport(self,node):        
        nodeStructure = node.export()
        if node.inject:
            try:
                masterFile = type(nodeStructure)().parseFile(node.filepath)
                masterFile.injectFile(nodeStructure)
                nodeStructure = masterFile
            except IndexError:
                node.error_handler.takeOwnership(node)
                node.error_handler.append("G_INJECTION_ENTRY_COUNT",node.name,masterFile.entryCount())
                node.error_handler.logUnsolved()        
        if self.addon_props.output_log:
            node.error_handler.writeLog(node.filepath,self.addon_props.output_log_folder)
        node.error_handler.display()
        if node.error_handler.verifyExport():            
            filedata = nodeStructure.serialize()
        
        outpath = os.path.realpath(bpy.path.abspath(node.filepath))
        with open(outpath,"wb") as outf:
            outf.write(filedata)
    
    def generateTIML(self,timlData):
        timl = TIML.TIML().construct()
        timl.extend(timlData)
        return timl        
        
    def EFXExport(self,node):
        self.FileExport(node)
        """
        subTimls = node.export()
        with open(node.filepath,"rb") as inf:
            file = inf.read()
            timlOffsets = TIML.getTimlOffsets(file)
            start = 0
            data = b''
            if node.inject:
                subTimls = sorted(subTimls,key=lambda x: x.id)
            for ix,timlData in enumerate(subTimls):
                if node.inject:
                    offset = timlOffsets[timlData.id]
                else:
                    offset = timlOffsets[ix]
                data += file[start:offset-4]
                originalLength = TIML.parseLength(file,offset)
                start = offset+originalLength
                timlData = self.generateTIML(timlData).serialize()
                data += TIML.writeLength(len(timlData))
                data += timlData
            data += file[start:]            
        with open(node.filepath,"wb") as outf:
            outf.write(data)       
        """
    def execute(self,context):
        addon = context.user_preferences.addons[self.addon_key]
        self.addon_props = addon.preferences
        globalCacheClear()
        for node in self.getOutputNodes(context):
            try:
                #node.cleanup()
                #try:
                if node.bl_idname == TIMLFILE:
                    self.TIMLExport(node)
                if node.bl_idname == EFXFILE:
                    self.EFXExport(node)
                if node.bl_idname == LMTFILE:
                    self.LMTExport(node)
                #except Exception as e:
                #    raise
                #finally:
                #    node.cleanup()
                #node.cleanup()
            except:
                pass
            #finally:
        globalCacheClear()
        return {'FINISHED'}
    def getOutputNodes(self,context):
        criteria = {"selected":lambda x: x.select and x.bl_idname in FILE,
                    "all": lambda x: x.bl_idname in FILE,
                    "lmt": lambda x: x.bl_idname == LMTFILE,
                    "timl": lambda x: x.bl_idname == TIMLFILE,
                    "efx": lambda x: x.bl_idname == EFXFILE,                    
            }
        targets = []
        for node in context.space_data.node_tree.nodes:
            if criteria[self.mode](node):
                targets.append(node)
        return targets   
    
classes = [
    TreeExporter
    ]

def exporter_menu_ops(self, context):
    self.layout.operator(TreeExporter.bl_idname, text="MHW FREEHK Tree (.timl/.efx/.lmt)")
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.INFO_MT_file_export.append(exporter_menu_ops)
    
def unregister():
    bpy.types.INFO_MT_file_export.remove(exporter_menu_ops)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    