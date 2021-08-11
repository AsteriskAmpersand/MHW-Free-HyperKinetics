# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 11:52:09 2021

@author: AsteriskAmpersand
"""

import bpy
from bpy.types import Node
from bpy.props import BoolProperty,EnumProperty
from .freeHKNodes import FreeHKNode
from ...struct import TIML,EFX,Lmt,ExtensibleList
from ...error_handling.errorLists import errorItems,errorTextLevel,errorDisplayLevel
from ...error_handling.errorController import ErrorHandler

def getEntryIndex(node):
    return node.entryNum

outputProps = '''customizeExport = BoolProperty(name = "Customize Export",default = False)

graph_error = EnumProperty(name = "Graph Error Handling",items = errorItems,default = "Fix")
action_error = EnumProperty(name = "Action Error Handling",items = errorItems,default = "Fix")
fcurve_error = EnumProperty(name = "FCurve Error Handling",items = errorItems,default = "Fix")
error_text_level = EnumProperty(name = "Error Descriptiveness Level",items = errorTextLevel,default = "Verbose")
error_log_level = EnumProperty(name = "Filter Errors Output",items = errorDisplayLevel,default = "All")
'''

class FreeHKOutputNode(FreeHKNode):
    entryCountError = "G_LOW_ENTRY_COUNT"
    exec(outputProps)
    addon_key = __package__.split('.')[0]
    def init(self, context):
        inx = self.inputs.new(self.inputType,self.inputName,self.inputStr)
        inx.link_limit = 0
    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "outputPath")
        layout.prop(self, "entryCount")
        layout.prop(self, "customizeExport")
        if self.customizeExport:
            col = layout.column(align=True)        
            col.prop(self,"graph_error")
            col.prop(self,"action_error")
            col.prop(self,"fcurve_error")
            col = layout.column(align=True)
            col.prop(self,"error_text_level")
            col.prop(self,"error_log_level")    
    def fixEntryCount(self,entryCount,entryIndices,spares,errors):
            entryCount = max(len(spares) + len(entryIndices),max(entryIndices)+1)
            errors.logSolution("Increased Entry Count to %d"%entryCount)
    def omitEntries(self,entryCount,entryIndices,spares,errors):
        keys = list(entryIndices.keys())
        for k in keys:
            if k > entryCount:
                del entryIndices[k]
        while(spares and (len(spares)+len(entryIndices) > entryCount)):
            spares.pop()
        errors.logSolution("Excess Nodes were filtered out")
        return entryCount
    def checkEntryCount(self,entryCount,entryIndices,spares,errors):
        maxid = max(max(entryIndices),len(spares)+len(entryIndices))
        if entryCount < max(entryIndices):
            errors.append((self.entryCountError,
                           self.name,
                           maxid,
                           entryCount))
            return True
        elif entryCount < len(spares) + len(entryIndices):
            errors.append(("G_LOW_ENTRY_COUNT",
                           self.name,maxid,
                           entryCount))   
            return True
        return False
    def handleEntryCount(self,entryIndices,spares,errors):
        entryCount = self.entryCount
        err = self.checkEntryCount(entryCount,entryIndices,spares,errors)
        if err:
            if errors.graphError.fix:
                entryCount = self.fixEntryCount(entryCount,entryIndices,spares,errors)
            if errors.graphError.omit:
                entryCount = self.omitEntries(entryCount,entryIndices,spares,errors)
        return entryCount
    def getEntries(self,errors):
        entryIndices = {}
        spares = []
        entryNodes,errs = self.validSocketInputs(self.inputs[self.inputName],errors)
        for entryNode in entryNodes:
            ix = getEntryIndex(entryNode)
            if ix == -1:
                spares.append(entryNode)
            elif ix in entryIndices:
                errors.append(("G_REPEATED_ID",entryNode.name,ix))
                if errors.graphError.fix:
                    spares.append(entryNode)
                    errors.logSolution("Node %s was given a new entry id"%entryNode.name)
                elif errors.graphError.omit:
                    errors.logSolution("Node %s was omitted from the export process"%entryNode.name)
            else:
                entryIndices[ix] = entryNode
        if hasattr(self,"entryCount"):
            if self.entryCount == -1:
                entryCount = max(len(spares) + len(entryIndices),max(entryIndices)+1)
            else:
                entryCount = self.handleEntryCount(entryIndices,spares,errors)                           
        else:
            entryCount = max(len(spares) + len(entryIndices),max(entryIndices)+1)      
        return entryCount,entryIndices,spares
    def export(self,error_handler = None):
        if self.customizeExport:
            options = self
        else:
            addon = bpy.context.user_preferences.addons[self.addon_key]
            options = addon.preferences
        if error_handler is None:
            error_handler = ErrorHandler(self,options)
        self.error_handler = error_handler
        error_handler.takeOwnership(self)
        entryCount,entryIndices,spares = self.getEntries(error_handler)
        #TODO - Check for any and all Graph Errors
        #Stop if graph errors found
        self.structure = self.basicStructure()
        substructure = []
        for i in range(entryCount):
            if i in entryIndices:
                entryIndices[i].id = i
                substructure.append(entryIndices[i].export(error_handler))
            elif spares:
                entry = spares.pop()
                entry.id = i
                substructure.append(entry.export())
            else:
                substructure.append(None)
        self.structure.extend(substructure)        
        return self.structure
        

class LMTFileNode(Node, FreeHKOutputNode):
    '''LMT Output Node'''
    entryCountError = "G_INJECTION_ENTRY_COUNT"
    bl_idname = 'LMTFileNode'
    bl_label = "LMT Output Node"
    bl_icon = 'GREASEPENCIL'

    outputPath = bpy.props.StringProperty(
        name = "Path",
        description = "Path to the file to export",
        default = "",
        subtype = 'FILE_PATH'
        )
    entryCount = bpy.props.IntProperty(name="Entry Count", default = -1)
    inject = bpy.props.BoolProperty(name="Inject",description="Inject into a file instead of exporting",default = False)
    exec(outputProps)
    
    inputType = "FreeHKAnimationEntrySocket"
    inputName = "LMT Entry"
    inputStr = "LMT_Entry"

    def basicStructure(self):
        return Lmt.LMT()

    def draw_buttons(self, context, layout):
        super().draw_buttons(context,layout)
        layout.prop(self, "inject")

class TIMLFileNode(Node, FreeHKOutputNode):
    '''TIML Output Node'''
    bl_idname = 'TIMLFileNode'
    bl_label = "TIML Output Node"
    bl_icon = 'GREASEPENCIL'

    outputPath = bpy.props.StringProperty(
        name = "Path",
        description = "Path to the file to export",
        default = "",
        subtype = 'FILE_PATH'
        )
    entryCount = bpy.props.IntProperty(name="Entry Count", default = -1)
    inject = False
    exec(outputProps)

    def basicStructure(self):
        return TIML.TIML()    

    inputType = "FreeHKTimlEntrySocket"
    inputName = "TIML Entry"
    inputStr = "TIML_Entry"

#TODO - Basic structure is list of TIMLs
class EFXFileNode(Node, FreeHKOutputNode):
    '''EFX Output Node'''
    entryCountError = "G_INJECTION_ENTRY_COUNT"
    bl_idname = 'EFXFileNode'
    bl_label = "EFX Output Node"
    bl_icon = 'GREASEPENCIL'
    exec(outputProps)
    
    outputPath = bpy.props.StringProperty(
        name = "Path",
        description = "Path to the file to export",
        default = "",
        subtype = 'FILE_PATH'
        )    
    inject = bpy.props.BoolProperty(name="Inject",description="Inject into a file instead of exporting",default = False)
    inputType = "FreeHKEFXEntrySocket"
    inputName = "EFX Entry"
    inputStr = "EFX_Entry"
    addon_key = __package__.split('.')[0]
    def draw_buttons(self, context, layout):
        layout.prop(self, "outputPath")
        layout.prop(self, "inject")        
    def calculateEntryCount(self):
        with open(self.filepath,"rb") as inf:
            file = inf.read()
            timlOffsets = TIML.getTimlOffsets(file)
        return len(timlOffsets)
    def basicStructure(self):
        addon = bpy.context.user_preferences.addons[self.addon_key]
        retrograde = addon.preferences.preferences.dumb_efx_timl        
        with open(self.outputPath,"rb") as inf:
            if retrograde:
                return TIML.Legacy_TIML_EFX().marshall(inf)                
            else:
                return TIML.TIML_EFX().marshall(inf)
    
class JSONFileNode(Node,FreeHKOutputNode):
    '''JSON Output Node'''
    bl_idname = 'JSONFileNode'
    bl_label = "JSON Output Node"
    bl_icon = 'GREASEPENCIL'
    outputPath = bpy.props.StringProperty(
        name = "Path",
        description = "Path to the file to export",
        default = "",
        subtype = 'FILE_PATH'
        )
    def init(self, context):
        self.inputs.new("FreeHKGenericSocket","Action, Data or Entry")#
    def draw_buttons(self, context, layout):
        layout.prop(self, "outputPath")
    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "outputPath")
    def update(self):
        linkName = list(self.inputs.keys())[0]
        if self.inputs[linkName].links:            
            self.inputs[linkName].name = self.inputs[linkName].links[0].from_socket.name

classes = [
    LMTFileNode, EFXFileNode, TIMLFileNode,JSONFileNode
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)