# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 05:24:15 2020

@author: AsteriskAmpersand
"""


from ..common.Cstruct import PyCStruct

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import IntProperty, BoolProperty, StringProperty
from bpy.types import Operator

from collections import OrderedDict
import math

FreedomUniteTransforms = {()}


class PointerBlockHeader(PyCStruct):
    fields = OrderedDict([
                        ("count", "uint"),
                        ("offset", "uint"),
    ])

    def __bool__(self):
        return bool(self.count)


def AnimPointerBlock(count):
    class _AnimPointerBlock(PyCStruct):
        fields = OrderedDict([
                            ("animPointers", "uint[%d]" % count),
        ])

        def __iter__(self):
            return iter(self.animPointers)
    return _AnimPointerBlock()


class AnimHeader(PyCStruct):
    fields = OrderedDict([
                        ("mainType", "ushort"),
                        ("blockType", "ushort"),
                        ("boneCount", "uint"),
                        ("blockSize", "uint"),
                        ("animMetadataType", "uint"),
                        ("animMetadata", "float"),
    ])


class BoneHeader(PyCStruct):
    fields = OrderedDict([
                        ("transformType", "ushort"),
                        ("mainType", "ushort"),
                        ("transformCount", "uint"),
                        ("blockSize", "uint"),
    ])


class Transform(PyCStruct):
    fields = OrderedDict([
                        ("keyframeType", "ushort"),
                        ("blockType", "ushort"),
                        ("keyframeCount", "uint"),
                        ("blockSize", "uint"),
    ])


class AnimDataUnkn(PyCStruct):
    fields = OrderedDict([("unknown", "uint[2]")])


baseFields = ["keyvalue", "frameIndex", "lInterpol", "rInterpol"]


class KeyframeShort(PyCStruct):
    fields = OrderedDict([(field, "short") for field in baseFields])


class KeyframeShortExtended(PyCStruct):
    fields = OrderedDict([(field, "short") for field in baseFields] +
                         [("unkn5", "short"), ("unkn6", "short")])

    def construct(self, data):
        if "unkn5" not in data:
            data["unkn5"] = 0
        if "unkn6" not in data:
            data["unkn6"] = 0
        return super().construct(data)


class KeyframeFloat(PyCStruct):
    fields = OrderedDict([(field, "float") for field in baseFields])


def transformFromMask(transformDataType):
    transformList = [(i, j) for i in range(3) for j in range(3)]
    transformMasks = [1 << i for i in range(0, 9)]
    for typing, mask in zip(transformList, transformMasks):
        if mask == transformDataType:
            return typing
    raise KeyError(transformDataType)


def transformTypes(animDataType):
    # Scale Rot Trans, X Y Z
    result = []
    transformList = [(i, j) for i in range(3) for j in range(3)]
    transformMasks = [2 << i for i in range(2, 2+9)]
    for typing, mask in zip(transformList, transformMasks):
        if mask & animDataType:
            result.append(typing)
    return result


kIndexMap = {0x8012: 0, 0x8022: 1, 0x8013: 2}


def keyframeType(typeEnum):
    kindex = kIndexMap[typeEnum]
    return [KeyframeShort, KeyframeFloat, KeyframeShortExtended][kindex]()


def transformFrameValue(ttype, ktype):
    ktindex = kIndexMap[ktype]
    return [
        [lambda x: x/15, lambda x: x, lambda x: x/15],  # Scale
        [lambda x: x/(4096*2/math.pi), lambda x: x*math.pi,
         lambda x: x/(4096*2/math.pi)],  # Rot
        [lambda x: x/15, lambda x: x,
         lambda x: x/15],  # Trans
    ][ttype][ktindex]


class PackagedTransform(list):
    pass


def BoneIterator(skeleton, splitPoint):
    if splitPoint == -1:
        return SingleIterator(skeleton)
    else:
        return DoubleIterator(skeleton, splitPoint)


class SkeletonIterator():
    def __init__(self, skeleton, start, end):
        self.curr = start
        self.start = start
        self.end = end
        self.skeleton = skeleton

    def next(self):
        bone = self.skeleton[self.curr]
        self.curr += 1
        if self.curr >= self.end:
            self.curr = 0
        return bone
    
    def reset(self):
        self.curr = self.start


class SingleIterator():
    def __init__(self, skeleton):
        self.iterator = SkeletonIterator(skeleton, 0, len(skeleton))

    def next(self):
        return self.iterator


class DoubleIterator():
    def __init__(self, skeleton, splitPoint):
        self.current = 0
        self.iterators = [SkeletonIterator(skeleton, 0, splitPoint), SkeletonIterator(
            skeleton, splitPoint, len(skeleton))]

    def next(self):
        iterator = self.iterators[self.current % 2]
        self.current += 1
        return iterator


class BBoneTransform():
    def __repr__(self):
        return "<class BBoneTransform: %s>: %s" % (self.boneName, self.transforms)

    def __getitem__(self, key):
        return self.transforms[key]

    def __str__(self):
        return self.boneName


class FreedomUniteAnim():
    def __init__(self, skeleton, splitPoint):
        self.boneIterator = BoneIterator(skeleton, splitPoint)

    def marshall(self, stream):
        prev = True
        self.headers = []
        while prev:
            prev = PointerBlockHeader().marshall(stream)
            if prev:
                self.headers.append(prev)
        for ix, header in enumerate(self.headers):
            boneIter = self.boneIterator.next()
            header.id = ix
            stream.seek(header.offset)
            pointers = AnimPointerBlock(header.count).marshall(stream)
            header.animations = {}
            for jx, ptr in enumerate(pointers):
                if ptr != 4294967295:
                    stream.seek(ptr)
                    # print(ix,jx)
                    header.animations[jx] = self.marshallAnimData(
                        stream, boneIter)
                boneIter.reset()
        return self

    def marshallAnimData(self, stream, bix):
        animData = AnimHeader().marshall(stream)
        bones = []
        for boneIx in range(animData.boneCount):
            #transformType = transformTypeList[transformIx]
            boneHeader = BoneHeader().marshall(stream)
            transformTypeList = transformTypes(boneHeader.transformType)
            bt = BBoneTransform()
            bt.boneName = bix.next()
            bt.transforms = []
            for transformJx in range(boneHeader.transformCount):
                transform = Transform().marshall(stream)
                transform.type = transformFromMask(transform.keyframeType)
                if transform.keyframeCount:
                    #print("    ",boneIx,transformJx)
                    transformType = transformFromMask(transform.keyframeType)
                    kfs = PackagedTransform()
                    correction = transformFrameValue(
                        transformType[0], transform.blockType)

                    for frame in range(transform.keyframeCount):
                        kf = keyframeType(transform.blockType).marshall(stream)
                        kf.keyvalue = correction(kf.keyvalue)
                        kfs.append(kf)

                    kfs.transformType = transformType
                    transform.keyframes = kfs
                    bt.transforms.append(transform)
            if bt.transforms:
                bones.append(bt)
        return bones


def rotationAndName(bone):
    bone.rotation_mode = "XYZ"
    return bone.name 

def getSkeleton(context,startPoint = 2,functionCall = rotationAndName):
    for obj in context.scene.objects:
        if obj.type == "ARMATURE":
            return [functionCall(bone) for bone in obj.pose.bones][startPoint:]

class CycleBoneNames(Operator):
    bl_idname = "custom_import.cycle_bone_names"
    bl_label = "Cycle Bone Names for Testing"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    startPoint = IntProperty(name = "Skip Initial", default = 2)
    def execute(self,context):
        getName = lambda x: x.name
        for obj in context.scene.objects:
            if obj.type == "ARMATURE":
                action = obj.animation_data.action if obj.animation_data else None
                if obj.animation_data: obj.animation_data.action = None
                boneNames = getSkeleton(context,startPoint=self.startPoint,
                                       functionCall = getName)
                for bone in obj.pose.bones[self.startPoint:]:
                    bone.name = "Dummy"
                for name,bone in zip(boneNames[1:]+[boneNames[0]],
                                     list(obj.pose.bones)[self.startPoint:]):
                    bone.name = name    
                if action:
                    obj.animation_data.action = action
        try:
            bpy.ops.pose.transforms_clear()
        except:
            pass
        return {'FINISHED'}

class ImportFUAnim(Operator, ImportHelper):
    bl_idname = "custom_import.import_mhfu_fuanim"
    bl_label = "Load MHFU Animation file (.fua)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}

    # ImportHelper mixin class uses this
    filename_ext = ".fua"
    filter_glob = StringProperty(
        default="*.fua", options={'HIDDEN'}, maxlen=255)
    split = BoolProperty(name="Split Skeleton", default=False)
    splitPoint = IntProperty(name="Split Point", default=-1)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "split")
        if self.split:
            col.prop(self, "splitPoint")

    def execute(self, context):
        skeleton = getSkeleton(context)
        if not skeleton:
            self.report(
                {"WARNING"}, "Could not find a valid skeleton to animate")
            return {'CANCELED'}
        with open(self.properties.filepath, "rb") as inf:
            fuanim = FreedomUniteAnim(
                skeleton, self.splitPoint if self.split else -1)
            fuanim.marshall(inf)
        self.loadAnimations(context, fuanim)
        return {'FINISHED'}

    def createAction(self, ix, jx):
        name = "FUAnim-%02d/%03d" % (ix, jx)
        action = bpy.data.actions.new(name)
        action["id"] = [ix, jx]
        return action

    def createDataPath(self, boneName, typing):
        typeName = ["scale", "rotation_euler", "location"][typing]
        return 'pose.bones["%s"].%s' % (boneName, typeName)

    def createChannel(self, action, boneName, transform):
        dataPath = self.createDataPath(boneName, transform.type[0])
        keyframeCount = len(transform.keyframes)
        f = action.fcurves.new(data_path=dataPath, index=transform.type[1])
        f.keyframe_points.add(keyframeCount)
        for bkeyframe, fkeyframe in zip(f.keyframe_points, transform.keyframes):
            bkeyframe.co = fkeyframe.frameIndex, fkeyframe.keyvalue
        f.update()
        return

    def loadAnimations(self, context, fuanim):
        for ix, header in enumerate(fuanim.headers):
            for jx, bones in header.animations.items():
                action = self.createAction(ix, jx)
                for bone in bones:
                    for transform in bone.transforms:
                        self.createChannel(action, bone.boneName, transform)


classes = [
    ImportFUAnim, CycleBoneNames,#ExportFreedomUniteAnimation
]


def menu_func_import_mhfu(self, context):
    self.layout.operator(ImportFUAnim.bl_idname, text="MHFU Animation (.fua)")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    addon_key = __package__.split('.')[0]
    addon = bpy.context.user_preferences.addons[addon_key]
    wrong = addon.preferences.enable_wrong
    if wrong:
        bpy.types.INFO_MT_file_import.append(menu_func_import_mhfu)
    #    bpy.types.INFO_MT_file_import.append(menu_func_export_mhfu)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    if menu_func_import_mhfu in bpy.types.INFO_MT_file_export:
        bpy.types.INFO_MT_file_export.remove(menu_func_import_mhfu)
    #if menu_func_export_mhfu in bpy.types.INFO_MT_file_export:
    #    bpy.types.INFO_MT_file_export.remove(menu_func_export_mhfu)


"""
if __name__ in "__main__":
    bones = ["Bone%03d"%b for b in range(60)]
    anim = FreedomUniteAnim(bones,-1)
    with open(r"D:\Downloads\Shagaru\0003_00DCA2D3.bin","rb") as inf:
        anim.marshall(inf)
"""

# 08 00 00 02 - Animation Header
# > 08 00 XX XX - Bone Animation:
#                                   OR of all Transform Bitflags
# >     > 08 00 YY YY - Transform Listing
#                                   00 08/00 10/00 20 Rotation
#                                   00 40/00 80/01 00 Translation
#                                   02 00/04 00/08 00 Scaling
"""
typedef struct{
    uint unknown[2];
}AnimDataUnkn;

typedef struct {
    uint blockType; 
    uint blockCount; 
    uint blockSize; 
} BlockHeader;

typedef struct{
    short keyvalue;// x/4096*4/Pi rad => 4096*Pi/4
    short frameIndex;
    short easingInterpol;//Does easing but mechanism is insane and not meant for humans
    short interpolEasing;//Does easing but mechanism is insane and not meant for humans
}MiniDataBlock1;

typedef struct{
    float keyvalue;// Half turns: keyvalue * 3.14159265358979323
    float frameIndex;
    float easingInterpol;
    float interpolEasing;
}MiniDataBlock2;

typedef struct{
    short keyvalue;// x/4096*4/Pi rad => 4096*Pi/4
    short frameIndex;
    short easingInterpol;//Does easing but mechanism is insane and not meant for humans
    short interpolEasing;//Does easing but mechanism is insane and not meant for humans
    short unkn5;
    short unkn6;
}MiniDataBlock3;
"""