# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 10:05:22 2024

@author: Asterisk
"""

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from ..struct.EFX_Pl import PL, PLEntry

class ExportPL(Operator, ExportHelper):
    bl_idname = "custom_import.export_mhw_pl"
    bl_label = "Save MHW PL file (.pl)"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Export PL from Scene"
 
    # ImportHelper mixin class uses this
    filename_ext = ".pl"
    filter_glob = StringProperty(default="*.pl", options={'HIDDEN'}, maxlen=255)

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
        
        plprxs = [{"viscon":obj["visibleCondition"], "location":obj.location} 
             for obj in bpy.context.scene.objects
                 if obj.type == "EMPTY" 
                 and "Type" in obj 
                 and obj["Type"] == "PL_Proxy"]
        pl = PL().construct({"entries":plprxs})
        with open(self.filepath,"wb") as outf:
            outf.write(pl.serialize())
        self.displayErrors(self.ErrorMessages)
        return {'FINISHED'}


def createPLProxy(viscon):
    pl = bpy.data.objects.new("PlProxy-%02d"%viscon, None )
    bpy.context.scene.objects.link( pl )
    pl["Type"] = "PL_Proxy"
    pl.empty_draw_size = .1
    pl.empty_draw_type = "SPHERE"
    pl.show_x_ray = True
    pl["Viscon"] = viscon
    return pl
    
def pl_export_menu(self, context):
    self.layout.operator(ExportPL.bl_idname, text="MHW PL (.pl)")
