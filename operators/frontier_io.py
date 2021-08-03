# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 01:31:17 2020

@author: AsteriskAmpersand
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 11:43:04 2019

@author: AsteriskAmpersand
"""
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, IntProperty, EnumProperty, FloatProperty, BoolProperty
from bpy.types import Operator

from pathlib import Path

from ..blender.exchangeFormat import ExchangeFormat
from ..blender.frontierFormat import FrontierFormat
from ..blender.clearQuaternions import fixQuaternions 

def skeletonCandidates(obj,context):
    return [ (ob.name, ob.name, ob.type, i)
            for i,ob in enumerate(bpy.context.scene.objects)
            if skeletonCondition(obj,ob)]
def skeletonCondition(obj,ob):
    return ob.type == "ARMATURE" or (ob.type == "EMPTY" and ob.parent is None)
    
class ExportFrontierAnimation(Operator, ExportHelper):
    bl_idname = "custom_export.export_mhf_anim"
    bl_label = "Save MHF Hari Animation Timeline File (.fhat)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
 
    filename_ext = ".fhat"
    filter_glob = StringProperty(default="*.fhat", options={'HIDDEN'}, maxlen=255)
    
    skeleton = EnumProperty(
            name = "Skeleton",
            description = "Selects the skeleton or empty root on which animation indexes will be generated",
            items = skeletonCandidates,
            )
    typingR = EnumProperty(
            name = "Rotation Type",
            description = "Select binary type",
            items = [
                ("0", "Short", "Short"),
                ("1", "Float", "Float"),
                ("2", "Extended Short", "Extended Short"),
                ],
            default = "0")
    typingT = EnumProperty(
            name = "Translation Type",
            description = "Select binary type",
            items = [
                ("0", "Short", "Short"),
                ("1", "Float", "Float"),
                ("2", "Extended Short", "Extended Short"),
                ],
            default = "0")
    typingS = EnumProperty(
            name = "Scale Type",
            description = "Select binary type",
            items = [
                ("0", "Short", "Short"),
                ("1", "Float", "Float"),
                ("2", "Extended Short", "Extended Short"),
                ],
            default = "0")
    startingBone = IntProperty(
            name = "Starting Bone Index",
            description = "Index on which the last animation left.",
            default = 0)
    ack = StringProperty(
            name = "Acknowledge",
            description = "Acknowledge 'Frontier is trash that should remain dead' to export"
        )
    fix = BoolProperty(
            name = "Rectify Quaternions",
            description = "Rectify Quaternion into Euler Rotations",
            default = True
        )
    body = BoolProperty(
            name = "Rectify Player Body Y Position",
            description = "Exports player Bone.002 at a 110 offset",
            default = True
        )
    name = BoolProperty(
            name = "Bone by Name",
            description = "Exports bones based on name instead of hierarchy",
            default = False
        )
    def execute(self,context):
        if self.ack != 'Frontier is trash that should remain dead':
            raise ValueError("You have not acknowledged that 'Frontier is trash that should remains dead'\nYou instead wrote '%s'"%self.ack)
        if self.fix:
            fixQuaternions()
        exf = ExchangeFormat()
        skeleton = bpy.data.objects[self.skeleton]
        if skeleton.type == "ARMATURE":
            exf.parseSkeleton(skeleton,use_name = self.name)
        elif skeleton.type == "EMPTY":
            exf.parseEmptySkeleton(skeleton,use_name = self.name)
        ffx = FrontierFormat(int(self.typingR),int(self.typingT),int(self.typingS),self.body)
        anim,offsets = ffx.serializeExchangeFormat(exf,ffx.getSkeletonSize(skeleton),self.startingBone)
        with open(self.filepath,"wb") as outf:
            outf.write(anim)
        with open(Path(self.filepath).with_suffix(".fhatso"),"wb") as outf:
            outf.write(offsets)
        return {"FINISHED"}
    
def menu_func_export_mhf(self, context):
    self.layout.operator(ExportFrontierAnimation.bl_idname, text="MHF HAT (.fhat)")
