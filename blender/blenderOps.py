# -*- coding: utf-8 -*-
"""
Created on Sun Jun 27 04:15:30 2021

@author: AsteriskAmpersand
"""
import bpy
import math

def createTIMLAction(typing):
    action = bpy.data.actions.new("TIML::%s"%typing.timelineParameterString)
    action.freehk.starType = "TIML_Action"
    action.freehk.timelineParam = "m%08X"%typing.timelineParameterHash
    action.freehk.unkn0 = typing.unkn0
    for prop in ["transx","transy","transz","rotx","roty","rotz","sclx","scly","sclz"]:
        if prop in typing.remapSettings:
            setattr(action.freehk,prop,typing.remapSettings[prop])
    return action

def createTIMLFcurve(action,transform):
    path,index = transform.datatype
    fcurve = action.fcurves.new(data_path=path,index = index)
    fcurve.keyframe_points.add(transform.count)
    return fcurve

def createTIMLKeyframes(fcurve,keyframe):
    kf = fcurve.keyframe_points[keyframe.index]
    factor = lambda x: x if "rotation_euler" not in fcurve.data_path else math.radians(x)
    kf.co = (keyframe.frameTiming,factor(keyframe.value))
    kf.interpolation = keyframe.interpolation
    kf.back = keyframe.controlL
    kf.period = keyframe.controlR
    bpy.context.scene.frame_end = max(keyframe.frameTiming,bpy.context.scene.frame_end)
    return kf

def customizeFCurve(fc,starType=0,boneFunction=-2):
    l = fc.modifiers.new("LIMITS")
    l.use_restricted_range = True
    l.mute = True
    l.frame_start = l.frame_end = 0
    l.min_x = starType
    l.min_y = boneFunction
    return l

def animationLength(action):
    return max(keyframe.co[0]-1*(fetchBoneFunction(fcurve)==-1) for fcurve in action.fcurves for keyframe in fcurve.keyframe_points)
        
def completeBasis(action):
    frameCount = action.freehk.frameCount
    if frameCount == -1:
        frameCount = animationLength(action)
    for fcurve in action.fcurves:
        if fetchBoneFunction(fcurve) == -1:
            timings = {kf.co[0] for kf in fcurve.keyframe_points}
            if frameCount + 1 not in timings:
                fcurve.keyframe_points.insert(frameCount+1,fcurve.evaluate(frameCount+1))
                
def previewStrip(self,obj,actions):
    if not obj:
        return
    if obj.animation_data is None:
        obj.animation_data_create()
    track = obj.animation_data.nla_tracks.new()
    length = 0
    #scene_length = bpy.context.scene.frame_end
    for action in actions:
        if action.freehk.starType == "LMT_Action":
            if action.freehk.frameCount == -1:
                #probably should justcalculate from fcurves
                delta = animationLength(action) + 1
            else:
                delta = action.freehk.frameCount + 1
            if bpy.context.scene.frame_end < length + delta:
                bpy.context.scene.frame_end = length+delta+1
            s = track.strips.new(name = action.name, start = length, action = action)
            length += delta
    #bpy.context.scene.frame_end = scene_length

def foldFCurve(action,fcurve):
    fc = action.fcurves.new(data_path = fcurve.data_path, index=(fcurve.array_index+4)%8)
    fc.keyframe_points.add(1)
    fc.keyframe_points[0].co = (0,0)
    starType,boneFunction = fetchEncodingType(fcurve),fetchBoneFunction(fcurve)
    if starType is not None and boneFunction is not None:
        customizeFCurve(fc,starType,boneFunction)
    else:
        customizeFCurve(fc)
    fc.mute = not action.freehk.fold == "FOLDED"
    if action.freehk.fold:
        fcurve.mute = True
    fc.update()
    return fc

def addKeyframe(action, fcurve):
    f = max((k.co for k in fcurve.keyframe_points),default = (0,0))
    fcurve.keyframe_points.add(1)
    fcurve.keyframe_points[-1].co = (f[0]+1,f[1])
    
def stripBuffers(action):
    for fc in action.fcurves:
        mod = fetchFreeHKCustom(fc)
        if mod:
            mod.min_x = 0

def breakPath(actionPath):
    sectional = actionPath.split(".")
    if len(sectional) < 2:
        return actionPath,""
    else:
        return ".".join(sectional[:-1]),sectional[-1]

def transformSize(transformType):
    if transformType == "rotation_quaternion":
        return 4
    elif transformType in ["location","scale","rotation_euler"]:
        return 3
    else:
        return None

def fetchFreeHKCustom(fcurve):
    if fcurve.modifiers:
        for mod in fcurve.modifiers:
            if mod.type == "LIMITS" and mod.mute and\
                mod.use_restricted_range and\
                mod.frame_start == mod.frame_end and mod.frame_end == 0:    
                return mod
    return None

def fetchBoneFunction(fcurve):
    mod = fetchFreeHKCustom(fcurve)
    if mod: return int(round(mod.min_y))
    return None

def fetchEncodingType(fcurve):
    mod = fetchFreeHKCustom(fcurve)
    if mod: return int(round(mod.min_x))
    return None

def setBoneFunction(fcurve,boneFunction):
    mod = fetchFreeHKCustom(fcurve)                     
    if mod:
        mod.min_y = boneFunction
        return
    customizeFCurve(fcurve,0,boneFunction)

def setEncodingType(fcurve,encoding):
    mod = fetchFreeHKCustom(fcurve)                     
    if mod:
        mod.min_x = encoding
        return
    customizeFCurve(fcurve,encoding,-2)

def frameless(fcurve,boneFunction):
    if len(fcurve.keyframe_points) == 0:
        return True
    if boneFunction == -1:
        if len(fcurve.keyframe_points) > 2:
            return False
        if len(fcurve.keyframe_points) == 2:
            return 0 in {p.co[0] for p in fcurve.keyframe_points}
    else:
        if len(fcurve.keyframe_points) == 1:
            return 0 in {p.co[0] for p in fcurve.keyframe_points}
        else:
            return False
        
def setMaxEncoding(fcurve):
    path,transform = breakPath(fcurve.data_path)
    encodingMap = {"rotation_quaternion":6,
                   "scale":3,
                   "location":3,
                   "rotation_euler":6     
                }
    keylessEncodingMap = {"rotation_quaternion":2,
                   "scale":1,
                   "location":1,
                   "rotation_euler":2     
                }
    if transform in encodingMap:
        boneFunction = fetchBoneFunction(fcurve)
        if frameless(fcurve,boneFunction):
            setEncodingType(fcurve,keylessEncodingMap[transform])
        setEncodingType(fcurve,encodingMap[transform])
    return

def replaceBoneName(oldname,newname):
    transform = oldname.split(".")[-1]
    return 'pose.bones["%s"].%s'%(newname,transform)    

def getActiveAction(context):
    action = None
    try:
        area = context.area
        dopesheet = area.spaces[0]
        action = dopesheet.action
    except Exception as e:
        for area in bpy.context.screen.areas:  #loop through areas
            if area.type == 'DOPESHEET_EDITOR':   #find the dopesheet
                dopesheet = area.spaces[0]
                action = dopesheet.action
                break
    return action

def updateDopesheet(context):
    try:
        area = context.area
        dopesheet = area.spaces[0]
    except:
        for area in bpy.context.screen.areas:  #loop through areas
            if area.type == 'DOPESHEET_EDITOR':   #find the dopesheet
                dopesheet = area.spaces[0]
                break
    try: dopesheet.use_realtime_update = dopesheet.use_realtime_update
    except: pass
    return
    

def getActions(op,context,filterstr = None):
    if op.limit:
        action = getActiveAction(context)
        target_actions = [action] if action else []
    else:
        target_actions = bpy.data.actions
    if filterstr is not None:
        target_actions = list(filter(lambda x: x.freehk.starType == filterstr,target_actions))
    return target_actions

def armaturePoll(self,obj):
    return obj.type == "ARMATURE"