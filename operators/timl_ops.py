# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 09:02:02 2021

@author: AsteriskAmpersand
"""
import bpy
from ..blender.blenderOps import getActiveAction
from ..blender.timl_controller import geometryitems

class remapTIMLProperties(bpy.types.Operator):
    bl_idname = 'freehk.timl_remap'
    bl_label = "Reamp TIML Properties"
    bl_description = 'Perform a TIML Datatype reassigment to the geometry transforms.'
    bl_options = {"REGISTER", "UNDO"}
    
    #action = bpy.props.PointerProperty(type=bpy.types.Action)
    for name,prop in zip(["trans","rot","scl"],["Translation","Rotation","Scale"]):
        for axis in ["x","y","z"]:
            fmt = lambda name,axis,prop,src,opt: '%s = bpy.props.EnumProperty(name = "%s Map"%s,items = geometryitems)'%(src+name+axis,prop+" "+axis.upper(),opt)
            exec(fmt(name,axis,prop,"from_",", options={'HIDDEN'}"))
            exec(fmt(name,axis,prop,"to_",""))

    def execute(self,context):
        action = getActiveAction(context)
        if not action:
            return {'FINISHED'}
        lmapper = {}
        rmapper = {}
        for name,prop in zip(["trans","rot","scl"],["location","rotation_euler","scale"]):
            for ix,axis in enumerate(["x","y","z"]):
                lmapper[(prop,ix)] = ("FreeHKTiml."+getattr(self,"from_"+name+axis),0)
                rmapper[("FreeHKTiml."+getattr(self,"to_"+name+axis),0)] = (prop,ix)
                setattr(action.freehk,name+axis,getattr(self,"to_"+name+axis))
        for fcurve in action.fcurves:
            dp = fcurve.data_path
            ix = fcurve.array_index
            if (dp,ix) in lmapper:
                dp,ix = lmapper[(dp,ix)]
            if (dp,ix) in rmapper:
                dp,ix = rmapper[(dp,ix)]
            fcurve.data_path = dp
            fcurve.array_index = ix
        return {"FINISHED"}

classes = [
    remapTIMLProperties,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
