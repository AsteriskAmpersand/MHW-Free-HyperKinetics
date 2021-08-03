# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 14:27:30 2021

@author: AsteriskAmpersand
"""

import bpy
from bpy.props import EnumProperty
from ...ui.HKIcons import pcoll
from .freeHKNodeOps import (LMTACTION,                            
                            LMTENTRY,EFXENTRY,TIMLENTRY)
from ..lmt_operators import (TransferTether,TransferTetherSilent,ClearTether,UpdateBoneFunctions,
                            UpdateAnimationNames,CompleteChannels,SynchronizeKeyframes,
                            ResampleFCurve,ResampleSelectedFCurve,GlobalEnableFCurves,
                            CheckActionForExport)
from ..lmt_tools import lmtTools, lmtDescriptions, lmtIcons

def hasInputs(node):
    return hasattr(node,"inputs") and len(node.inputs)!=0

def fetchTerminalParents(node,fltr = None,visited = None):
    if visited is None:
        visited = set()
    visited.add(node)
    if fltr is None: fltr = lambda x: True    
    if not hasInputs(node):
        return [node]
    terminal = []
    for socket in node.inputs.values():
        for inp in socket.links:
            p = inp.from_node
            if fltr(p) and p not in visited:
                terminal += fetchTerminalParents(p,fltr,visited)            
    return terminal
            
    
class GoToEntry(bpy.types.Operator):
    bl_idname = "freehk.goto"
    bl_label = "Go to Entry Node"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Center view on node with entry index."
    #index = IntProperty(name="Index",description="Index",default=0)
    typing = EnumProperty(name="Type",description="Node Type",
                          items = [(TIMLENTRY,"TIML Entry",""),
                                   (LMTENTRY,"LMT Entry",""),
                                   (EFXENTRY,"EFX Entry",""),                              
                              ],
                          default = LMTENTRY)
    def execute(self,context):
        candidates = []
        for node in context.space_data.node_tree.nodes:
            if node.bl_idname == self.typing and node.entryNum == bpy.context.scene.freehk_node_goto:
                candidates.append(node)
            node.select = False
        if candidates:
            center = candidates[0]
            center.select = True
            ctx = context.copy()
            bpy.ops.node.view_selected(ctx)
        return {"FINISHED"}

class LMTNodeModifier():
    def actionFetch(self,context,action_type):
        visited = set()
        actionNodes = []
        for node in context.space_data.node_tree.nodes:
            if "LMT" in node.bl_idname:
                actionNodes += fetchTerminalParents(node,lambda x: "LMT" in x.bl_idname,visited)
        directActions = set((node.input_action for node in actionNodes if node.bl_idname == LMTACTION and node.input_action is not None))
        return directActions
    
    @classmethod
    def poll(cls,context):
        return context.space_data and hasattr(context.space_data,"node_tree") and context.space_data.node_tree

    def execute(self,context):
        self.limit = False
        return super().execute(context)
        
def defineDependentClass(parent):
    class DependentClass(LMTNodeModifier,parent):
        bl_idname = parent.bl_idname + "_node"
        bl_label = parent.bl_label
        bl_options = parent.bl_options
        bl_description = parent.bl_description.replace("Action","Selected Nodes Action")
    return DependentClass

ClearTetherNode = defineDependentClass(ClearTether)
TransferTetherSilentNode = defineDependentClass(TransferTetherSilent)
TransferTetherNode = defineDependentClass(TransferTether)
UpdateBoneFunctionsNode = defineDependentClass(UpdateBoneFunctions)
UpdateAnimationNamesNode = defineDependentClass(UpdateAnimationNames)
CompleteChannelsNode = defineDependentClass(CompleteChannels)
SynchronizeKeyframesNode = defineDependentClass(SynchronizeKeyframes)
ResampleFCurveNode = defineDependentClass(ResampleFCurve)
ResampleSelectedFCurveNode = defineDependentClass(ResampleSelectedFCurve)
GlobalEnableFCurvesNode = defineDependentClass(GlobalEnableFCurves)
CheckActionForExportNode = defineDependentClass(CheckActionForExport)


#layout.operator("freehk.resample_fcurve",icon_value=pcoll["FREEHK"].icon_id, text="Add FreeHK Props")
#layout.operator("freehk.create_fcurve_action",icon_value=pcoll["FREEHK"].icon_id, text="Add FreeHK Props")

class ActionToolsNodes(bpy.types.Panel):
    bl_idname = "freehk.tree_tools_lmt_ops"
    bl_space_type = 'NODE_EDITOR'
    bl_category = "MHW Free HK"
    bl_region_type = 'UI'
    bl_label = "Free HK Action Tools"
    bl_description = "FreeHK Action Tools"
    
    def draw(self, context):
        layout = self.layout
        actionName = "All "
        iconName = "_TOTAL"
        c = layout.column(align=True)
        for tool,desc,icon in zip(lmtTools,lmtDescriptions,lmtIcons):
            if tool == "transform_tether" or "resample_action":
                l = c.row(align = True)
            else:
                l = c
            l.operator("freehk.%s_node"%tool,icon_value=pcoll[icon+iconName].icon_id, text=desc%actionName)
            if "transform_tether" in tool:
                l.prop(context.scene,"freehk_tether",text = "")#,text = "Transfer Target")
            if tool == "resample_action":
                l.prop(bpy.context.scene,"freehk_node_resample","")

class ExportSettings(bpy.types.Panel):
    bl_idname = "freehk.tree_tools_export"
    bl_space_type = 'NODE_EDITOR'
    bl_category = "MHW Free HK"
    bl_region_type = 'UI'
    bl_label = "Free HK Export Settings"
    bl_description = "FreeHK Export Settings"

    addon_key = __package__.split('.')[0]   

    @classmethod
    def poll(cls, context):
        return context.space_data and context.space_data.node_tree and \
            context.space_data.node_tree.bl_idname == 'FreeHKNodeTree'# and context.scene.node_tree    

    def draw(self, context):
        addon = context.user_preferences.addons[self.addon_key]
        #self.addon_props = addon.preferences
        layout = self.layout
        col = layout.column(align=True)
        
        col.prop(addon.preferences,"graph_error")
        col.prop(addon.preferences,"action_error")
        col.prop(addon.preferences,"fcurve_error")
        col = layout.column(align=True)
        col.prop(addon.preferences,"error_text_level")
        col.prop(addon.preferences,"error_log_level")

#layout.operator("freehk.export",icon_value=pcoll["FREEHK"].icon_id,text="Export")
class TreeTools(bpy.types.Panel):
    bl_idname = "freehk.tree_tools"
    bl_space_type = 'NODE_EDITOR'
    bl_category = "MHW Free HK"
    bl_region_type = 'UI'
    bl_label = "Free HK Tree Tools"
    bl_description = "FreeHK Tree Tools"
    
    @classmethod
    def poll(cls, context):
        return context.space_data and context.space_data.node_tree and \
            context.space_data.node_tree.bl_idname == 'FreeHKNodeTree'# and context.scene.node_tree
    
    def draw(self,context):
        self.layout.label("Export Tools")
        col = self.layout.column(align=True)
        col.operator("freehk.export",icon_value=pcoll["FREEHK_FILE"].icon_id,text="Export All")
        col.operator("freehk.export",icon_value=pcoll["FREEHK_SELECTED_FILE"].icon_id,text="Export Selected").mode="selected"
        col.operator("freehk.export",icon_value=pcoll["FREEHK_LMT_FILE"].icon_id,text="Export LMT").mode="lmt"
        col.operator("freehk.export",icon_value=pcoll["FREEHK_TIML_FILE"].icon_id,text="Export TIML").mode="timl"
        col.operator("freehk.export",icon_value=pcoll["FREEHK_EFX_FILE"].icon_id,text="Export EFX").mode="efx"
        col.separator()
        row = col.row(align=True)
        row.operator("freehk.goto",icon_value = pcoll["FREEHK"].icon_id,text="Go to Entry")
        row.prop(context.scene,"freehk_node_goto","")
        
def node_pulldown(self, context):
    if context.space_data.tree_type == 'FreeHKNodeTree':
        row = self.layout.row(align=True)
        row.operator("freehk.export",icon_value=pcoll["FREEHK_FILE"].icon_id,text="")
        row.operator("freehk.export",icon_value=pcoll["FREEHK_SELECTED_FILE"].icon_id,text="").mode="selected"
        row.operator("freehk.export",icon_value=pcoll["FREEHK_LMT_FILE"].icon_id,text="").mode="lmt"
        row.operator("freehk.export",icon_value=pcoll["FREEHK_TIML_FILE"].icon_id,text="").mode="timl"
        row.operator("freehk.export",icon_value=pcoll["FREEHK_EFX_FILE"].icon_id,text="").mode="efx"

classes = [
    TreeTools,ExportSettings,ActionToolsNodes,GoToEntry,
    
    TransferTetherNode,
    TransferTetherSilentNode,
    ClearTetherNode,
    UpdateBoneFunctionsNode,
    UpdateAnimationNamesNode,
    CompleteChannelsNode,
    SynchronizeKeyframesNode,
    ResampleFCurveNode,
    ResampleSelectedFCurveNode,
    GlobalEnableFCurvesNode,
    CheckActionForExportNode
]

def importer_menu_ops(self, context):
    pass

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
#    bpy.types.INFO_MT_file_import.append(importer_menu_ops)
    bpy.types.Scene.freehk_node_goto =  bpy.props.IntProperty(name = "Go To Index",default = 0)
    bpy.types.Scene.freehk_node_resample =  bpy.props.IntProperty(name = "Global Resample Rate",default = 1,min=1)
    bpy.types.NODE_HT_header.append(node_pulldown)
    
def unregister():
#    bpy.types.INFO_MT_file_import.remove(importer_menu_ops)
    bpy.types.NODE_HT_header.remove(node_pulldown)    
    del bpy.types.Scene.freehk_node_resample
    del bpy.types.Scene.freehk_node_goto
    for cls in classes:
        bpy.utils.unregister_class(cls)
    