# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 15:56:52 2020

@author: AsteriskAmpersand
"""
from ..common import Constants as ct

import bpy
import bisect
from collections import OrderedDict

class NonSkeletonAnimationError(Exception):
    pass

class MultipleRootsError(Exception):
    pass

class RNAPath():
    def __init__(self,rnapath,dimension):
        bone,transform = self.tokenize(rnapath)
        self.path = rnapath
        self.bone = bone
        self.boneIndex = None
        self.transform = transform
        self.dimension = dimension
        self.type = self.bone != ""
    def tokenize(self,rnapath):
        tokens = []
        current = ""
        bone = ""
        stringChar = None
        transform = None
        stringActive = False
        ignore = False
        for char in rnapath:
            if not stringActive:
                if char == ".":
                    tokens.append(current)
                    current = ""
                elif char in ["'",'"']:
                    stringActive=True
                    stringChar = char
                    current += char
                else:
                    current += char
            else:
                if char == "\\":
                    ignore = True
                elif char == stringChar and not ignore:
                    stringActive = False
                else:
                    bone += char
                    ignore = False
                current += char
        tokens.append(current)
        transform =  ct.transform_map[current] if current in ct.transform_map else ct.UNKN
        return bone,transform    
    def stringBoneIndex(self):
        try:
            self.boneIndex = int(self.bone.split(".")[1])
        except:
            pass
        return self.boneIndex    
    def key(self):
        return (self.bone,self.transform,self.dimension)

class StarFrame():
    def __init__(self,frame):   
        self.index = frame.co[0]
        self.value = frame.co[1]
        self.easing = frame.easing
        self.interpolation = frame.interpolation
        self.period = frame.period
        self.amplitude = frame.amplitude
        self.handle_left = frame.handle_left
        self.handle_right = frame.handle_right

class StarFrameSet():
    def __init__(self,transform,dimension,frames):
        self.keyframes = [StarFrame(frame) for frame in frames]
        self.transform = transform
        self.dimension = dimension
    def concat(self,frames):
        self.keyframes += [StarFrame(frame) for frame in frames]
        self.keyframes.sort()        
    def key(self):
        return (self.transform,self.dimension)        
    def merge(self,frame):
        if self.key() != frame.key():
            raise ValueError("Star Frame Mismatch")
        self.keyframes += frame.keyframes
        self.keyframes = sorted(self.keyframes,key = lambda x: x.index)
    def __iter__(self):
        return iter(self.keyframes)
    def __repr__(self):
        result = ""
        result+="\n"+ct.inverse_transform[self.transform]+"["+str(self.dimension)+"]"
        for frame in self.keyframes:
            result += "\n\t(%.2f,%.2f)"%(frame.index,frame.value)
        return result

class StarObject():
    def __init__(self,header,keyframes = None):
        if keyframes is None:
            keyframes = {}
        self.name = header.bone
        self.boneName = header.bone    
        self.keyframes = keyframes
    def rename(self,name):
        self.name = name
    def key(self):
        return self.name
    def __contains__(self,key):
        return key in self.keyframes
    def append(self,frame):
        key = frame.key() 
        if key not in self:
            self.keyframes[key] = frame
        else:
            self.keyframes[key].merge(frame)
    def __getitem__(self,key):
        return self.keyframes[key]
    def __setitem__(self,key,val):
        self.keyframes[key] = val
    def merge(self,starObj):
        for key in starObj.keyframes:
            if key not in self:
                self[key] = starObj[key]
            else:
                self[key].merge(starObj[key])
    def setBone(self,index=None):
        if index is None:
            self.boneName = int(self.boneName.split(".")[-1])
        else:
            self.boneName = index
    def sort(self):
        self.keyframes = OrderedDict(sorted([(key,val)
                                                for key,val in self.keyframes.items()],
                                                key=lambda x: x[0]))
        return self
    def __iter__(self):
        return iter([self.keyframes[key] for key in self.keyframes])
    def __repr__(self):            
        result = ""
        result+="\n"+self.name+"\n"
        for key in self.keyframes:
            result += str(self.keyframes[key]).replace("\n","\n\t")
        result += "\n"
        return result

class StarAnimation():
    def __init__(self,name):
        self.name = name
        self.transforms = {}
    def rename(self,name):
        self.name = name
    def tagChildren(self):
        for key in self.transforms:
            self[key].rename(self.name +("." if self[key].name else "")+self[key].name)
            self[self[key].name] = self[key]
            del self[key]
    def append(self,starObj):
        key = starObj.key()
        if key not in self:
            self[key] = starObj
        else:
            self.transforms[key].merge(starObj)
    def insertData(self,header,dimension,frame):
        frameHolder = StarFrameSet(header.transform,dimension,frame)
        obj = StarObject(header,{frameHolder.key():frameHolder})
        self.append(obj)
    def __getitem__(self,key):
        return self.transforms[key]
    def __setitem__(self,key,value):
        self.transforms[key] = value
    def __delitem__(self,key):
        del self.transforms[key]
    def __contains__(self,key):
        return key in self.transforms
    def __iter__(self):
        return iter(self.transforms.values())
    def merge(self,anim,rename = False):
        for key in anim.transforms:
            if key in self:
                self[key].merge(anim[key])
            else:
                self[key] = anim[key]
    def setBone(self,index=None):
        for key in self.transforms:
            self.transforms[key].setBone(index)
    def denumerateToBones(self,mapping):
        for key in self.transforms:
            if self.transforms[key].name in mapping:
                self.transforms[key].setBone(mapping[self.transforms[key].name])
    def sort(self):
        self.transforms = OrderedDict(sorted([(key,transform.sort()) 
                            for key,transform in self.transforms.items()],
                            key=lambda x: x[1].boneName))
        return self
    def __repr__(self):
        result = ""
        result+="\n"+self.name+"\n"
        for key in self.transforms:
            result += str(self.transforms[key]).replace("\n","\n\t")
        result += "\n"
        return result

class ExchangeFormat():
    def starFromAction(self,action):
        animation = StarAnimation(action.name)
        for curve in action.fcurves:
            dimension = curve.array_index
            header = RNAPath(curve.data_path,dimension)
            animation.insertData(header, dimension, curve.keyframe_points)
        return animation
    def packageScene(self):
        actions = []
        if bpy.data.actions:            
            for action in bpy.data.actions:
                animation = self.starFromAction(action)
                actions.append(animation)    
        self.actions = actions
        return actions
    def traverseHierarchy(self,root,callback,index=-1,mapping={}):
        callback(root,index,mapping)
        #mapping[keyf(root)] = valf(root,index)#root.name
        index += 1
        for children in root.children:
            index,mapping = self.traverseHierarchy(children,callback,index,mapping)
        return index,mapping    
    def parseEmptySkeleton(self,emptyRoot,use_name = False):
        #keyf = lambda x: x.name
        #valf = lambda x,i: i
        actionBuffer = []
        def callback(root,index,mapping):
            if root.animation_data:
                if root.animation_data.action:
                    animation = self.starFromAction(root.animation_data.action)
                    animation.setBone(None if use_name else index)
                    animation.rename(root.name)
                    actionBuffer.append(animation)
        self.traverseHierarchy(emptyRoot,callback)
        self.actions = actionBuffer
        self.mergeActions(False)
    def parseEmptySkeletonFunctions(self,emptyRoot):
        #keyf = lambda x: x.name
        #valf = lambda x,i: x["boneFunction"] if "boneFunction" in x else -1
        actionBuffer = []
        def callback(root,index,mapping):
            if root.animation_data:
                if root.animation_data.action:
                    animation = self.starFromAction(root.animation_data.action)
                    animation.setBone(root["boneFunction"])
                    animation.rename(root["boneFunction"])
                    actionBuffer.append(animation)        
        self.traverseHierarchy(emptyRoot,callback)
        self.actions = actionBuffer
        self.mergeActions(False)
    def parseSkeleton(self,skeleton,use_name = False):
        keyf = lambda x: x.name
        valf = lambda x,i: None if use_name else i
        def callback(root,index,mapping):
            mapping[keyf(root)] = valf(root,index)
        rootBone = self.getSkeletonRoot(skeleton)
        _,mapping = self.traverseHierarchy(rootBone,callback)
        self.assignSkeleton(skeleton,mapping)
    def parseSkeletonFunctions(self,skeleton):
        keyf = lambda x: x.name
        valf = lambda x,i: x["boneFunction"] if "boneFunction" in x else -1
        def callback(root,index,mapping):
            mapping[keyf(root)] = valf(root,index)
        rootBone = self.getSkeletonRoot(skeleton)
        _,mapping = self.traverseHierarchy(rootBone,callback)
        self.assignSkeleton(skeleton,mapping)
        return mapping    
    def getSkeletonRoot(self,skeleton):
        roots = [bone for bone in skeleton.data.bones if bone.parent is None]
        if len(roots)>1:
            raise MultipleRootsError("%d Roots Found for Skeleton %s"%(len(roots),skeleton.name))
        return roots[0]
    def assignSkeleton(self,skeleton,mapping):
        self.packageScene()
        for action in self.actions:
            action.denumerateToBones(mapping)
    def mergeActions(self,preserveSplit = True):
        if not self.actions:
            return
        result = self.actions[0]
        if preserveSplit: result.tagChildren()
        for action in self.actions[1:]:
            if preserveSplit: action.tagChildren()            
            result.merge(action)
        result.rename("MergedAnimation")
        self.actions = [result]
    def sort(self):
        for action in self.actions:
            action.sort()
        return self
    def __iter__(self):
        return iter(self.actions)
    def __repr__(self):
        res = ""
        delim = "======================================"
        for action in self.actions:
            res += delim+"\n"+str(action)+"\n"+delim +"\n"
        return res

if __name__ in "__main__":
    exf = ExchangeFormat()
    exf.parseSkeleton(bpy.context.active_object)
    for ac in exf.actions:
        print(str(ac))