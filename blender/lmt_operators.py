# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 22:00:26 2021

@author: AsteriskAmpersand
"""
import bpy
from .timl_param_utils import timlNameToProp,timlPropToName
from .blenderOps import (customizeFCurve,foldFCurve,addKeyframe,getActions,fetchFreeHKCustom,
                        updateDopesheet,setEncodingType,setMaxEncoding,fetchEncodingType,
                        previewStrip)
from .tetherOps import (transferTether, updateAnimationNames,updateAnimationBoneFunctions,
                        completeMissingChannels,synchronizeKeyframes,resampleAction,resampleFCurve,
                        getBoneFromPath)
from .lmt_exporter import LMTActionParser
from ..error_handling.errorController import DebugVerifier
from .lmt_tools import encodingTypes


class CreateFCurve(bpy.types.Operator):
    bl_idname = "freehk.create_fcurve"
    bl_label = "Customize F-Curve with FreeHK Properties"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Customize F-Curve"
    
    action = bpy.props.IntProperty(name ="Action",options = {'HIDDEN'})
    fcurve = bpy.props.IntProperty(name = "FCurve",options = {'HIDDEN'})
    starType = bpy.props.EnumProperty(name = "Type",
                                      items = encodingTypes,
                                      default = "0",)
    boneFunction = bpy.props.IntProperty(name = "Bone Function",description = "Bone Function ID",default = -2) 
    
    def execute(self,context):
        fc = bpy.data.actions[self.action].fcurves[self.fcurve]
        customizeFCurve(fc,int(self.starType),int(self.boneFunction))
        return {"FINISHED"}

class FCurveOperator(bpy.types.Operator):
    def execute(self,context):
        action = bpy.data.actions[self.action]
        added = []        
        for fc in action.fcurves:
            if fc.select:
                added.append(fc)
        for curve in added:
            type(self).operation(action,curve)
        return {"FINISHED"}    
    
class AddKeyframes(FCurveOperator):
    bl_idname = "freehk.add_keyframes"
    bl_label = "Add Keyframes to F-Curves"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Add Keyframes to Selected FCurves"
    
    action = bpy.props.IntProperty(name ="Action",options = {'HIDDEN'})
    operation = addKeyframe


class FoldFCurve(FCurveOperator):
    bl_idname = "freehk.fold_fcurve"
    bl_label = "Fold Selected F-Curves"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Fold F-Curve generating a clone of channels for it."
    
    action = bpy.props.IntProperty(name ="Action",options = {'HIDDEN'})
    operation = foldFCurve
    

class _TransferTether():
    actionFetch = getActions
    def execute(self,context):
        target_tether = self.fetchTether(context)
        target_actions = self.actionFetch(context,"LMT_Action")
        transferTether(target_actions,target_tether)
        #context.scene.update()
        return {'FINISHED'}

class TransferTetherSilent(_TransferTether,bpy.types.Operator):
    bl_idname = "freehk.transform_tether_silent"
    bl_label = "Transfer Tether without Updates"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Swap Action's LMT Tether to a new Target without modifying the animation"

    limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )
    addon_key = __package__.split('.')[0]
    
    def fetchTether(self,context):
        return context.scene.freehk_tether
    def execute(self,context):
        target_tether = self.fetchTether(context)
        target_actions = self.actionFetch(context,"LMT_Action")
        
        addon = context.user_preferences.addons[self.addon_key]
        implicitTether = addon.preferences.implicit_tether 
        for action in target_actions:
            action.freehk.tetherFrame = target_tether
            if implicitTether:
                updateAnimationNames(target_tether,action)
                updateAnimationBoneFunctions(target_tether,action)
        updateDopesheet(context)
        return {'FINISHED'}
    
class TransferTether(_TransferTether,bpy.types.Operator):
    bl_idname = "freehk.transform_tether"
    bl_label = "Transfer Tether"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Swap Action's LMT Tether to a new Target"

    limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )

    def fetchTether(self,context):
        return context.scene.freehk_tether    

class ClearTether(_TransferTether,bpy.types.Operator):
    bl_idname = "freehk.clear_tether"
    bl_label = "Clear Tether"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Clear Action's LMT Tether"

    limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )

    def fetchTether(self,ct):
        return None 

class MappedActionOperator():
    actionFetch = getActions
    tetherless = False
    actionType = "LMT_Action"
    def execute(self,context):
        errors = []
        target_actions = self.actionFetch(context,self.actionType)
        for action in target_actions:            
            armature = action.freehk.tetherFrame
            if armature or self.tetherless:
                self.mappedOperator(armature,action)
                #try:
                #    self.mappedOperator(armature,action)
                #except Exception as e:
                #    errors.append(e)
            else:
                errors.append("Action %s is missing a tether which is required for the operation"%action.name)
        if errors:
            print("Errors during FreeHK Operation:")
            for err in errors:
                print("\t",err)
        updateDopesheet(context)
        return {'FINISHED'}

class UpdateBoneFunctions(MappedActionOperator,bpy.types.Operator):
    bl_idname = "freehk.update_bone_function"
    bl_label = "Update Bone Functions"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Update bone functions from current tether based on name"

    limit = bpy.props.BoolProperty(name = "Limit", description = "Limit to current action", default = True, options={'HIDDEN'})    
    def mappedOperator(self,armature,action):
        updateAnimationBoneFunctions(armature,action)

class UpdateAnimationNames(MappedActionOperator,bpy.types.Operator):
    bl_idname = "freehk.update_name"
    bl_label = "Update Animation Names"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Update animation names based on bone functions"

    limit = bpy.props.BoolProperty(name = "Limit", description = "Limit to current action", default = True, options={'HIDDEN'})
    def mappedOperator(self,armature,action):
        updateAnimationNames(armature,action)

class CompleteChannels(MappedActionOperator,bpy.types.Operator):
    bl_idname = "freehk.complete_channels"
    bl_label = "Completes Missing Channels"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Adds missing channels to partial animations"
    tetherless = True
    limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )
    def mappedOperator(self,armature,action):
        completeMissingChannels(action)

class SynchronizeKeyframes(MappedActionOperator,bpy.types.Operator):
    bl_idname = "freehk.synchronize_keyframes"
    bl_label = "Synchronizes Keyframe Timings"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Adds missing keyframes for exporting."
    tetherless = True
    limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )
    def mappedOperator(self,armature,action):
        print(action.name)
        synchronizeKeyframes(action)

class ResampleFCurve(MappedActionOperator,bpy.types.Operator):
    bl_idname = "freehk.resample_action"
    bl_label = "Resample Keyframes"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Adds keyframes if distance between keyframe pair larger than sample rate."
    tetherless = True
    limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )
    def mappedOperator(self,armature,action):
        resampleAction(action,action.freehk.resampleRate)    

class ResampleSelectedFCurve(MappedActionOperator,bpy.types.Operator):
    bl_idname = "freehk.resample_fcurve"
    bl_label = "Resample Keyframes"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Adds keyframes if distance between keyframe pair larger than sample rate."
    tetherless = True
    limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )
    def mappedOperator(self,armature,action):        
        for fcurve in action.fcurves:
            if fcurve.select:
                resampleFCurve(fcurve,action.freehk.resampleRate) 

class ResampleSelectedTIMLFCurve(MappedActionOperator,bpy.types.Operator):
    bl_idname = "freehk.resample_timl_fcurve"
    bl_label = "Resample Keyframes"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Adds keyframes if distance between keyframe pair larger than sample rate."
    tetherless = True
    actionType = "TIML_Action"
    #limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )
    def __init__(self,*args,**kwargs):
        self.limit = True
        super().__init__(*args,**kwargs)
    def mappedOperator(self,armature,action):        
        for fcurve in action.fcurves:
            if fcurve.select:
                resampleFCurve(fcurve,action.freehk.resampleRate) 

class GlobalEnableFCurves(MappedActionOperator,bpy.types.Operator):
    bl_idname = "freehk.create_fcurve_action"
    bl_label = "Enable FreeHK FCurves"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Enables all fcurves on action with FreeHK properties."
    tetherless = True
    limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )
    def mappedOperator(self,armature,action):
        for fcurve in action.fcurves:
            if fetchFreeHKCustom(fcurve) is None:
                pbone = getBoneFromPath(armature,fcurve.data_path)
                if pbone and "boneFunction" in pbone:
                    bone = pbone["boneFunction"]
                else:
                    bone = None
                customizeFCurve(fcurve,0,bone if bone is not None else -2)
                #customizeFCurve

class ClearEncoding(MappedActionOperator,bpy.types.Operator):
    bl_idname = "freehk.clear_buffer_quality"
    bl_label = "Clear Encoding Types"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Sets the encoding of all fcurves witthout a buffer on the action to the highest quality setting."
    tetherless = True
    limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )
    def mappedOperator(self,armature,action):
        for fcurve in action.fcurves:
            setEncodingType(fcurve,0)

class MaximizeQuality(MappedActionOperator,bpy.types.Operator):
    bl_idname = "freehk.maximize_buffer_quality"
    bl_label = "Max FCurve Encoding Quality"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Sets the encoding of all fcurves witthout a buffer on the action to the highest quality setting."
    tetherless = True
    limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )
    def mappedOperator(self,armature,action):
        for fcurve in action.fcurves:
            if not fetchEncodingType(fcurve):
                setMaxEncoding(fcurve)

class CheckActionForExport(MappedActionOperator,bpy.types.Operator):
    bl_idname = "freehk.check_export"
    bl_label = "Check Action for FreeHK Export"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Run the action through the Exporter Process to see possible errors"
    tetherless = True
    limit = bpy.props.BoolProperty(name = "Limit", default = True, options={'HIDDEN'} )
    addon_key = __package__.split('.')[0]
    def __init__(self,*args,**kwargs):
        self.displayed = False
        super().__init__(*args,**kwargs)
    def mappedOperator(self,armature,action):
        addon = bpy.context.user_preferences.addons[self.addon_key]
        error_handler = DebugVerifier(addon.preferences)
        LMTActionParser(action,error_handler)
        errors = error_handler.display()
        if errors and not self.displayed:
            self.displayed = True
            error_handler.raiseAlert()
        print()
    def execute(self,context):
        returnCode = super().execute(context)
        if not self.displayed:
            addon = bpy.context.user_preferences.addons[self.addon_key]
            error_handler = DebugVerifier(addon.preferences)
            error_handler.raiseAlert()
        return returnCode
            
class PreviewActionsInStrip(bpy.types.Operator):
    bl_idname = "freehk.preview_actions"
    bl_label = "Preview All Actions in the NLA Editor"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Preview all animations in a succession on the NLA Editor"
    actionType = "LMT_Action"
    limit = False
    actionFetch = getActions
    def execute(self,context):
        target_actions = sorted(self.actionFetch(context,self.actionType),key = lambda x: x.name)
        armature = bpy.context.scene.freehk_tether
        if armature or self.tetherless:
            previewStrip(self,armature,target_actions)
        return {'FINISHED'}
    
        
classes = [
    CreateFCurve,FoldFCurve,AddKeyframes,TransferTether,TransferTetherSilent,ClearTether,UpdateBoneFunctions,UpdateAnimationNames,
    CompleteChannels,SynchronizeKeyframes,ResampleFCurve,ResampleSelectedFCurve,GlobalEnableFCurves,CheckActionForExport,
    ResampleSelectedTIMLFCurve, ClearEncoding, MaximizeQuality, PreviewActionsInStrip
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
