# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 20:37:56 2021

@author: AsteriskAmpersand
"""
import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import Matrix,Vector,Quaternion,Euler
from .blenderOps import breakPath,transformSize,setBoneFunction,fetchBoneFunction,replaceBoneName,customizeFCurve

class FreeHK_IncompleteFCurve(Exception): 
    # Constructor or Initializer 
    def __init__(self, errlist): 
        self.errors = errlist

def extractNonReference(fcurveSet):
    sortedTuples = [list(sorted(filter(lambda x: x.co[0]>=0,fcurve.keyframe_points),key = lambda x: x.co[0])) for fcurve in fcurveSet]
    return sortedTuples

def extractChannels(fcurveSet):
    sortedTuples = [list(sorted(fcurve.keyframe_points,key = lambda x: x.co[0])) for fcurve in sorted(fcurveSet,key = lambda x: x.array_index)]
    return sortedTuples

def extractAllFrames(fcurveSet):
    channels = extractChannels(fcurveSet)
    return [tuple(map(lambda x: x.co[1],frameTuple)) for frameTuple in zip(*channels)]

def channelToVec(channels):
    return list(zip(*channels))

def vecToChannels(vecs):
    return channelToVec(vecs)

def verifySynchronicity(fcurveSet):
    sortedKeyframes = extractChannels(fcurveSet)
    lengths = list(map(len,sortedKeyframes))
    maxlength = max(lengths)
    minlength = min(lengths)
    if maxlength != minlength:
        return False
    for timeTuple in zip(*sortedKeyframes):
        timings = [t.co[0] for t in timeTuple]
        maxima,minima = max(timings),min(timings)
        if maxima != minima:
            return False
    return True

CHANNEL_COUNT = 0
SYNCHRONICITY = 1

def verifyTuplings(action):
    propertyDictionary = {}
    propertySize = {}
    errors = []
    for fcurve in action.fcurves:
        actionPath = fcurve.data_path
        transformTarget,transformType =  breakPath(actionPath)
        tsize = transformSize(transformType)
        fold = fcurve.array_index//4
        if not tsize:
            continue
        else:
            propertySize[actionPath] = tsize
        if (actionPath,fold) not in propertyDictionary:
            propertyDictionary[(actionPath,fold)] = []
        propertyDictionary[(actionPath,fold)].append(fcurve)
    for (actionPath,fold) in propertyDictionary:
        if len(propertyDictionary[(actionPath,fold)]) != propertySize[actionPath]:
            errors.append(((actionPath,fold),CHANNEL_COUNT))
        if not verifySynchronicity(propertyDictionary[(actionPath,fold)]):
            errors.append(((actionPath,fold),SYNCHRONICITY))
    return errors, propertyDictionary

def extractReference(fcurve):
    reference = None
    for keyf in fcurve:
        if keyf.co[0] == -1:
            reference = keyf.co[1]
    if reference is None:
        reference = 0
    return reference
        
def reconstructReference(fcurveSet):
    return [extractReference(fcurve) for fcurve in sorted(fcurveSet,lambda x: x.array_index)]

def collectTuplings(action):
    errs,curves = verifyTuplings(action)
    tuplings = []
    if errs:
        #TODO - Handle incomplete tuplings on more "idiot proof" modes
        raise FreeHK_IncompleteFCurve(errs)
    for (path,fold),fcurves in curves.items():
        #referenceFrame = reconstructReference(fcurves)
        keyframes = extractAllFrames(fcurves)
        tuplings.append(((path,fold),fcurves,keyframes))
    return tuplings
    #TODO - Patch from here on as well
        
def insertVectorialKeymatches(fcurveSet,channelReplacements):
    sortedChannels = extractChannels(fcurveSet)
    for channel,newframes in zip(sortedChannels,channelReplacements):
        for frame,value in zip(channel,newframes):
            frame.co[1] = value
    for f in fcurveSet:
        f.update()
    return

def updateAnimationBoneFunctions(skeleton,action):
    for fcurve in action.fcurves:
        try:
            pbone = getBoneFromPath(skeleton,fcurve.data_path)
            if "boneFunction" not in pbone.bone: raise ValueError("Functionless Bone %s"%pbone.name)
            function = pbone.bone["boneFunction"]
            setBoneFunction(fcurve,function)
        except:
            #TODO - Need an error handler to log the errors happening here
            pass

def boneFunctionMap(skeleton):
    return {bone.bone["boneFunction"]:bone for bone in skeleton.pose.bones if "boneFunction" in bone.bone}

def updateAnimationNames(skeleton,action):
    if skeleton:        
        skeletonFunctions = boneFunctionMap(skeleton)
        for fcurve in action.fcurves:
            func = fetchBoneFunction(fcurve)
            if func in skeletonFunctions:
                nbone = skeletonFunctions[func]
                fcurve.data_path = replaceBoneName(fcurve.data_path,nbone.name)
    
def getBoneFromPath(armature,path):
    try: 
        return armature.path_resolve(path).owner.data
    except:
        return None

def scaleMatrix(vec):
    m = Matrix.Identity(4)
    for i in range(len(vec)):
        m[i][i]=vec[i]
    return m

def translationMatrix(vec):
    m = Matrix.Identity(4)
    for i in range(len(vec)):
        m[i][3]=vec[i]
    return m

def basisTransformForType(ttype):
    if ttype == "rotation_quaternion":
        return Quaternion
    elif ttype == "location":
        return Vector
    elif ttype == "scale":
        return Vector
    elif ttype == "rotation_euler":
        return Quaternion

def basicTransformsForType(ttype):
    if ttype == "rotation_quaternion":
        return lambda x: Quaternion(x)
    elif ttype == "location":
        return lambda x: Vector(x)
    elif ttype == "scale":
        return lambda x: Vector(x)
    elif ttype == "rotation_euler":
        return lambda x:  Euler(x)

def transformsForType(ttype):
    if ttype == "rotation_quaternion":
        dataRead = lambda x: Quaternion(x).to_matrix().to_4x4()
        dataWrite = lambda x: x.to_quaternion()
    elif ttype == "location":
        dataRead = lambda x: translationMatrix(Vector(x))
        dataWrite = lambda x: x.to_translation()
    elif ttype == "scale":
        dataRead = lambda x:  scaleMatrix(Vector(x))
        dataWrite = lambda x: x.to_scale()
    elif ttype == "rotation_euler":
        dataRead = lambda x:  Euler(x).to_matrix().to_4x4()
        dataWrite = lambda x: x.to_euler()
    return dataRead,dataWrite
   
def strackerForwardTransform(bone,nmatrix):
    try:
        local = bone.bone.matrix_local.inverted()#(bone.matrix.inverted()*bone.matrix_channel)
    except:
        print(bone.name)
        print(bone.matrix)
        raise
    if not bone.parent:
        return local*nmatrix
    else:
        parent = bone.parent.bone.matrix_local#bone.parent.matrix_channel.inverted()*bone.parent.matrix
        return local*parent*nmatrix

def strackerInverseTransform(bone,nmatrix):
    try:
        local = bone.bone.matrix_local#(bone.matrix.inverted()*bone.matrix_channel)
    except:
        print(bone.name)
        print(bone.matrix)
        raise
    if not bone.parent:
        return local*nmatrix
    else:
        parent = bone.parent.bone.matrix_local#bone.parent.matrix_channel.inverted()*bone.parent.matrix
        return parent.inverted()*local*nmatrix

def e_output(*args,**kwargs):
    pass

def boneTransform(bone,ttype,kfTuplets,operation):
    read,write = transformsForType(ttype)    
    return [write(operation(bone,read(keyf))) for keyf in kfTuplets]
    
def unapplyBoneTransform(bone,ttype,kfTuplets):
    return vecToChannels(boneTransform(bone,ttype,kfTuplets,strackerInverseTransform))

def applyBoneTransform(bone,ttype,kfTuplets):
    return vecToChannels(boneTransform(bone,ttype,kfTuplets,strackerForwardTransform))
        
def tetherOperator(action,tether,preUpdateFunction,updateFunction,postUpdateFunction):
    if not tether:
        return
    addon_key = __package__.split('.')[0]
    addon = bpy.context.user_preferences.addons[addon_key]
    implicitTether = addon.preferences.implicit_tether 
    if implicitTether:
        armature = tether
        preUpdateFunction(armature,action)
    #TODO - Handle error from missing tuplings.
    tuplings = collectTuplings(action)
    for (path,fold), fcurves, vectorKeys in tuplings:        
        animBone = getBoneFromPath(tether,path)
        if animBone:
            transformTarget,transformType =  breakPath(path)
            updatedKeyframeChannels = updateFunction(animBone,transformType,vectorKeys)
            postUpdateFunction(fcurves, updatedKeyframeChannels)
        

#before clearing the tether, assign bone functions if the armature
#has a compatible bone, even if the link isn't explicit already
#when re-tethering check the orphans for bone functions the new one might have
#and proceed to rename appropiately

#Tether TO is based on bone function (So call updateAnimationNames)
#Tether FROM is based on bone name (So call updateAnimationBoneFunction)

def clearReferences(action):
    tether = action.freehk.tetherFrame
    
    preUpdateFunction = updateAnimationBoneFunctions
    updateFunction = unapplyBoneTransform
    postUpdateFunction = insertVectorialKeymatches
    tetherOperator(action,tether,preUpdateFunction,updateFunction,postUpdateFunction)
            
    action.freehk.tetherFrame = None

def targetReferenceFromClear(action,referenceFrame):
    tether = referenceFrame

    preUpdateFunction = updateAnimationNames
    updateFunction = applyBoneTransform
    postUpdateFunction = insertVectorialKeymatches
    tetherOperator(action,tether,preUpdateFunction,updateFunction,postUpdateFunction)
            
    action.freehk.tetherFrame = referenceFrame

"""    
def prepareExportAction(action,options):
    stowed = []
    def stowActions(self,fcurves,updatedKeyframeChannels):
        stowed += updatedKeyframeChannels
    tether = action.freehk.tetherFrame
    
    if not options.applyPatchLevels(action):
        return None
        
    preUpdateFunction = updateAnimationBoneFunctions
    updateFunction = unapplyBoneTransform
    postUpdateFunction = pass
    tetherOperator(action,tether,preUpdateFunction,updateFunction,postUpdateFunction)
    
    return
"""
    
def transferTether(actions,tether):
    for action in actions:
        clearReferences(action)
        targetReferenceFromClear(action, tether)
        
def completeMissingChannels(action): 
    errs, curveMap = verifyTuplings(action)
    for (actionPath,fold),errType in errs:
        if errType == CHANNEL_COUNT:
            transformTarget,transformType =  breakPath(actionPath)
            tsize = transformSize(transformType)
            missingIndices = set(range(tsize))
            for curve in curveMap[(actionPath,fold)]:
                try:
                    missingIndices.remove(curve.array_index%4)
                except:
                    pass
            for i in missingIndices:
                f = action.fcurves.new(data_path = actionPath, index = i+4*fold)
                f.mute = fold
                customizeFCurve(f, starType = 0,boneFunction = -2)
                
                
def synchronizeKeyframes(action):
    errs, curveMap = verifyTuplings(action)
    for (actionPath,fold),errType in errs:
        if errType == SYNCHRONICITY:
            curvePoints = [set((k.co[0] for k in curve.keyframe_points if k.co[0]>=0)) for curve in curveMap[(actionPath,fold)]]
            synchronizedSet = set()
            for c in curvePoints: synchronizedSet = synchronizedSet.union(c)
            for points,curve in zip(curvePoints,curveMap[(actionPath,fold)]):
                newPoints = synchronizedSet.difference(points)
                values = []
                for point in newPoints:
                    t = point
                    values.append((t,curve.evaluate(t)))
                for v in values:
                    kp = curve.keyframe_points.insert(*v)

def resampleFCurve(fcurve,resampleRate):
    frames = list(sorted(((k.co[0] for k in fcurve.keyframe_points if k.co[0]>=0))))
    for l,r in zip(frames[:-1],frames[1:]):
        distance = r-l
        values = []
        for d in range(int((distance-1)//resampleRate)):
            t = l+(d+1)*resampleRate
            values.append((t,fcurve.evaluate(t)))
        for v in values:
            kp = fcurve.keyframe_points.insert(*v)
            

def resampleAction(action,resampleRate):
    for fcurve in action.fcurves:
        resampleFCurve(fcurve,resampleRate)