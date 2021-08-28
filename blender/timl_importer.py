# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 07:06:19 2021

@author: AsteriskAmpersand
"""
import bpy
from .blenderOps import createTIMLAction,createTIMLFcurve,createTIMLKeyframes
from .timl_controller import geometryitems,timl_propcode,timl_propmap
from ..common.HashUtils import hashResolver


interpolationMapping = ['CONSTANT','LINEAR','QUAD','CUBIC','QUART','EXPO','SINE']

bigFlags = [
      150806694,#            mFlag
     2575924291,#         mTrigger
     4027018852,#           mFlag6
     2154666731,#           mFlag3
     4150962813,#           mFlag2
     1852046279,#           mFlag1
      503910216,#           mFlag4
     1762541534,#           mFlag5
     2768909048,#    TargetReqNo A
     3787782803,#  ChangeLeftJntNo
     ]

#timl.dataHeaders[].data
#                   .types[].transforms[].keyframes[]

class dummyKeyframe():
    def __init__(self,keyframe):
        for attr in keyframe.__dict__.keys():
            setattr(self,attr,getattr(keyframe,attr))

def TIMLColorImport(transform,action):
    for i in range(4):
        transform.datatype[1] = i
        fcurve = createTIMLFcurve(action,transform)
        for keyframe in transform.keyframes:
            kf = dummyKeyframe(keyframe)
            kf.value = kf.value[i]/255
            createTIMLKeyframes(fcurve,kf)
        fcurve.update()

mask = 0xFFFF 
def TIMLSplitter(val):
    return (mask&val,((mask<<16)&val)>>16)   
def TIMLJoin(l,r):
    return (l + (r<<16)) & 0xFFFFFFFF

def TIMLFlagImport(transform,action):
    splitter = TIMLSplitter    
    transform.datatype[1] = 0
    l_fcurve = createTIMLFcurve(action,transform)
    transform.datatype[1] = 1
    r_fcurve = createTIMLFcurve(action,transform)
    
    for keyframe in transform.keyframes:
        l_kf, r_kf = dummyKeyframe(keyframe),dummyKeyframe(keyframe)
        l_kf.controlL, r_kf.controlL = splitter(keyframe.controlL)
        l_kf.controlR, r_kf.controlR = splitter(keyframe.controlR)
        #print(keyframe.value)
        l,r = splitter(keyframe.value)
        #print(l,r)
        #print((l<<16) + r)
        #print()
        l_kf.value, r_kf.value = splitter(keyframe.value)
        createTIMLKeyframes(l_fcurve,l_kf)
        createTIMLKeyframes(r_fcurve,r_kf)
    l_fcurve.update()
    r_fcurve.update()
        
def TIMLStructure(processedTIML,tree,entry=[]):#controller
    dataNodes = []
    for data in processedTIML:        
        dataNode = tree.createTIMLDataNode(data,outputs=entry)
        for typing in data.types:
            action = createTIMLAction(typing)
            tree.createTIMLActionNode(action,outputs = [dataNode])
            for transform in typing.transforms:
                if transform.dataType == 3:
                    TIMLColorImport(transform,action)
                elif transform.datatypeHash in bigFlags:
                    TIMLFlagImport(transform,action)
                else:
                    fcurve = createTIMLFcurve(action,transform)
                    for keyframe in transform.keyframes:
                        createTIMLKeyframes(fcurve,keyframe)
                    fcurve.update()
        dataNodes.append(dataNode)
    return dataNodes

def TIMLFileLoad(path,rawTIML,remapOperation,tree):
    processedTIML = processTIML(rawTIML,remapOperation)
    outputNode = tree.createTIMLOutputNode(str(path))
    for i,data in enumerate(processedTIML):
        entryNode = tree.createTIMLEntryNode(data.id,outputs=[outputNode])
        TIMLStructure([data],tree,[entryNode])
    return outputNode

def EFXFileLoad(path,timls,remapOperation,tree):
    outputNode = tree.createEFXOutputNode(str(path))
    for i,rawTIML in enumerate(timls):        
        processedTIML = processTIML(rawTIML,remapOperation)        
        entryNode = tree.createEFXEntryNode(i,outputs=[outputNode])
        for i,data in enumerate(processedTIML):            
            TIMLStructure([data],tree,[entryNode])
    return outputNode

def applyRemap(remap,dth):
    dthProp = "m%08X"%dth
    if dthProp in remap:
        return remap[dthProp]
    else:
        return "FreeHKTiml."+dthProp,0

highKw = {"pos:":"location","rot:":"rotation_euler","scl:":"scale"}
highDT = {kw+i:bl for kw,bl in highKw.items() for i in ["x","y","z"]}
midKw = {"Rotation":"rotation_euler","RotationAdd":"rotation_euler",
         "Size":"scale","TerminatePosition":"location","Scale":"scale"}
midDT = {kw+i:bl for kw,bl in midKw.items() for i in ["X","Y","Z"]}
#lowKw = {"PosRotate":"rotation_euler","OfsPos":"location","TargetOfsPos":"location"}
#lowDT = {"%s%s %02d"%(kw,i,j):bl for kw,bl in lowKw.items() for i in ["X","Y","Z",""] for j in range(16) }
def dtIndex(dtt):
    if "x" in dtt or "X" in dtt:
        return [0]
    if "y" in dtt or "Y" in dtt:
        return [1]
    if "z" in dtt or "Z" in dtt:
        return [2]
    return [0,1,2]

blenderProps = [(key,index) for key in ["location","rotation_euler","scale"] for index in range(3)]
uiProps = [t+co for t in ["trans","rot","scl"] for co in ["x","y","z"]]
settingMapping = {blendProp:uiProp for blendProp,uiProp in zip(blenderProps, uiProps)}
defaultProps = {"transx":"m8E8AFE06","transy":"mF98DCE90","transz":"m60849F2A",
                "rotx":"mF105BBE3", "roty":"m86028B75", "rotz":"m1F0BDACF",
                "sclx":"m9486DF23", "scly":"mE381EFB5","sclz":"m7A88BE0F" }

def remapAnalyzer(typing):
    lowClass = []
    midClass = []
    highClass = []
    for transform in typing.transforms:
        transform.datatypeString,_ = hashResolver(transform.datatypeHash)
        transform.shortTypeString =  transform.datatypeString.split("::")[-1]
        dts = transform.shortTypeString 
        ixs = dtIndex(dts)
        if dts in highDT:
            var = highDT[dts]
            array = highClass
        elif dts in midDT:
            var = midDT[dts]
            array = midClass
#        elif dts in lowDT:
#            var = lowDT[dts]
#            array = lowClass
        else:
            continue
        for ix in ixs:
            array.append((timl_propcode[dts],(var,ix)))
    reversemapper = {}
    for prop,bm in lowClass:
        reversemapper[bm] = prop
    for prop,bm in midClass:
        reversemapper[bm] = prop
    for prop,bm in highClass:
        reversemapper[bm] = prop
    mapper = {v:k for k,v in reversemapper.items()}
    reverse_mapper = {ui:reversemapper[b]
                      if b in reversemapper else defaultProps[ui]
                      for b,ui in zip(blenderProps,uiProps)}    
    return mapper,reverse_mapper    

def processTIMLData(datum,remapOperation):
    for typing in datum.types:
        remap,actionProps = remapOperation(typing)
        typing.timelineParameterString = hashResolver(typing.timelineParameterHash)[0]
        typing.remapSettings = actionProps
        for transform in typing.transforms:
            transform.datatype = list(applyRemap(remap,transform.datatypeHash))
            for ix,kf in enumerate(transform.keyframes):
                kf.index = ix
                kf.interpolation = interpolationMapping[kf.transition]
    return datum

def processTIML(rawTIML,remapOperation):
    processed = []
    for datum in rawTIML.data:
        #datum = dataH.data
        datum.types = datum.types
        processTIMLData(datum,remapOperation)
        processed.append(datum)
    return processed

