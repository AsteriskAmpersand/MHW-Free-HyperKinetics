# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 13:26:27 2021

@author: Asterisk
"""
import bpy
from bpy.app.handlers import persistent
from .timl_importer import bigFlags,TIMLJoin,TIMLSplitter,interpolationMapping
from .timl_controller import timl_propmap
from .lmt_tools import TIMLCONTROLLER

propName = "m%08X"
flagHash = [propName%p for p in bigFlags]

class ChannelKeyframe(bpy.types.PropertyGroup):
    #name = StringProperty() -> Instantiated by default
    time = bpy.props.IntProperty()
    buffered = bpy.props.BoolProperty(name = "Buffered")
    active = bpy.props.BoolProperty(name = "Active")
    def compile(self):
        return (self.active<<1)+self.buffered
    

class KeyframeChannels(bpy.types.PropertyGroup):
    hide = bpy.props.BoolProperty(default = False)
    index = bpy.props.IntProperty()
    keyframes = bpy.props.CollectionProperty(type=ChannelKeyframe)
    def empty(self):
        for kf in self.keyframes:
            if kf.buffered or kf.active:
                return False
        return True

def bigFlagCheck(self,context):
    result = []
    used = set()
    if context.active_object:
        if hasattr(context.active_object, "FreeHKTiml"):
            if context.active_object.animation_data:
                if context.active_object.animation_data.action:
                    for fcurve in context.active_object.animation_data.action.fcurves:
                        prop = fcurve.data_path.split(".")[-1]
                        if prop in flagHash and prop not in used:
                            used.add(prop)
                            result.append((prop,timl_propmap[prop],""))
                            
    return result

class InputEditorProperties(bpy.types.PropertyGroup):
    datapath = bpy.props.EnumProperty( items = bigFlagCheck,name = "Input Property")
    inputs = bpy.props.CollectionProperty(type=KeyframeChannels)
    show_unused = bpy.props.BoolProperty(name = "Show Unused Channels", default = False)
    update_parameters = bpy.props.BoolProperty(name = "Update FreeHK Parameter", default = True)

class InputEditorGet(bpy.types.Operator):
    bl_idname = "freehk_inputs.get"
    bl_label = "Get Inputs"
    bl_description = "Copy TIML Controller Input Flag Keyframes into Panel"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return not not bigFlagCheck(cls,context)

    def execute(self, context):
        editor = context.scene.freehk_input_editor
        for channel in editor.inputs:
            channel.keyframes.clear()
            channel.hide = False
            channel.index = 0
        #channels = [editor.inputs.add() for i in range(8)]
        context.scene.update()
        
        for fcurve in context.active_object.animation_data.action.fcurves:
            if "FreeHKTiml."+editor.datapath == fcurve.data_path:
                offset = fcurve.array_index*8
                binsplit = lambda  x: (bool(x&1),bool(x&2))
                getPair = lambda ix,val: binsplit((round(val)&(3 << 2*ix))>>2*ix)
                for kf in fcurve.keyframe_points:
                    for i in range(0,8):
                        ix = i+offset
                        channel = editor.inputs[ix]
                        item = channel.keyframes.add()
                        buffer, active = getPair(i,kf.co[1])
                        item.buffered = buffer
                        item.active = active
                        item.time = round(kf.co[0])
                        #print("Added Frame to Channel %d with [%d|%d\%d]"%(ix,item.time,item.buffered,item.active))

        for channel in editor.inputs:
        #    print(len(channel.keyframes))
            if channel.empty() or not len(channel.keyframes):
                channel.hide = True
        return{'FINISHED'}

def orList(lst):
    val = 0
    for v in lst:
        val |= v
    return val

class InputEditorSet(bpy.types.Operator):
    bl_idname = "freehk_inputs.set"
    bl_label = "Set Inputs"
    bl_description = "Set TIML Controller Input Flag Keyframes from Panel into current action"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.freehk_input_editor.inputs) and not not bigFlagCheck(cls,context)

    def compileRange(self,editor,ix):
        f = []
        for frames in zip(*[channel.keyframes for channel in editor.inputs[ix:ix+8]]):
            frameval = 0
            for kf in reversed(frames):
                frameval = kf.compile() + (frameval << 2)
            t = frames[0].time
            f.append((t,frameval))
        return f

    def compileFrames(self,context):
        editor = context.scene.freehk_input_editor
        lower = self.compileRange(editor,0)
        upper = self.compileRange(editor,8)
        lindices = set((t for t,f in lower))
        uindices = set((t for t,f in upper))
        return (lower,upper),(lindices,uindices)

    def newKeyframes(self,kp,framelist):
        kfs = [k for k in kp]
        for k in reversed(kfs):
            try: kp.remove(k)
            except: pass
        kp.add(len(framelist))
        last = orList([ f[1] for f in framelist])
        for ix,(t,kf) in enumerate(framelist):
            kp[ix].co = t,kf
            kp[ix].back = last
            kp[ix].period = 0
            kp[ix].interpolation = interpolationMapping[5]

    def replaceKeyframes(self,kfdic,framelist,update):
        last = orList([ f[1] for f in framelist])
        for t,kf in framelist:
            keyframe = kfdic[t]
            keyframe.co[1] = kf
            if update:
                keyframe.back = last
                keyframe.period = 0

    def execute(self, context):
        frames,findices = self.compileFrames(context)
        found = [False,False]
        editor = context.scene.freehk_input_editor
        action = context.active_object.animation_data.action
        for fcurve in action.fcurves:
            ix = fcurve.array_index
            if "FreeHKTiml."+editor.datapath == fcurve.data_path and ix < 2: 
                indices = {round(k.co[0]):k for k in fcurve.keyframe_points}
                actual_indices = set(indices.keys())
                if actual_indices == findices[ix]:
                    self.replaceKeyframes(indices,frames[ix],editor.update_parameters)
                else:
                    self.newKeyframes(fcurve.keyframe_points,frames[ix])         
        for i,create in enumerate(found):
            if create:
                fcurve = action.fcurves.new(data_path = editor.datapath, index=i)
                self.newKeyframes(fcurve.keyframe_points,frames[i])
        return{'FINISHED'}

class ChannelDisplayItems(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label("%d"%item.time)
        row.prop(item,"buffered")
        row.prop(item,"active")
    def invoke(self, context, event):
        pass

def zerostrGen(ix):
    z = list("00"*4)
    z[(ix%4)*2:((ix%4)+1)*2] = "XX"
    return ''.join(list(reversed(''.join(z))))

def displayBinaryOffset(ix):
    dummy = "FF"
    position = ix//4
    zerostr = [dummy if position != 3-i else zerostrGen(ix) for i in range(4)]
    return ' '.join(zerostr)

class TIMLControllerObjectPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_idname = 'panel.input_editor'
    bl_label = 'Free HK Input Editing'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        if obj.type == "EMPTY" and "Type" in obj and obj["Type"] == TIMLCONTROLLER and\
            obj.animation_data and obj.animation_data.action:
            return True
        return False

    def draw(self, context):
        input_editor = context.scene.freehk_input_editor
        layout = self.layout
        row = layout.row(align=True)
        row.operator("freehk_inputs.get")
        row.operator("freehk_inputs.set")
        layout.prop(input_editor,"datapath")
        row = layout.row(align=True)
        row.prop(input_editor,"show_unused")
        row.prop(input_editor,"update_parameters")
        for ix,keyframe_channel in enumerate(input_editor.inputs):
            if input_editor.show_unused or not keyframe_channel.hide:
                col = layout.column(align=True)
                col.label("%s[%d] - %s"%(input_editor.datapath,ix,displayBinaryOffset(ix)))
                col.template_list("ChannelDisplayItems", "freehk_inputs_grid_list", keyframe_channel, "keyframes", 
                                     keyframe_channel, "index")
                #Display the whole list here


def onRegister(scene):
    for i in range(16):
        c = bpy.context.scene.freehk_input_editor.inputs.add()
        c.hide = True
    # the handler isn't needed anymore, so remove it
    try:
        bpy.app.handlers.scene_update_post.remove(onRegister)    
    except:
        pass

@persistent
def onFileLoaded(scene):
    onRegister(scene)


classes = [ChannelKeyframe,KeyframeChannels,InputEditorProperties,InputEditorGet,
           InputEditorSet,ChannelDisplayItems,TIMLControllerObjectPanel]


def register():    
    for cl in classes:
        bpy.utils.register_class(cl)
    bpy.types.Scene.freehk_input_editor = bpy.props.PointerProperty(type = InputEditorProperties)
    bpy.app.handlers.scene_update_post.append(onRegister)
    bpy.app.handlers.load_post.append(onFileLoaded)
    
def unregister(): 
    del bpy.types.Scene.freehk_input_editor
    for cl in classes:
        bpy.utils.unregister_class(cl)
    bpy.app.handlers.load_post.remove(onFileLoaded)
#bpy.types.Scene.freehk_input_editor.clear()

"""

    col = layout.column(align=True)
    for i in range(8):
        row = col.row(align=True)
        row.label("Prop %d"%i)
        row.prop(context.scene.freehk_binary,"bool_test",index = 2*i,text = "")
        row.prop(context.scene.freehk_binary,"bool_test",index = 2*i+1,text = "")
"""