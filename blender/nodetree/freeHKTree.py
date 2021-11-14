# -*- coding: utf-8 -*-
"""
Created on Sun Jun 20 19:54:00 2021

@author: AsteriskAmpersand
"""

import bpy
from bpy.props import BoolProperty
from bpy.types import NodeTree,Node

class FreeHKCustomTree(NodeTree):
    ''' Free Hyper Kinetics - Monster Hunter World Animation Editing Tree '''
    bl_idname = 'FreeHKNodeTree'
    bl_label = 'FreeHK Node Tree'
    bl_icon = 'RENDER_ANIMATION'
    

classes = [
    FreeHKCustomTree, 
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
