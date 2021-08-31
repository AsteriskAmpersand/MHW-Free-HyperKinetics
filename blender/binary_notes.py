# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 23:02:44 2021

@author: Asterisk
"""

import bpy
import re

def binFormat(binstr):
    return ' '.join(re.findall("."*8,binstr)) 

def intToBin(intVal):
    intVal = intVal & 0xFFFFFFFF
    #if intVal < 0:
    #    intVal = intVal + 2**32
    binstr = binFormat(bin(intVal)[2:].rjust(32,"0"))[:]
    return binstr[max(0,len(binstr)-(32+3)):]

def binToInt(binVal):
    intval = int(binVal.replace(' ',''),2)
    return (intval & 0xFFFFFFFF) - 2**32 if intval > 0x7FFFFFFF else intval & 0xFFFFFFFF

# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

class NOTES_OT_actions(bpy.types.Operator):
    """Move items up and down, add and remove"""
    bl_idname = "freehk_notes.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.freehk_notes_index

        try:
            item = scn.freehk_notes[idx]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and idx < len(scn.freehk_notes) - 1:
                scn.freehk_notes.move(idx, idx+1)
                scn.freehk_notes_index += 1

            elif self.action == 'UP' and idx >= 1:
                scn.freehk_notes.move(idx, idx-1)
                scn.freehk_notes_index -= 1

            elif self.action == 'REMOVE':
                item = scn.freehk_notes[scn.freehk_notes_index]                    
                scn.freehk_notes.remove(idx)
                scn.freehk_notes_index = max(min(scn.freehk_notes_index,len(scn.freehk_notes)-1),0)

        if self.action == 'ADD':
            item = scn.freehk_notes.add()
            #TODO - Result Code from Binary Ops
            for prop in ["int_input",'operation','binary_target','name']:
                setattr(item,prop,getattr(scn.freehk_binary,prop))
            scn.freehk_notes_index = (len(scn.freehk_notes)-1)
        return {"FINISHED"}

class NOTES_OT_clearList(bpy.types.Operator):
    """Clear all items of the list and remove from scene"""
    bl_idname = "freehk_notes.clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items of the list and remove from scene"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.freehk_notes)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if bool(context.scene.freehk_notes):
            # Clear the list
            context.scene.freehk_notes.clear()
        else:
            self.report({'INFO'}, "Nothing to remove")
        return{'FINISHED'}


# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

opMap = {"+": "&","x":"|","xor":"^"}

class NOTES_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT'}:     
            r = layout.row(align = True)
            r.label("%08X %s %08X = "%(item.int_input&0xFFFFFFFF,opMap[item.operation],binToInt(item.binary_target)))
            r.prop(item,'int_result',text="")
            #col = layout.column(align=True)
            #col.prop(item,"int_input")  
            #col.prop(item,"binary_input")  
            #col.prop(item,"operation")
            #col.prop(item,"binary_target")
            #col = layout.column(align=True)
            #col.prop(item,"binary_result")
            #col.prop(item,"int_result")
        elif self.layout_type in {'GRID','COMPACT'}:
            #layout.alignment = 'CENTER'
            layout.prop(item,"int_result",text="")

    def invoke(self, context, event):
        pass



class NOTES_PT_objectList():

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        
        if not scn.freehk_notes_compact:
            row = layout.row()
            row.template_list("NOTES_UL_items", "freehk_notes_def_list", scn, "freehk_notes", 
                scn, "freehk_notes_index")
            col = row.column(align=True)
            col.operator("freehk_notes.list_action", icon='ZOOMIN', text="").action = 'ADD'
            col.operator("freehk_notes.list_action", icon='ZOOMOUT', text="").action = 'REMOVE'
            col.separator()
            col.operator("freehk_notes.list_action", icon='TRIA_UP', text="").action = 'UP'
            col.operator("freehk_notes.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
    
        else:
            row = layout.row()
            row.template_list("NOTES_UL_items", "freehk_notes_grid_list", scn, "freehk_notes", 
                scn, "freehk_notes_index", type='GRID', columns = 4)
            col = row.column(align=True)
            col.operator("freehk_notes.list_action", icon='ZOOMIN', text="").action = 'ADD'



        row = layout.row()
        col = row.column(align=True)
        row = col.row(align=True)
        row.operator("freehk_notes.clear_list", icon="X")
        row.prop(scn,"freehk_notes_compact")