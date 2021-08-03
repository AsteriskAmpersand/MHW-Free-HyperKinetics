# -*- coding: utf-8 -*-
"""
Created on Sun Jun 20 22:26:49 2021

@author: AsteriskAmpersand
"""

import bpy
from bpy.types import NodeTree, Node, NodeSocket

class FreeHKSocket:
    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)
    # Socket color
    def draw_color(self, context, node):
        return (*(col/255 for col in self.rgb),1)

class AnimationSocket(NodeSocket,FreeHKSocket):    
    '''MHW Animation Socket'''
    bl_idname = 'FreeHKAnimationSocket'
    bl_label = "FreeHK Animation Socket"
    rgb = (13,79,145)
    
class EFXEntrySocket(NodeSocket,FreeHKSocket):
    '''MHW Special Effect Socket'''
    bl_idname = 'FreeHKEFXEntrySocket'
    bl_label = "FreeHK EFX Socket"
    rgb = (54,141,24)
    
class TIMLSocket(NodeSocket,FreeHKSocket):
    '''MHW Timeline Socket'''
    bl_idname = 'FreeHKTimlSocket'
    bl_label = "FreeHK Timeline Socket"
    rgb = (125,79,202)
    

class LMTEntrySocket(NodeSocket,FreeHKSocket):    
    '''MHW Animation Socket'''
    bl_idname = 'FreeHKAnimationEntrySocket'
    bl_label = "FreeHK Animation Socket"
    rgb = (48,162,254)
    
class TIMLDataSocket(NodeSocket,FreeHKSocket):
    '''MHW Timeline Socket'''
    bl_idname = 'FreeHKTimlDataSocket'
    bl_label = "FreeHK Timeline Socket"
    rgb = (204,131,222)

class TIMLEntrySocket(NodeSocket,FreeHKSocket):
    '''MHW Timeline Socket'''
    bl_idname = 'FreeHKTimlEntrySocket'
    bl_label = "FreeHK Timeline Socket"
    rgb = (255,183,222)    

class GenericSocket(NodeSocket,FreeHKSocket):
    '''MHW Generic Socket'''
    bl_idname = 'FreeHKGenericSocket'
    bl_label = "FreeHK Generic Socket"
    rgb = (202,198,215)    

classes = [
    AnimationSocket, TIMLSocket, TIMLDataSocket, LMTEntrySocket,  TIMLEntrySocket, EFXEntrySocket, GenericSocket
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
