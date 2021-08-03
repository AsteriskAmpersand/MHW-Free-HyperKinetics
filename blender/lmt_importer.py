# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 06:54:50 2021

@author: AsteriskAmpersand
"""
import bpy
from pathlib import Path
from mathutils import Vector
from .timl_importer import TIMLStructure,processTIMLData
from .blenderOps import customizeFCurve

def defineFCurve(action,fcurveSet,kfCount,data_path,index):
    #if not kfCount:
    #    return None
    bind = "Root" if fcurveSet.boneId == -1 else "BoneFunction.%03d"%fcurveSet.boneId 
    path =  'pose.bones["%s"]'%bind+"."+data_path
    f = action.fcurves.new(data_path=path,index=index)
    f.keyframe_points.add(kfCount)
    return f

def createChannels(action,fcurveSet):
    channels = []
    keys = fcurveSet.channelNames()
    for bdata_path,data_path,index,var in keys:        
        extra_index = iter(range(-1,-4,-1))
        keyframeCount = 1 + (hasattr(fcurveSet,"tail")) + len(fcurveSet.keyframes)
        if fcurveSet.fold:
            f = defineFCurve(action,fcurveSet,keyframeCount,bdata_path,index+4)#bdata_path+
            f.mute = True            
        else:
            f = defineFCurve(action,fcurveSet,keyframeCount,bdata_path,index)#1+
        f.keyframe_points[next(extra_index)].co = (0,getattr(Vector(fcurveSet.basis),var))#-1            
        if hasattr(fcurveSet,"tail"):
            animeEnd = action.freehk.frameCount
            f.keyframe_points[next(extra_index)].co = (animeEnd+1,getattr(Vector(fcurveSet.tail),var))
        channels.append(f)
    return channels

def loadKeyframes(bones,action):
    warning = False
    for fcurve_set in bones:
        if not warning and fcurve_set.fold:
            print("WARNING - Action %s has folded animation frames"%action.name) 
            warning = True
        channels = createChannels(action,fcurve_set)        
        list(map(lambda x: customizeFCurve(x,fcurve_set.bufferType,fcurve_set.boneId),channels))        
        for fcurve,keyframeList in zip(channels,fcurve_set.channels()):
            timing = 1#0            
            for ix,(keyframeVal,keyframeTiming) in enumerate(keyframeList):
                kf = fcurve.keyframe_points[ix]
                kf.co = (timing,keyframeVal)
                timing+=keyframeTiming     
            bpy.context.scene.frame_end = max(bpy.context.scene.frame_end,timing)
            fcurve.update()

def loadAction(action_name,lmt_action):
    name = action_name
    action = bpy.data.actions.new(name)
    action.freehk.starType = "LMT_Action"
    action.freehk.loopFrame = lmt_action.loopFrame
    action.freehk.frameCount = lmt_action.frameCount
    action.freehk.fold = "MAIN"
    return action

def KBRAction(path,lmt_action):
    action_name = "LMT::"+path+"::"+"%03d"%lmt_action.id
    bones = lmt_action.bones    
    action = loadAction(action_name,lmt_action)
    loadKeyframes(bones,action)
    return action

def LMTFileLoad(path,rawLMT,remapOperation,tree):
    outputNode = tree.createLMTOutputNode(str(path))
    outputNode.entryCount = rawLMT.Header.entryCount#len(rawLMT.Offsets)
    timlNodes = {}
    kbrNodes = {}
    for i,lmt_action in enumerate(rawLMT.ActionHeaders):
        kbrO = lmt_action.fcurveOffset
        timlO = lmt_action.timlOffset
        lmtEntry = tree.createLMTEntryNode(lmt_action,outputs = [outputNode])
        if kbrO:
            if kbrO in kbrNodes:
                kbrActionNode = kbrNodes[kbrO]
                tree.connect(kbrActionNode,lmtEntry,"LMT Animation")
            else:
                kbrAction = KBRAction(Path(path).stem,lmt_action)
                kbrActionNode = tree.createLMTActionNode(kbrAction,outputs=[lmtEntry])
                kbrNodes[kbrO] = kbrActionNode
        if timlO:
            if timlO in timlNodes:
                timlDataNode = timlNodes[timlO]
                tree.connect(timlDataNode,lmtEntry,"TIML Data")
            else:
                timlDataNode = TIMLStructure([processTIMLData(lmt_action.timl,remapOperation)],
                                             tree,[lmtEntry])
                timlNodes[timlO] = timlDataNode
    return outputNode