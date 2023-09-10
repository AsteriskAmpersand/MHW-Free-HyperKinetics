# -*- coding: utf-8 -*-
"""
Created on Mon Aug  9 05:04:08 2021

@author: AsteriskAmpersand
"""
from .lmt_tools import actionDataPath,axislessDataPath
from .tetherOps import strackerInverseTransform

from mathutils import Vector

class FreeHKError(Exception):
    pass

class EncodingObject():
    def checkPrepassEncoding(self,encodings):
        for encoding in encodings:
            if encoding not in [1,2,3,4,5,6,7, 11,12,13,14,15]:
                encodings.remove(encoding)
                self.reportEncodingType("F_LMT_INVALID_ENCODING_TYPE")
                if self.error_handler.fcurveError.fix:
                    self.error_handler.logSolution("Transform %s Encoding set to autodetection"%axislessDataPath(self.datapath))
                elif self.error_handler.fcurveError.omit:
                    self.error_handler.logSolution("Transform %s omitted from export process"%axislessDataPath(self.datapath))
                    return False
                else:
                    return False
        if len(encodings) >1:
            self.report("F_LMT_CONFLICTING_ENCODING_TYPE")
            if self.error_handler.fcurveError.fix:
                self.error_handler.logSolution("Transform %s Encoding set to autodetection"%axislessDataPath(self.datapath))
            elif self.error_handler.fcurveError.omit:
                self.error_handler.logSolution("Transform %s omitted from export process"%axislessDataPath(self.datapath))
                return False
            else:
                return False
        return True  
    def reportEncoding(self,errtype,encoding):
        self.reportEncodingType(errtype,encoding)
        if self.error_handler.fcurveError.fix:
                self.error_handler.logSolution("Transform %s Encoding set to autodetection"%axislessDataPath(self.datapath))
        elif self.error_handler.fcurveError.omit:
            self.error_handler.logSolution("Transform %s omitted from export process"%axislessDataPath(self.datapath))
            return False
        else:
            return False
        return True
    def reportNonReference(self,encoding):
        return self.reportEncoding("F_LMT_INVALID_ENCODING_NONKEY",encoding)
    def reportReference(self,encoding):
        return self.reportEncoding("F_LMT_INVALID_ENCODING_KEY",encoding)
    def reportRotation(self,encoding):
        return self.reportEncoding("F_LMT_INVALID_ENCODING_ROT",encoding)
    def reportNonRotation(self,encoding):
        return self.reportEncoding("F_LMT_INVALID_ENCODING_NONROT",encoding)
    def verifyCompatibility(self,encoding):
        if encoding in {1,2}:
            if not self.isReference():
                return self.reportNonReference(encoding)
            elif encoding == 1 and self.isRotation():
                return self.reportRotation(encoding)
            elif encoding == 2 and not self.isRotation():
                return self.reporttNonRotation(encoding)        
        elif encoding in {3,4,5}:
            if self.isRotation():
                return self.reportRotattion(encoding)            
        elif encoding in {6,7,11,12,13,14,15}:
            if not self.isRotation():
                return self.reporttNonRotation(encoding)
        return True
            
    def calculateValidateEncoding(self,tether):
        encodings = set()
        for fcurve in self.raw_fcurves:
            encodings.add(fcurve.encoding)
        try: encodings.remove(0)
        except: pass    
        if not self.checkPrepassEncoding(encodings): 
            return False            
        #For dynamic encoding verify depth of tether for precision
        #classes = self.compatibilityClasses()
        if len(encodings) == 1:
            encoding = next(iter(encodings))
            if not self.verifyCompatibility(encoding): 
                return False
        else:
            encoding = self.calculateTypeBuffer(tether)
        self.bufferType = encoding
        return True
    def isReference(self):
        return len(self.vector_keyframes) == 1 or (len(self.vector_keyframes) == 2 and self.isRoot())
    def isRotation(self):
        return self.usage%3 == 0  
    def checkAxis(self,axis):
        if not self.isRotation(): return False
        for t,keyframe in self.vector_keyframes:
            if getattr(keyframe,axis) < self.eps: return False            
        return True
    def bounds(self):
        if hasattr(self,"boundary"):
            return self.boundary
        keyframeValues = [vec
                          for t,vec in (self.vector_keyframes[1:] 
                                      if not self.isRoot() 
                                      else self.vector_keyframes[1:-1])]        
        maxima =  list(map(max,zip(*keyframeValues)))
        minima =  list(map(min,zip(*keyframeValues)))
        boundary = self.basisRead([l-r for l,r in zip(maxima,minima)])
        self.boundary = boundary
        self.offset = self.basisRead(minima)
        return boundary
    def mul(self):
        if hasattr(self,"boundary"):
            return self.boundary
        else:
            return self.bounds()
    def add(self):
        if hasattr(self,"offset"):
            return self.offset
        else:
            self.bounds()
            return self.offset
    def monoaxial(self):        
        x = self.checkAxis("x")
        y = self.checkAxis("y")
        z = self.checkAxis("z")
        if x and not y and not z:
            return 11
        if not x and y and not z:
            return 12
        if not x and not y and z:
            return 13        
        return None
    def calculateTypeBuffer(self,tether):
        if self.isReference():
            return 2 if self.isRotation else 1
        monoaxial = self.monoaxial()
        if monoaxial: return monoaxial           
        if self.isRotation():
            return self.calculateRotationType(tether)
        else:
            return self.calculateNonRotationType(tether)
    def calculateRotationType(self,tether):
        #Calculate depth and multiply transform error delta to "approximate error propagation"
        #if no depth assume a depth of 10 as average
        #set epsilon to something like 0.001 for rotations and 0.1 for translations and 0.001 for scale        
        comparisonPoint = Vector(self.bounds()).length
        if comparisonPoint < 0.3:
            return 7
        if comparisonPoint < 1:
            return 15
        if comparisonPoint > 2:
            return 6
        else:
            return 14
        #or just set everything to 14
    def calculateNonRotationType(self,tether):
        if self.usage%3 == 1:
            #Translation
            comparisonPoint = max(self.bounds())
            if comparisonPoint < 30:
                return 5
            elif comparisonPoint < 300:
                return 4
            else:
                return 3
        if self.usage%3 == 2:
            #Scale
            comparisonPoint = max(self.bounds())
            if comparisonPoint > 2.2:
                return 4
            elif comparisonPoint > 0.4:
                return 5
            else:
                return 3


    
class SynchronicityObject():
    def calculatePotentialMissing(self,timingSet,frameCount):
        potentialMissingFrames = []
        if self.isRoot():
            if len(timingSet) == 1 and 0 in timingSet:
                potentialMissingFrames+=[3]
            elif len(timingSet) == 1 and frameCount+1 in timingSet:
                potentialMissingFrames+=[0]
            elif len(timingSet) != 2 or 0 not in timingSet or frameCount+1 not in timingSet:
                potentialMissingFrames += [0,1,2,3]
        else:
            if not(len(timingSet) == 1 and 0 in timingSet):
                potentialMissingFrames+=[0,1,2]
        return potentialMissingFrames
    def missingSpecificFrame(self,timingSet,frameVal,errtype):
        if frameVal not in timingSet:
            self.report(errtype)
            if self.error_handler.fcurveError.fix or self.error_handler.fcurveError.omit:
                self.error_handler.logSolution("Obtained Frame through Interpolation")
                timingSet.add(frameVal)
                return 1
            else:
                raise FreeHKError
        return 0
    def completeRawKeyframes(self,curve,timingSet,adjust):
        if curve.fcurve:
            if not curve.synthetic and len(curve.keyframe_points) < len(timingSet)-adjust:
                self.report("F_LMT_UNSYNCHRONIZED_KEYFRAMES")
                if self.error_handler.fcurveError.fix:
                    self.error_handler.logSolution("Reconstructed missing keyfreams through Interpolation")
                elif self.error_handler.fcurveError.omit:
                    self.error_handler.logSolution("Omitted Transform from Export Process")
                    return False
                else:
                    return False            
        kf = [curve.evaluate(i) for i in timingSet]
        return kf
    #Validate Synchronicity
    def validateSynchronicity(self,frameCount):
        self.frameCount = frameCount
        #Generate the list of keyframe timings
        timingSet = set()
        for curve in self.raw_fcurves:
            for k in curve.keyframe_points:
                timingSet.add(k.co[0])
        #Check Potential Missing Frames, track "extra frames"
        adjust = 0
        potentialMissingFrames = self.calculatePotentialMissing(timingSet,frameCount)                
        frames = [0,1,frameCount,frameCount+1]
        errs = ["F_LMT_MISSING_REFERENCE_FRAME","F_LMT_MISSING_FIRST_FRAME","F_LMT_MISSING_LAST_FRAME","F_LMT_MISSING_BASIS_FRAME"]        
        
        #If ready to complete missing frames start process
        timingSet = sorted(list(timingSet))
        for curve in self.raw_fcurves:
            kf = self.completeRawKeyframes(curve,timingSet,adjust)
            if not kf: return False
            curve.keyframe_complete_points = kf
        self.timings = timingSet
        raw_tuple_keyframes = []       
            
        self.raw_tuple_keyframes = [(t,tuple(channels)) for t,channels in zip(timingSet,zip(*[c.keyframe_complete_points for c in sorted(self.raw_fcurves,key = lambda x: x.array_index)]))]
        return True
    
class InversionObject():
    #Validate Tether Inversibility
    def validateInversibility(self,tether,functionMap):
        pbone = None
        if not tether:
            self.pbone = pbone
            return True
        else:
            if self.boneFunction in functionMap:
                pbone = functionMap[self.boneFunction]
                if not (pbone.bone.matrix_local.determinant() != 0) or (pbone.parent and (pbone.parent.bone.matrix_local.determinant() == 0)):
                    try:
                        self.fcurveReportPattern("F_LMT_UNINVERSIBLE_MATRIX",self.errorOut(),"Missing Channels were Added",
                                                 self.errorOut(),"Transform was omitted from export process",
                                                 pbone.name,tether.name)
                    except FreeHKError:
                        return False
        self.pbone = pbone
        return True
    def vectorize(self,vec):
        return self.basicRead(vec)
    def keyframe_transform(self,tupleKf):
        if not self.pbone:
            return self.eulerCorrection(self.vectorize(tupleKf))
        else:            
            return self.eulerCorrection(self.dataWrite(strackerInverseTransform(self.pbone,self.dataRead(tupleKf))))
    def eulerCorrection(self,vec):
        if self.transform == "rotation_euler":
            return vec.to_quaternion()
        else:
            return vec
    def generateVectorKeyframes(self):            
        self.vector_keyframes = [(timing,self.keyframe_transform(raw_tuple)) 
                              for timing,raw_tuple in self.raw_tuple_keyframes]