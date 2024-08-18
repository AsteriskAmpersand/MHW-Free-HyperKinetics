# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 09:11:25 2024

@author: Asterisk
"""
import bpy
from ..blender.pl_importer import ImportPL, pl_import_menu, createPLProxy
from ..blender.pl_exporter import ExportPL, pl_export_menu
from bpy.props import StringProperty, IntProperty, FloatProperty, EnumProperty
from collections import UserDict

#Disable PL
#Enable PL
#Update PL

class posDict(UserDict):
    def __init__(self, *args, epsilon = 0.01, **kwargs):
        super().__init__(*args,**kwargs)
        self.epsilon = epsilon
    def __setitem__(self, k, v):
        x,y,z = k
        nk = int(x),int(y),int(z)
        if nk not in self.data:
            self.data[nk] = [(k,1,v)]
        else:
            update = None
            for ix,(vec,cnt,val) in enumerate(self.data[nk]):
                if (vec-k).magnitude <= self.epsilon:
                    #update = (ix,(vec*cnt + k)/(cnt+1),cnt+1,v)
                    update = (ix,vec,cnt,v)
                    continue
            if update:
                ix,vec,cnt,val = update
                self.data[nk][ix] = (vec,cnt,val)
            else:
                self.data[nk].append((k,1,v))
        
    def __contains__(self,k):
        x,y,z = k
        nk = int(x),int(y),int(z)
        if nk not in self.data:
            return False
        for ix,(vec,cnt,val) in enumerate(self.data[nk]):
            if (vec-k).magnitude <= self.epsilon:
                return True
        return False
                
    def __getitem__(self,k):
        x,y,z = k
        nk = int(x),int(y),int(z)
        for ix,(vec,cnt,v) in enumerate(self.data[nk]):
            if (vec-k).magnitude <= self.epsilon:
                return v
        raise KeyError(k)
        

def isMHWMesh(obj):
    return obj.type == "MESH" and \
        obj.data and "visibleCondition" in obj.data
        
def isPlProxy(obj):
    return obj.type == "EMPTY" and \
        "Type" in obj and obj["Type"] == "PL_Proxy"


def connectMesh(mesh,proxy):
    c = mesh.constraints.new(type = "COPY_LOCATION")
    c.target = proxy

def disconnectMesh(mesh,pset):
    delete = []
    for constraint in mesh.constraints:
        if constraint.type == "COPY_LOCATION" and \
            (constraint.target in pset or constraint.target is None):
            delete.append(constraint)
    for c in delete:
        mesh.constraints.remove(c)

def trinumerate(context):
    proxies = {}
    proxy_set = []
    meshes = []
    for obj in context.scene.objects:
        if isPlProxy(obj):
            proxies[obj["visibleCondition"]] = obj
            proxy_set.append(obj)
        if isMHWMesh(obj):
            meshes.append(obj)
    return proxies,proxy_set,meshes

class updatePL(bpy.types.Operator):
    bl_idname = 'pl_tools.update_pl'
    bl_label = 'Update Mesh to PL'
    bl_description = 'Updates mesh constraints to their relevant PL Proxy'
    bl_options = {"REGISTER", "UNDO"}
    def execute(self,context):
        proxies,proxy_set,meshes = trinumerate(context)
        for mesh in meshes:
            disconnectMesh(mesh,proxy_set)
            if mesh.data["visibleCondition"] in proxies:
                connectMesh(mesh,proxies[mesh.data["visibleCondition"]])
        return {"FINISHED"}

class createPL(bpy.types.Operator):
    bl_idname = 'pl_tools.create_pl'
    bl_label = 'Creates a PL Proxy'
    bl_description = 'Creates a PL Proxy Node'
    bl_options = {"REGISTER", "UNDO"}
    viscon = IntProperty(name = "Visible Condition", default = 0)
    
    def execute(self,context):
        if bpy.context.active_object:
            l = bpy.context.active_object.location
        else:
            l = (0,0,0)
        pl = createPLProxy(self.viscon)
        pl.name = "User PLProxy-%02d"%self.viscon
        pl.location = l
        return {"FINISHED"}

class selectionPL(bpy.types.Operator):
    bl_idname = 'pl_tools.selection_pl'
    bl_label = 'Convert Selection to PL Proxy'
    bl_description = 'Converts selection with individual transforms to PL Proxies with No Transform'
    bl_options = {"REGISTER", "UNDO"}
    epsilon = FloatProperty(name = "Merge Distance", default = 0.01)
    viscon = IntProperty(name = "Default Visible Condition", default = -1)
    
    def execute(self,context):
        sel_objs = [objs for objs in bpy.context.selected_objects]
        posCache = posDict(epsilon = self.epsilon)
        for obj in sel_objs:
            tl = obj.matrix_world.to_translation()
            if tl.magnitude <= self.epsilon:
                continue
            if tl not in posCache:
                if isMHWMesh(obj):
                    viscon = obj.data["visibleCondition"]
                else:
                    viscon = self.viscon
                pl = createPLProxy(viscon)
                pl.name = "User PLProxy-%02d"%viscon
                pl.location = tl
                posCache[tl] = pl
            else:
                pl = posCache[tl]
            obj.location = (0,0,0)
            context.scene.update()
            connectMesh(obj,pl)
        return {"FINISHED"}
    
class enablePL(bpy.types.Operator):
    bl_idname = 'pl_tools.enable_pl'
    bl_label = 'Constraint Meshes to PL'
    bl_description = 'Constraints meshes to their relevant PL Proxy'
    bl_options = {"REGISTER", "UNDO"}
    def execute(self,context):
        proxies,proxy_set,meshes = trinumerate(context)
        for mesh in meshes:
            disconnectMesh(mesh,proxy_set)
            if mesh.data["visibleCondition"] in proxies:
                connectMesh(mesh,proxies[mesh.data["visibleCondition"]])
        return {"FINISHED"}
    

class disablePL(bpy.types.Operator):
    bl_idname = 'pl_tools.disable_pl'
    bl_label = 'Free Mesh from  PL'
    bl_description = 'Unconstraints meshes from their relevant PL Proxy'
    bl_options = {"REGISTER", "UNDO"}
    def execute(self,context):
        proxies,proxy_set,meshes = trinumerate(context)
        for mesh in meshes:
            disconnectMesh(mesh,proxy_set)
        return {"FINISHED"}
    
    
class PLTools(bpy.types.Panel):
    bl_category = "MHW Tools"
    bl_idname = "panel.mhw_pl"
    bl_label = "PL Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    # bl_category = "Tools"

    def draw(self, context):
        self.layout.label("EFX PL Tools")
        col = self.layout.column(align = True)
        col.operator("pl_tools.create_pl", icon='MESH_CUBE', text="Create PL Proxy")
        col.operator("pl_tools.selection_pl", icon='MOD_ARRAY', text="Selection to PL Proxies")
        col.operator("pl_tools.update_pl", icon='PLAY', text="Update PL Links")
        col = self.layout.column(align = True)
        row = col.row(align = True)
        row.operator('pl_tools.disable_pl', icon='VISIBLE_IPO_OFF',text = 'Free')
        row.operator('pl_tools.enable_pl', icon='VISIBLE_IPO_ON',text = 'Link')


classes = [ImportPL, ExportPL, createPL, selectionPL, updatePL, enablePL, disablePL, PLTools]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.INFO_MT_file_import.append(pl_import_menu)
    bpy.types.INFO_MT_file_export.append(pl_export_menu)
            
    
def unregister():
    bpy.types.INFO_MT_file_import.remove(pl_import_menu)
    bpy.types.INFO_MT_file_export.remove(pl_export_menu)
    for cls in classes:
        bpy.utils.unregister_class(cls)
