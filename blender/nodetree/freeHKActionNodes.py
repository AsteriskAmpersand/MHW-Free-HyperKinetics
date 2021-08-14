# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 11:51:51 2021

@author: AsteriskAmpersand
"""

import bpy
import math
from bpy.types import Node
from .freeHKNodes import FreeHKNode,align
from ..timl_importer import interpolationMapping
from ..timl_controller import timl_typemap,timl_propmap
from ..lmt_exporter import LMTActionParser
from ...struct import TIML,Lmt


class KeyframeSynchronizationError(Exception):
    pass

def filter_TIML_actions(self,object):
    return object.bl_rna.name == "Action" and object.freehk.starType == "TIML_Action"

def filter_Non_TIML_actions(self,object): 
    return object.bl_rna.name == "Action" and not filter_TIML_actions(self,object)

class FreeHKAnimationNode(FreeHKNode):
    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        self.input_action = node.input_action

    # Free function to clean up on removal.
    def free(self):
        pass

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "input_action")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "input_action")

class BoneList(list):
    pass

class LMTActionNode(Node, FreeHKAnimationNode):
    '''LMT Animation Action Node'''
    bl_idname = 'LMTActionNode'
    bl_label = "LMT Action Node"
    bl_icon = 'ACTION'
    input_action = bpy.props.PointerProperty(name = "Action",
                                            type=bpy.types.Action,
                                    		poll=filter_Non_TIML_actions)
    def init(self, context):
        self.use_custom_color = True
        #self.inputs.new('CustomSocketType', "Hello")
        self.outputs.new('FreeHKAnimationSocket', "LMT Animation","LMT_Animation")
        
    def basicStructure(self):
        return self

    def extend(self,null):
        print("Node Input Action:",self.input_action)        
        bl = BoneList()
        bl.frameCount = 0
        bl.translation = [0,0,0,0]
        bl.rotation = [0,0,0,1]
        if not self.input_action:
            return bl
        if self.input_action.freehk.starType != "LMT_Action":
            self.error_handler.append("A_LMT_INVALID_ACTION_TYPE",self.input_action.name)
            if self.error_handler.actionError.fix:
                external,internal = LMTActionParser(self.input_action,self.error_handler,bpy.contetxt.scene.freehk_tether).export()
                self.error_handler.logSolution("Action was treated as an LMT Action and the tether set without updates to the scene's target tether (this might cause issues)")
            elif self.error_handler.actionError.omit:
                self.error_handler.logSolution("Action was omitted from export process")
                return bl
            else:
                return bl
        else:
            parsedAction = LMTActionParser(self.input_action,self.error_handler)            
            external,internal = parsedAction.export()
        if external is None:
            return bl
        bl.frameCount = external.frameCount
        bl.rotation = external.rotation
        bl.translation = external.translation
        #Parse LMT Action passing self.errors (error handler)
        bl.extend(internal)
        return bl
    
    def compile(self,exporter):
        if self.input_action:
            return (self.input_action,exporter)
        else:
            return None
        

class ExportTIMLTransformNode:
    def __init__(self,fcurve,datapath,rot,error_handler):
        self.__valid__ = True
        self.action = fcurve.id_data
        self.error_handler = error_handler
        self.error_handler.curveOwnership(self)
        self.offset = None
        self.count = None
        self.datatypeHash = int(datapath[1:],16)
        self.dataType = timl_typemap[datapath]
        self.dataClass = TIML.TIML_DataFrame(self.dataType)
        self.dataTransform = (lambda x: x) if self.dataType == 2 else (lambda x: int(x))
        if self.dataType == 3:
            #self.keyframes = [[],[],[],[]]
            self.keyframes = [fcurve]
        else:
            self.keyframes = fcurve.keyframe_points
        self.rot = rot
    def aggregate(self,fcurve):
        if self.dataType == 3:
            self.keyframes.append(fcurve)
        else:
            self.keyframes.extend(fcurve.keyframe_points)
    def parseColors(self,inputchannels,kfs):
        if self.error_handler.fcurveError.fix:
            self.synchronizeColors(inputchannels,kfs)
        else:
            if len(inputchannels) < 4:
                self.channelError()
                return
            try:
                self.blindParseColors(self,inputchannels,kfs)
            except KeyframeSynchronizationError:
                self.synchroError()
                self.__valid__ = False
            except ValueError:
                self.interpolationError()
                self.__valid__ = False
    def synchronizeColors(self,inputchannels,kfs):
        indices = set()
        for channel in inputchannels:
            indices = indices.union((int(kf.co[0]) for kf in channel.keyframe_points))
        #channels = [[],[],[],[]]
        #print(indices)
        keyframes = {i:TIML.TIML_Color().construct({"value":[255,255,255,255],
                                          "controlL":None,
                                          "controlR":None,
                                          "transition":None,
                                          "frameTiming":i,
                                          "dataType":self.dataType}) for i in indices}
        if len(inputchannels) < 4:
                self.channelError()
                self.error_handler.logSolution("Missing Channels were created and set to a fixed value of 1.0 (255)")
        for channel in inputchannels:
            visited = set()
            for keyframe in channel.keyframe_points:
                t = int(keyframe.co[0])
                kf = keyframes[t]
                kf.value[channel.array_index] = int(255*keyframe.co[1])
                if kf.controlL is None: kf.controlL = keyframe.back
                if kf.controlR is None: kf.controlR = keyframe.period
                try:
                    if kf.transition is None: kf.transition = interpolationMapping.index(keyframe.interpolation)
                except:
                    self.interpolationError(kf.interpolation)
                    self.error_handler.logSolution("Transition value was set to '%s' (1)"%interpolationMapping[1])
                    kf.transition = 1
                visited.add(t)
            missingIndices = indices.difference(visited)
            if missingIndices:
                self.synchroError()
                self.error_handler.logSolution("Interpolation Keyframes were added where necessary")
            for t in missingIndices:
                keyframes[t][channel.array_index] = int(255*channel.evaluate(t)         )       
            #channels[channel.array_index] = [channel.evaluate(i) for i in indices]
        kfs.extend(keyframes.values())
        
    def blindParseColors(self,inputchannels,kfs):
        for kr,kg,kb,ka in zip(*inputchannels):
                keyf = self.mergeColor(kr,kg,kb,ka)
                kfs.append(keyf)
    def __bool__(self):
        return self.__valid__
    def mergeColor(self,r,g,b,a):
        rv,gv,bv,av = map(lambda x: int(x.co[1]*255),[r,g,b,a])
        rt,gt,bt,at = map(lambda x: int(x.co[0]),[r,g,b,a])
        if rt != gt or gt != bt or bt != at:
            raise KeyframeSynchronizationError("Disjointed Color Keyframes found on TIML Animation")
        color = [int(rv),int(gv),int(bv),int(av)]
        kf = TIML.TIML_Color().construct({"value":color,
                                          "controlL":r.back,
                                          "controlR":r.period,
                                          "transition":interpolationMapping.index(r.interpolation),
                                          "frameTiming":rt,
                                          "dataType":self.dataType})
        return kf
    
    def fixIllegalControl(self,errType):
        getattr(self,errType)()
        
    def checkControlTypes(self,kf):
        #0 - 0,0
        #1 - UINT, 0/1120403000
        #2 - Float/Float
        #3 - Float/Float
        #4 - 0,0
        ctrlR = self.dataTransform(kf.period)
        ctrlL = self.dataTransform(kf.back)
        err = False
        if self.dataType in [0,4]:
            if ctrlL != 0 or ctrlR != 0:
                if self.dataType == 0: 
                    self.invalidSINTControl()
                else:
                    self.invalidBoolControl()
                ctrlL = 0
                ctrlR = 0
                err = True
        if self.dataType == 1:
            if ctrlL < 0 or ctrlR < 0:
                self.invalidUINTControl()                
                ctrlL = max(0,ctrlL)
                ctrlR = max(0,ctrlR)
                err = True
        if err:
            if not self.error_handler.fcurveError.fix:
                self.__valid__ = False
            else:
                self.error_handler.logSolution("Illegal Control Values were set to 0")
        return ctrlL,ctrlR
    def checkInterpolate(self,kf):
        try:
            interpolate = interpolationMapping.index(kf.interpolation)
        except ValueError:
            interpolate = 1
            self.interpolationError(kf.interpolation)
            if not self.error_handler.fcurveError.fix:
                self.__valid__ = False
            else:
                self.error_handler.logSolution("Transition value was set to '%s' (1)"%interpolationMapping[1])
        return interpolate
    def clean(self):
        kfs = []
        rotTrans = (lambda x: math.degrees(x)) if self.rot else (lambda x: x)
        if self.dataType == 3:
            self.parseColors(list(sorted(self.keyframes,key = lambda x: x.array_index)),kfs)
        else:
            for kf in sorted(self.keyframes,key = lambda x:x.co[0]):
                interpolate = self.checkInterpolate(kf)
                ctrlL,ctrlR = self.checkControlTypes(kf)
                keyf = self.dataClass().construct({"value":(self.dataTransform(rotTrans(kf.co[1]))),
                                            "controlL":ctrlL,
                                            "controlR":ctrlR,
                                            "frameTiming":kf.co[0],
                                            "transition":interpolate,
                                            "dataType":self.dataType})
                kfs.append(keyf)
        self.keyframes = kfs
        self.count = len(self.keyframes)
    def invalidSINTControl(self):
        self.error_handler.append(("K_TIML_INVALID_CONTROL_VALUE_SINT",timl_propmap[self.datapath],self.action.name))
    def invalidBOOLControl(self):
        self.error_handler.append(("K_TIML_INVALID_CONTROL_VALUE_BOOL",timl_propmap[self.datapath],self.action.name))
    def invalidUINTControl(self):
        self.error_handler.append(("K_TIML_INVALID_CONTROL_VALUE_UINT",timl_propmap[self.datapath],self.action.name))
    def interpolationError(self,entryValue):
        self.error_handler.append(("K_TIML_INVALID_INTERPOLATION",timl_propmap[self.datapath],self.action.name,entryValue))
    def channelError(self):
        self.error_handler.append(("F_TIML_MISSING_CHANNEL",timl_propmap[self.datapath],self.action.name))
    def synchroError(self):
        self.error_handler.append(("F_TIML_UNSYNCHRONIZED_KEYFRAMES",timl_propmap[self.datapath],self.action.name))
    def structure(self):
        struct = {"offset":self.offset,
                    "count":self.count,
                    "datatypeHash":self.datatypeHash,
                    "dataType":self.dataType}
        head = TIML.TIML_Transform().construct(struct)#.serialize()
        head.keyframes = self.keyframes
        return head

class ExportTIMLTypesNode:
    def __init__(self,action,error_handler):
        self.error_handler = error_handler
        self.error_handler.actionOwnership(self)
        if action is None:
            self.offset = 0
            self.count = 0
            self.timelineParameterHash = 0
            self.transforms = []
        else:
            transforms = self.packFCurves(action)            
            self.offset = None
            self.count = len(transforms)
            self.timelineParameterHash = int(action.freehk.timelineParam[1:],16)
            self.transforms = transforms
            self.unkn0 = action.freehk.unkn0
    def compileRemap(self,action):
        remapper = {}
        for t,b in zip(["trans","rot","scl"],["location","rotation_euler","scale"]):
            for ix,ax in enumerate(["x","y","z"]):
                remapper[(b,ix)] = getattr(action.freehk,t+ax)
        return remapper
    def packFCurves(self,action):
        remap = self.compileRemap(action)
        mapper = {}
        for fcurve in action.fcurves:
            dp,ix = fcurve.data_path,fcurve.array_index
            dp = remap[(dp,ix)] if (dp,ix) in remap else dp.split(".")[-1]
            if dp not in mapper:
                #try:
                mapper[dp] = ExportTIMLTransformNode(fcurve,dp,"rotation_euler" in fcurve.data_path,self.error_handler)#.structure()
                #except:
                #    pass
            else:
                mapper[dp].aggregate(fcurve)
        for value in mapper.values():
            value.clean()
        return mapper.values()#[mapper[key] for key in sorted(mapper)]
    def structure(self):
        struct = {"offset":self.offset,"count":self.count,"timelineParameterHash":self.timelineParameterHash,"unkn0":self.unkn0}
        typing = TIML.TIML_Type().construct(struct)#.serialize()
        typing.transforms = [t.structure() for t in self.transforms]
        typing.transforms = list(filter(lambda x: x,typing.transforms))
        typing.count = len(typing.transforms)
        return typing
        
            
class TIMLActionNode(Node, FreeHKAnimationNode):
    '''TIML Animation Action Node'''
    bl_idname = 'TIMLActionNode'
    bl_label = "TIML Action Node"
    bl_icon = 'ACTION'

    input_action = bpy.props.PointerProperty(name = "Action",
                                            type=bpy.types.Action,
                                    		poll=filter_TIML_actions)
    def init(self, context):
        #self.inputs.new('CustomSocketType', "Hello")
        self.outputs.new('FreeHKTimlSocket', "TIML Animation","TIML_Animation")
        
    def basicStructure(self):        
        return self
    
    def extend(self,substructure):
        if not self.input_action:
            return None
        else:
            if self.input_action.freehk.starType != "TIML_Action":
                self.error_handler.append("A_TIML_INVALID_ACTION_TYPE",self.input_action.name)
                if self.error_handler.actionError.fix or self.error_handler.actionError.omit:
                    self.error_handler.logSolution("Action was omitted from export process")
                return None                
            return ExportTIMLTypesNode(self.input_action,self.error_handler).structure()
        
        #Parse using self.errors to log errors
        #ExportTIMLTypesNode(self.input_action)

classes = [
    LMTActionNode, TIMLActionNode
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)