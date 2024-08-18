# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 14:09:29 2019

@author: AsteriskAmpersand
"""
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from ..struct.EFX_Pl import PlFile

class ImportPL(Operator, ImportHelper):
    bl_idname = "custom_import.import_mhw_pl"
    bl_label = "Load MHW PL file (.pl)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Import PL into Scene"
 
    # ImportHelper mixin class uses this
    filename_ext = ".pl"
    filter_glob = StringProperty(default="*.pl", options={'HIDDEN'}, maxlen=255)

            
    def cleanup(self,obj):
        for children in obj.children:
            self.cleanup(children)
        objs = bpy.data.objects
        objs.remove(objs[obj.name], do_unlink=True)

    @staticmethod
    def showMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    
        def draw(self, context):
            self.layout.label(message)
    
        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

    def displayErrors(self, errors):
        if errors:
            for _ in range(20):print()
            print("PL Import Errors:")
            print("#"*75)
            print(errors)
            print("#"*75)
            message="Warnings have been Raised, check them in Window > Toggle_System_Console"
            self.showMessageBox(message, title = "Warnings and Error Log")
    
    def execute(self,context):
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            pass
        self.ErrorMessages = []
        bpy.ops.object.select_all(action='DESELECT')
        try: pl = PlFile(self.properties.filepath)
        except:
            self.ErrorMessages.append("Corrupted PL File couldn't be read.")
            self.missingFunctionBehaviour = "Abort"
            self.displayErrors(self.ErrorMessages)
            return {'FINISHED'}
        for ix, entry in enumerate(pl.data.entries):
            plprx = createPLProxy(entry.viscon)
            plprx.location = entry.location
            for mesh in bpy.context.scene.objects:
                if mesh.type == "MESH" and mesh.data and "visibleCondition" in mesh.data and\
                    mesh.data["visibleCondition"] == entry.viscon:
                        c = mesh.constraints.new(type = "COPY_LOCATION")
                        c.target = plprx
        self.displayErrors(self.ErrorMessages)
        return {'FINISHED'}


def createPLProxy(viscon):
    pl = bpy.data.objects.new("PlProxy-%02d"%viscon, None )
    bpy.context.scene.objects.link( pl )
    pl["Type"] = "PL_Proxy"
    pl.empty_draw_size = 2.5
    pl.empty_draw_type = "SPHERE"
    pl.show_x_ray = True
    pl["visibleCondition"] = viscon
    return pl
    
def pl_import_menu(self, context):
    self.layout.operator(ImportPL.bl_idname, text="MHW PL (.pl)")
