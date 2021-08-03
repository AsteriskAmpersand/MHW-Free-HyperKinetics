#Taken from: https://blender.stackexchange.com/questions/40711/how-to-convert-quaternions-keyframes-to-euler-ones-in-several-actions
#By Mutant Bob
import bpy
from mathutils import Quaternion
def get_or_create_fcurve(action, data_path, array_index=-1, group=None):
    for fc in action.fcurves:
        if fc.data_path == data_path and (array_index<0 or fc.array_index == array_index):
            return fc
    fc = action.fcurves.new(data_path, array_index)
    fc.group = group
    return fc

def add_keyframe_euler(action, euler, frame, bone_prefix, group):
    for i in range(len(euler)):
        fc = get_or_create_fcurve(action, bone_prefix+"rotation_euler", i, group)
        pos = len(fc.keyframe_points)
        fc.keyframe_points.add(1)
        fc.keyframe_points[pos].co = [frame, euler[i]]
        fc.update()


def frames_matching(action, data_path):
    frames = set()
    for fc in action.fcurves:
        if fc.data_path == data_path:
            fri = [kp.co[0] for kp in fc.keyframe_points]
            frames.update(fri)
    return frames

def fcurves_group(action, data_path):
    for fc in action.fcurves:
        if fc.data_path == data_path and fc.group is not None:
            return fc.group
    return None

def convert_quaternion_to_euler(action, order):
    bone_prefixes = set()
    for fc in action.fcurves:
        if fc.data_path == "rotation_quaternion" or fc.data_path[-20:]==".rotation_quaternion":
            bone_prefixes.add(fc.data_path[:-19])
            
    for bone_prefix in bone_prefixes:
        data_path = bone_prefix + "rotation_quaternion"
        frames = frames_matching(action, data_path)
        group = fcurves_group(action, data_path)
        for fr in frames:
            quat = Quaternion()
            for fc in action.fcurves:
                if fc.data_path == data_path:
                    quat[fc.array_index] = fc.evaluate(fr)
            euler = quat.to_euler(order)
            add_keyframe_euler(action, euler, fr, bone_prefix, group)
    for fc in action.fcurves:
        if fc.data_path == "rotation_quaternion" or fc.data_path[-20:]==".rotation_quaternion":
            action.fcurves.remove(fc)

def fixQuaternions():
    order='XYZ'
    for action in bpy.data.actions:
        convert_quaternion_to_euler(action, order)