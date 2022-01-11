# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 02:42:39 2020

@author: AsteriskAmpersand
"""
import bpy
import importlib
import addon_utils

from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty

from .struct import freedomUniteAnim
from .blender.nodetree import freeHKTree,freeHKSockets,freeHKNodes,freeHKNodeTools
from .blender.nodetree import freeHKActionNodes,freeHKDataNodes,freeHKFileNodes
from .blender import timl_controller
from .blender import lmt_tools
from .blender import lmt_operators
from .blender import binary_tools
from .blender import binary_inputs
from .operators import timl_io,timl_ops,lmt_io,export_ops
from .operators import lmt_rig_ops
#from .operators import freedomUnite_io

from .error_handling.errorLists import errorItems,errorTextLevel,errorDisplayLevel

try:
    from .app_license.license import licenseProperty,licenseUI
    licensed = True
except:
    licenseProperty = ''
    licensed = False
    def licenseUI(self,layout):
        pass

content=bytes("","UTF-8")
bl_info = {
    "name": "Free Hyper-Kinetics",
    "description": "Monster Hunter Animations and Timelines Import Export Tools",
    "category": "Import-Export",
    "author": "AsteriskAmpersand",
    "version": (1,1,0),
    #1,0,0 - Alpha, Feature Complete to Original Spec
    #1,1,0 - Alpha, Feature Complete to Transfer Requirements    
    "blender": (2,79,0),
    "location":"Dopesheet > ActionEditor, NodeEditor > FreeHKNodeTree, File > Import",
    "wiki_url":"https://github.com/Ezekial711/MonsterHunterWorldModding/wiki/Free-Hyperkinetics-and-Independent-TIML-Works-Overview",
    "tracker_url":"https://github.com/AsteriskAmpersand/MHW-Free-HyperKinetics/issues"    ,
}                     

class FreeHKAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__
    implicit_tether = BoolProperty(
        name="Implicit Tethering",
        description="Performs bone function to animation linking implicitly",
        default=True,
    )
    dumb_efx_timl = BoolProperty(
        name="Retrograde EFX Mode",
        description="Dumbs down the EFX importing mode to only use explicit timl declarations",
        default=False,
    )
    graph_error = EnumProperty(name = "Graph Error Handling",items = errorItems,default = "Fix")
    action_error = EnumProperty(name = "Action Error Handling",items = errorItems,default = "Fix")
    fcurve_error = EnumProperty(name = "FCurve Error Handling",items = errorItems,default = "Fix")
    error_text_level = EnumProperty(name = "Error Descriptiveness Level",items = errorTextLevel,default = "Verbose")
    error_log_level = EnumProperty(name = "Filter Errors Output",items = errorDisplayLevel,default = "All")
    export_hidden = BoolProperty(name = "Export Muted F-Curves", default = True, description = "Include Muted F-Curves on Export")
    output_log = BoolProperty(name = "Log Export Info",default = True,description = "Write Export Process Information to a Log File")
    output_log_folder = StringProperty(name = "Export Output Log Directory",subtype = 'DIR_PATH')
    enable_wrong = BoolProperty(name = "Enable Failed Features", default = False, description = "Enables Improperly Implemented Features for Debug Reasons")
    if licensed:exec(licenseProperty)        
    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self,"implicit_tether")
        row.prop(self,"dumb_efx_timl")
        row = layout.row(align = True)
        row.prop(self,"output_log")
        if self.output_log:
            row.prop(self,"output_log_folder")
        if licensed:
            licenseUI(self,layout)
        col = layout.column(align=True)
        col.prop(self,"graph_error")
        col.prop(self,"action_error")
        col.prop(self,"fcurve_error")
        col = layout.column(align=True)
        col.prop(self,"error_text_level")
        col.prop(self,"error_log_level")
        col = layout.column(align=True)
        col.prop(self,"export_hidden")
        col.prop(self,"enable_wrong")

modules = [timl_controller,lmt_tools,
           freeHKTree,freeHKSockets,freeHKNodes,freeHKNodeTools,
           freeHKActionNodes,freeHKDataNodes,freeHKFileNodes,
           timl_io,timl_ops,lmt_io,lmt_operators,export_ops,
           lmt_rig_ops,binary_tools,binary_inputs,freedomUniteAnim,
           #freedomUnite_io
           ]
classes = []
importFunctions = []
exportFunctions = []


def register():
    bpy.utils.register_class(FreeHKAddonPreferences)    
    for cl in classes:
        bpy.utils.register_class(cl)
    for iF in exportFunctions:
        bpy.types.INFO_MT_file_export.append(iF)
    for r in modules:
        r.register()
    
def unregister():
    bpy.utils.unregister_class(FreeHKAddonPreferences)    
    for cl in classes:
        bpy.utils.unregister_class(cl)
    for iF in exportFunctions:
        bpy.types.INFO_MT_file_export.remove(iF)   
    for u in modules:
        u.unregister()
    
if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()
