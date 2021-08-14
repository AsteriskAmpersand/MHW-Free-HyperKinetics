# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 02:52:38 2021

@author: AsteriskAmpersand
"""
from dataclasses import dataclass
from mathutils import Vector,Euler,Quaternion,Matrix
from .lmt_exporter_action_calculators import EncodingObject,SynchronicityObject,InversionObject,FreeHKError
from .blenderOps import breakPath,fetchFreeHKCustom,fetchEncodingType,fetchBoneFunction
from .blenderOps import transformSize
from .lmt_tools import actionDataPath,axislessDataPath
from .tetherOps import getBoneFromPath,boneFunctionMap,basicTransformsForType,basisTransformForType, transformsForType
from ..struct import Lmt
from ..struct.LmtBuffers import typeMapping,lerped,buffered
def wrappedMap(skeleton):
    if not skeleton: return {}
    else: return boneFunctionMap(skeleton)

def breakVector(vec):
    return [vec.x,vec.y,vec.z,vec.w if hasattr(vec,"w") else 0]

@dataclass
class ExternalData():
    frameCount: int = 0
    rotation: tuple = (0,0,0,1)
    translation: tuple = (0,0,0,0)

def getBoneDepth(bone):
    if "__freehk_depth__" in bone:
        return bone["__freehk_depth__"]
    else:
        depth = max([getBoneDepth(child) for child in bone.children],default = 0)+1
        bone["__freehk_depth__"] = depth
        return depth

def generateDepthMap(skeleton):
    maxdepth = 0
    for bone in skeleton.pose.bones:
        maxdepth = max(maxdepth,getBoneDepth(bone))
    skeleton["__freehk_depth__"] = maxdepth
        
def clearTetherDepth(skeleton):
    for bone in skeleton.pose.bones:
        if "__freehk_depth__" in bone:
            del bone["__freehk_depth__"]

class LMTTransform(EncodingObject, SynchronicityObject, InversionObject):
    def __init__(self,action,error_handler,data_path):
        self.data_path = data_path
        self.action = action
        self.error_handler = error_handler
        self.raw_fcurves = []
        self.target,self.transform = breakPath(data_path)
        self.usage = self.getUsage(self.transform)
        self.dataRead,self.dataWrite = transformsForType(self.transform)
        self.basicRead = basicTransformsForType(self.transform)
        self.basisRead = basisTransformForType(self.transform)
        self.eps = 0.0001
    def getUsage(self,transform):
        return {"rotation_quaternion":0,"rotation_euler":0,"location":1,"scale":2}[transform]
    def append(self,fcurve):
        if fcurve is not None:
            fcurve.array_index = fcurve.array_index%4
            self.raw_fcurves.append(fcurve)
    #Validate Channel Count and fill as needed
    def passF(self):
        pass
    def errorOut(self):
        raise FreeHKError
    def executeFunctions(self,functionList):
        def _execute():
            for function in functionList:
                function()
        return _execute
    def report(self,errType,*args):
        self.error_handler.curveOwnership(self)
        self.error_handler.append((errType,self.data_path,self.action.name,*args))
    def fcurveReportPattern(self,errType,fixOp,fixLog,omitOp,omitLog,*err_args):
        self.report(errType,*err_args)
        if self.error_handler.fcurveError.fix:
            self.error_handler.logSolution(fixLog)
            fixOp()
        elif self.error_handler.fcurveError.omit:
            self.error_handler.logSolution(omitLog)
            omitOp()
        else:
            raise FreeHKError
    def patchMissingChannels(self):
        indices = [None for i in range(transformSize(self.transform))]
        for fcurve in self.raw_fcurves:
            indices[fcurve.array_index] = fcurve
        for ix,curveCandidate in enumerate(indices):
            if curveCandidate is None:
                pf = PaddedFCurve()
                pf.data_path = self.data_path
                pf.array_index = ix
                pf.encoding = 0
                pf.boneFunction = -2
                indices[ix] = pf
        self.raw_fcurves = indices
    def validateChannelCounts(self):
        if len(self.raw_fcurves) < transformSize(self.transform):
            try:
                self.fcurveReportPattern("F_LMT_MISSING_CHANNEL",self.patchMissingChannels,"Missing Channels were Added",
                                         self.errorOut,"Transform was omitted from export process")
            except FreeHKError:
                return False        
        return True
    def assignBoneFunction(self,tether,boneFunction):
        pbone = getBoneFromPath(tether,self.data_path)
        if pbone and "boneFunction" in pbone.bone and pbone.bone["boneFunction"] != boneFunction:
            try:
                self.fcurveReportPattern("F_LMT_NAME_FUNCTION_CONFLICT",self.passF,"Bone function set according to the relevant bone",
                                         self.errorOut,"Transform was omitted from export process",
                                         tether.name)
                self.boneFunction = pbone.bone["boneFunction"]                
            except FreeHKError:
                return False
        else:
            self.boneFunction = boneFunction        
        return True
    #Validate and Calculate Bone Functions, Drop Illegals
    def calculateValidateBoneFunction(self,tether):
        boneFunctions = set()
        for curve in self.raw_fcurves:
            boneFunctions.add(curve.boneFunction)
        try:
            boneFunctions.remove(-2)
        except:
            pass
        if len(boneFunctions) != 1:            
            pbone = getBoneFromPath(tether,self.data_path)
            #If there's no tie breaker bone            
            if not pbone or "boneFunction" not in pbone.bone:
                if len(boneFunctions)>1: 
                    self.report("F_LMT_CONFLICTING_BONE_FUNCTION")
                    if self.error_handler.fcurveError.fix or self.fcurveError.omit:
                        self.error_handler.logSolution("Transform omitted from export process")
                    return False
                else:
                    self.report("F_LMT_MISSING_BONE_FUNCTION")
                    return False
            #If there's a tiebreaker bone but it's not one of the choices
            if pbone.bone["boneFunction"] not in boneFunctions:                
                self.report("F_LMT_NAME_FUNCTION_CONFLICT")
                if self.error_handler.fcurveError.fix:
                    self.error_handler.logSolution("Bone function set according to the relevant bone")
                elif self.error_handler.fcurveError.omit:
                    self.error_handler.logSolution("Transform omitted from export process")
                    return False
                else:
                    return False                
            self.boneFunction = pbone.bone["boneFunction"]            
        if len(boneFunctions) == 1:
            self.assignBoneFunction(tether,boneFunctions.pop())
        if self.boneFunction == -1: self.usage = self.usage+3
        return True
    #Get Raw Frames Span
    def getFrameSpan(self):
        if not hasattr(self,"frameSpan"): 
            self.frameSpan = max(map(lambda y: max(map(lambda x: x.co[0],y),default=0),map(lambda x: x.keyframe_points,self.raw_fcurves)),default = 0)
        return max(1,self.frameSpan - 1*self.isRoot())
    def getBasis(self):
        if not self.isRoot():
            raise KeyError("Non Root bones cannot produce a basis")
        else:
            t,vec = self.vector_keyframes[-1]     
            return breakVector(vec)
    def isRoot(self):
        if hasattr(self,"boneFunction"):
            return self.boneFunction==-1
        else:
            raise KeyError("Bone Function not calculated yet")
    def buffered(self):
        return buffered[self.bufferType]
    def lerped(self):
        return lerped[self.bufferType]
    def bufferClass(self):
        return typeMapping[self.bufferType]
    def keyframeCount(self):
        rawCount = len(self.vector_keyframes)
        return rawCount-1-self.isRoot()
    def compile(self):
        struct = Lmt.LMTBoneDataHeader()        
        bufferClass = self.bufferClass()
        size = len(bufferClass())*self.keyframeCount()   
        #lerped and buffered
        tn,refVec = self.vector_keyframes[0]
        basis = breakVector(refVec)
        lerp = None
        buffer = []
        if self.buffered():
            prev,f = self.vector_keyframes[-1] if not self.isRoot() else self.vector_keyframes[-2]
            buffer = []
            if self.lerped():
                mul,add = self.mul(),self.add()
                lerp = Lmt.LMTBasis().construct({"mult":breakVector(mul),"add":breakVector(add)})
                tf = lambda x: ((getattr(vec,x)-getattr(add,x))/getattr(mul,x)) if hasattr(vec,x) and getattr(mul,x) != 0  else 0   
            else:
                tf =  lambda x: getattr(vec,x) if hasattr(vec,x) else 0             
            for t,vec in reversed(self.vector_keyframes[1:] if not self.isRoot() else self.vector_keyframes[1:-1]):
                deltat = prev-t
                buffer.append(bufferClass().construct({**{v:tf(v) for v in ["x","y","z","w"]},"frame":int(deltat)}))
                prev = t
            buffer = list(reversed(buffer))
        struct.construct({"bufferType":self.bufferType,"usage":self.usage,
                  "205":205,"jointType":0,"boneId":self.boneFunction,
                  "weight":1,"bufferSize":size,"bufferOffset":None,
                  "basis":basis,"lerpOffset":None,"lerp":lerp,"keyframes":buffer
                  })
        return struct
            
        
class PaddedFCurve():
    def __init__(self,fcurve = None):
        self.fcurve = fcurve
        if fcurve:
            self.data_path = fcurve.data_path
            self.array_index = fcurve.array_index%4
            self.keyframe_points = fcurve.keyframe_points
            self.synthetic = False
        else:
            self.keyframe_points = []
            self.synthetic = True
    def evaluate(self,t):
        if self.fcurve:
            return self.fcurve.evaluate(t)
        else:
            return 0
    def __str__(self):
        string = self.data_path + "[%d]"%self.array_index +": " + ','.join(map(lambda x: "(%d,%.2f)"%tuple(x.co),self.keyframe_points))
        return string

def clearDictProp(dict,prop):
    if dict:
        if prop in dict:
            del dict[prop]

def passFunc():
    pass

class LMTActionParser():
    def __init__(self,action,error_handler,silent_tether = None):
        tether = None
        self.action = action     
        self.error_handler = error_handler
        self.error_handler.actionOwnership(self.action)        
        try:
            if action.freehk.starType != "LMT_Action":
                self.actionErrorPattern("A_LMT_INVALID_ACTION_TYPE",passFunc,passFunc)
            if silent_tether is not None:
                tether = silent_tether
            else:
                tether = action.freehk.tetherFrame
            if tether:
                functionsMap = wrappedMap(tether)
                generateDepthMap(tether)  
            else:
                functionsMap = {}
            self.refRot = [0,0,0,1]
            self.refTrans = [0,0,0,0]            
            self.valid = True
            #Validate each curve and only keep valid ones
            validFcurves = self.filterCurves(action.fcurves)   
            #Group the curves into transform objects
            channels = self.groupChannels(validFcurves,tether)    
            #Validate ChannelCount and fill as needed
            full_channels = list(filter(lambda x: x.validateChannelCounts(),channels))                        
            #Validate and Calculate Bone Functions, Drop Illegals
            bf_full_channels = list(filter(lambda x: x.calculateValidateBoneFunction(tether),full_channels))
            #Calculate Frame Count
            self.frameCount = self.calculateFrameCount(bf_full_channels)  
            #Validate Synchronicity
            sync_bf_full_channels = list(filter(lambda x: x.validateSynchronicity(self.frameCount),bf_full_channels))
            #Validate Tether Inversibility
            inversible_channels = list(filter(lambda x: x.validateInversibility(tether,functionsMap),sync_bf_full_channels))
            for channel in inversible_channels: channel.generateVectorKeyframes()
            #Validate Transform Encoding Type
            valid_channels = list(filter(lambda x: x.calculateValidateEncoding(tether),inversible_channels))

            self.getBasis(valid_channels)
            self.external = ExternalData(self.frameCount,self.refRot,self.refTrans)
            transforms = list(map(lambda x: x.compile(),valid_channels))
            self.transforms = transforms
        except FreeHKError:
            self.invalidate()
            #Nothing to do, animation must be removed
            pass
        finally:
            if tether:
                clearDictProp(tether,"__freehk_depth__")
                clearTetherDepth(tether)            
    def invalidate(self,*args,**kwargs):
        self.valid = False
    def getBasis(self,validChannels):
        for transform in validChannels:
            if transform.isRoot():
                vec = transform.getBasis()
                if transform.usage%3 == 0:
                    self.refRot = vec
                if transform.usage%3 == 1:
                    self.refTrans = vec
    
    def calculateFrameCount(self,bf_channels):
        if self.action.freehk.frameCount != -1:
            frameCount = self.action.freehk.frameCount
            if not self.verifyFrameCount(bf_channels):
                self.valid = False
                raise FreeHKError
        else:
            frameCount = int(max(1,max(map(lambda x: x.getFrameSpan(),bf_channels),default = 1)))
        return frameCount
    def verifyFrameCount(self,bf_channels):
        for transform in bf_channels:
            suggestedEntryCount = transform.getFrameSpan()
            if self.action.freehk.frameCount < suggestedEntryCount:
                def assignFC():
                    self.action.freehk.frameCount = suggestedEntryCount
                try:self.actionErrorPattern("A_LMT_FRAME_COUNT_LOW",assignFC,passFunc)
                except:return False
        return True
    def actionErrorPattern(self,errType,fixOp,omitOp):
        self.actionErr(errType)
        if self.error_handler.actionError.fix:
            fixOp()
        elif self.error_handler.fcurveError.omit:
            omitOp()
        else:
            self.invalidate()
            raise FreeHKError
        
    def checkUncustomizedFCurve(self,fcurve):
        self.fcurveErr("F_LMT_UNCUSTOMIZED_FCURVE",fcurve)
        if self.error_handler.fcurveError.fix:
            self.error_handler.logSolution("FCurve was given default customization (Calculate bone function and encoding)")
            nfcurve = PaddedFCurve(fcurve)
            nfcurve.boneFunction = -2
            nfcurve.encoding = 0
            return nfcurve
        elif self.error_handler.fcurveError.omit:
            self.error_handler.logSolution("FCurve was omitted from export process")
            return None
        else:
            return None        
    
    def checkCustomizedFCurve(self,fcurve):
        nfcurve = PaddedFCurve(fcurve)
        nfcurve.encoding = fetchEncodingType(fcurve)
        nfcurve.boneFunction = fetchBoneFunction(fcurve)
        if nfcurve.encoding not in [0,1,2,3,4,5,6,7,11,12,13,14,15]:
            self.fcurveErr("F_LMT_INVALID_ENCODING_TYPE",fcurve,nfcurve.encoding)
            if self.error_handler.fcurveError.fix:
                nfcurve.encoding = 0
                self.error_handler.logSolution("Encoding Type was set to auto-detect (0)")
            elif self.error_handler.fcurveError.omit:
                self.error_handler.logSolution("FCurve was omitted from export process")
                return None
        if nfcurve.boneFunction < -2:
            self.fcurveErr("F_LMT_INVALID_BONE_FUNCTION",fcurve,nfcurve.boneFunction)
            if self.error_handler.fcurveError.fix:
                nfcurve.boneFunction = -2
                self.error_handler.logSolution("Bone Function was set to auto-detect (-2)")
            elif self.error_handler.fcurveError.omit:
                self.error_handler.logSolution("FCurve was omitted from export process")
                return None
        return nfcurve
    
    def validateFCurve(self,fcurve):
        mod = fetchFreeHKCustom(fcurve)
        if not mod:
            return self.checkUncustomizedFCurve(fcurve)
        else:
            return self.checkCustomizedFCurve(fcurve)
    
    def filterCurves(self,fcurves):
        valid = []
        knownCurves = set()
        for fcurve in fcurves:
            if len(fcurve.keyframe_points) == 0:
                self.fcurveErr("F_LMT_EMPTY_FCURVE",fcurve)
                if self.error_handler.fcurveError.fix or self.error_handler.fcurveError.omit:
                    self.error_handler.logSolution("Fcurve was omitted from the export process")
                else:
                    continue                
            if (fcurve.data_path,fcurve.array_index) in knownCurves:
                self.fcurveErr("F_LMT_DUPLICATE_FCURVE",fcurve)
                if self.error_handler.fcurveError.fix or self.error_handler.fcurveError.omit:
                    self.error_handler.logSolution("Fcurve was omitted from the export process")
            else:
                target,transform = breakPath(fcurve.data_path)
                if transform not in ["rotation_quaternion","rotation_euler","scale","location"]:                
                    self.fcurveErr("F_LMT_UNEXPORTABLE_PROPERTY",fcurve)
                    if self.error_handler.fcurveError.fix or self.error_handler.fcurveError.omit:
                        self.error_handler.logSolution("FCurve was omitted from the export process")
                else:
                    nfcurve = self.validateFCurve(fcurve)
                    if nfcurve is not None:
                        knownCurves.add((fcurve.data_path,fcurve.array_index))
                        valid.append(nfcurve)
        
        return valid

    def groupChannels(self,validfcurves,tether):
        transforms = set()
        unique_transforms = {}
        for fcurve in validfcurves:
            vix = 1 if (fcurve.data_path,fcurve.array_index) in transforms else 0
            transforms.add((fcurve.data_path,fcurve.array_index))
            if (fcurve.data_path,vix) not in unique_transforms:
                unique_transforms[(fcurve.data_path,vix)] = LMTTransform(self.action,self.error_handler,fcurve.data_path)                
            unique_transforms[(fcurve.data_path,vix)].append(fcurve)
        return unique_transforms.values()                    
    
    def actionErr(self,errType):
        self.error_handler.actionOwnership(self.action)
        self.error_handler.append((errType,self.action.name))        
    def fcurveErr(self,errType,fcurve,*args):
        self.error_handler.actionOwnership(self.action)
        self.error_handler.curveOwnership(fcurve)
        self.error_handler.append((errType,actionDataPath(fcurve),self.action.name,*args))
    def skeletonErr(self,bone,armature):
        self.error_handler.actionOwnership(self.action)
        self.error_handler.append(("F_LMT_UNINVERSIBLE_MATRIX",bone.name,armature.name))
    
    def export(self):
        if not self.valid:
            None, None
        #Actually Compile the internals into lerp-ed form
        #TODO - Implement
        return self.external,self.transforms
    
#LMTActionParser(self.input_action,self.error_handler).export()