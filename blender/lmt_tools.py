# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 03:11:41 2021

@author: AsteriskAmpersand
"""

import bpy
from .blenderOps import armaturePoll,getActiveAction,fetchFreeHKCustom
from .timl_controller import timl_properties,timl_propmap, geometryitems
from .timl_param_utils import timelineitems,timelineToDatatype
from ..ui.HKIcons import pcoll

TIMLCONTROLLER = "FreeHK_TIML_Controller"
LIMIT = 10

encodingTypes =  [("0","Detect","Infer F-Curve type from context"),
                ("1","Float Vector Base","Base Absolute Transform"),
                ("2","Float Rotation Key","Pure Quaternion Values"),
                ("3","Float Vector Key","Pure 3D Values"),
                ("4","Short LERP","LERP Parameters casted to normalized ushort"),
                ("5","Byte LERP","LERP Parameters casted to normalized ubyte"),
                ("6","14-bit Absolute Quaternion","Pure Quaternion compressed to 14 bit per field"),
                ("7","7-bit Quaternion LERP","LERP Parameters for Quaternion compressed to 7-bits"),
                ("11","Mono-Axial Quaternion X","Single Axis Rotation on X-Axis"),
                ("12","Mono-Axial Quaternion Y","Single Axis Rotation on Y-Axis"),
                ("13","Mono-Axial Quaternion Z","Single Axis Rotation on Z-Axis"),
                ("14","11-bit Quaternion LERP","Pure Quaternion compressed to 11 bit per field"),
                ("15","9-bit Quaternion LERP","Pure Quaternion compressed to 9 bit per field"),                                                
                ("-1","Reference Frame","Reference Frame for corresponding delta transform"),
                ]
encodingMap = {int(ix):[ix,name,desc] for ix,name,desc in encodingTypes}

def createTIMLController():
    empty = bpy.data.objects.new("TIML_Controller",None)
    bpy.context.scene.objects.link(empty)
    empty["Type"] = TIMLCONTROLLER
    return empty

class _PanelBase(object):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

class TIMLControllerObjectPanel(_PanelBase, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_freehk_object'
    bl_label = 'Free HK TIML Controls'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        if obj.type == "EMPTY" and "Type" in obj and obj["Type"] == TIMLCONTROLLER:
            return True
        return False

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        layout.prop(context.scene,"freehk_showall",text = "Show All")
        if obj.animation_data and obj.animation_data.action:
            properties = timl_properties if context.scene.freehk_showall else timelineToDatatype[obj.animation_data.action.freehk.timelineParam ]        
            for prop in properties:
                layout.prop(obj.FreeHKTiml, prop)

def TIMLControllerCheck(context,*args):
    found = False
    for obj in context.scene.objects:
        if obj.type == "EMPTY" and "Type" in obj and obj["Type"] == TIMLCONTROLLER:
            controller = obj
            found = True
    if not found:
        controller = createTIMLController()
    if not controller.animation_data:
        action =  controller.animation_data_create()
    else:
        action = controller.animation_data
    return action

def TIMLControllerCreation(self,context):
    if self.starType == "TIML_Action":
        action = TIMLControllerCheck(context)
        try:
            action.action = context.area.spaces[0].action
        except:
            for space in context.area.spaces:
                if hasattr(space,"action"):
                    action.action = space.action

def foldUpdate(self,context):
    action = self.id_data
    existing = {}
    for fcurve in action.fcurves:
        id = fcurve.data_path,fcurve.array_index%4
        if id in existing:
            fcurve.mute = not self.fold == "FOLDED"
            existing[id].mute = self.fold == "FOLDED"
            true = fcurve.array_index%4
            disp = true+4
            fcurve.array_index =  true if self.fold == "FOLDED" else disp
            existing[id].array_index = disp if self.fold == "FOLDED" else true
        else:
            fcurve.mute = False
            existing[id] = fcurve
        
        
class AnimData(bpy.types.PropertyGroup):
    #nextAction = bpy.props.PointerProperty(name = "Next Animation", type="Action")    
    starType = bpy.props.EnumProperty(name = "Type",
                                      items = [("None","None","Non MHW Action",pcoll["FREEHK_NONE_TYPE"].icon_id,0),
                                               ("LMT_Action","LMT","MHW Bone Action",pcoll["FREEHK_LMT_TYPE"].icon_id,1),
                                               ("TIML_Action","TIML","MHW TIML Action",pcoll["FREEHK_TIML_TYPE"].icon_id,2)],
                                      default = "None",
                                      update = TIMLControllerCreation)
    timelineParam = bpy.props.EnumProperty(name = "Timeline Type",
                                      items = timelineitems,
                                      default = "None")
    unkn0 = bpy.props.IntProperty(name = "Unknown",
                                  default = 0)
    
    transx = bpy.props.EnumProperty(name = "Translation X Map",items = geometryitems,default = "m8E8AFE06")
    transy = bpy.props.EnumProperty(name = "Translation Y Map",items = geometryitems,default = "mF98DCE90")
    transz = bpy.props.EnumProperty(name = "Translation Z Map",items = geometryitems,default = "m60849F2A")
    rotx = bpy.props.EnumProperty(name = "Rotation X Map",items = geometryitems,default = "mF105BBE3")
    roty = bpy.props.EnumProperty(name = "Rotation Y Map",items = geometryitems,default = "m86028B75")
    rotz = bpy.props.EnumProperty(name = "Rotation Z Map",items = geometryitems,default = "m1F0BDACF")
    #rotqw = bpy.props.EnumProperty(name = "Rotation QW Map",items = geometryitems,default = "")
    #rotqx = bpy.props.EnumProperty(name = "Rotation QX Map",items = geometryitems,default = "")
    #rotqy = bpy.props.EnumProperty(name = "Rotation QY Map",items = geometryitems,default = "")
    #rotqz = bpy.props.EnumProperty(name = "Rotation QZ Map",items = geometryitems,default = "")
    sclx = bpy.props.EnumProperty(name = "Scale X Map",items = geometryitems,default = "m9486DF23")
    scly = bpy.props.EnumProperty(name = "Scale Y Map",items = geometryitems,default = "mE381EFB5")
    sclz = bpy.props.EnumProperty(name = "Scale Z Map",items = geometryitems,default = "m7A88BE0F")
    #on update to TIML_Action remember to look for the TIML controller and
    #if it doesn't exist create it
    
    #animType = bpy.props.EnumProperty(name = "LMT Buffer Type",items = bufferitems,default = "None")
    #this is an fcurve property
    
    resample = bpy.props.BoolProperty(name = "Resample", description = "Add additional keyframes to have more control over exported animations", default = False)
    resampleRate = bpy.props.IntProperty(name = "Resample Rate", description = "Frequency on which to resample the animation. -1 for Dynamic Resampling", default = 1, min = 1)
    #Beats the F6 monstrosities for applying actions, add resample button
    
    fold = bpy.props.EnumProperty(name = "Folded Animation",items = [("MAIN","MAIN",""),("FOLDED","FOLDED","")],default = "MAIN", update = foldUpdate )
    #loopFrame = bpy.props.IntProperty(name="Loop Frame")
    frameCount = bpy.props.IntProperty(name="Frame Count",default = -1,min = -1)
    tetherFrame = bpy.props.PointerProperty(name="Tether Armature",type = bpy.types.Object,poll = armaturePoll)
    timl_reorder = bpy.props.EnumProperty(name = "TIML Order",items = [("BLENDER","BLENDER",""),("GAME","GAME","")],default = "BLENDER")

class KeyframeData(bpy.types.PropertyGroup):
    #lControl, rControl, interpolationMethod
    interpolationMethod = bpy.props.IntProperty(name="Interpolation Control", default = 2)

def timlMapSettings(context,layout,action):
    col = layout.column(align=True)
    op = col.operator("freehk.timl_remap", icon_value=pcoll["FREEHK"].icon_id, text="Remap Properties [F6]")
    for prop in ["trans","rot","scl"]:
        for axis in ["x","y","z"]:
            setattr(op,"from_"+prop+axis,getattr(action.freehk,prop+axis))
            setattr(op,"to_"+prop+axis,getattr(action.freehk,prop+axis))
    row = col.row(align=True)
    row.operator("freehk.resample_timl_fcurve", icon_value=pcoll["FREEHK_RESAMPLE"].icon_id, text="Resample Selected")
    action = getActiveAction(context)
    row.prop(action.freehk,"resampleRate","")
    col.operator("freehk.rescale_animation", icon_value=pcoll["FREEHK_RESAMPLE"].icon_id, text="Rescale Animation")
    
    
    #op.action = action

class LMTPanel():
    @classmethod
    def poll(cls,context):
        action = getActiveAction(context)
        if not action: return False
        return action.freehk.starType == "LMT_Action"
        
def lmtMapSettings(context,layout,action):
    #layout.prop(action.freehk,"loopFrame") 
    layout.prop(action.freehk,"frameCount") 
    row = layout.row(align=True)
    row.prop(action.freehk,"fold",expand=True) 
    r = layout.row(align=True)
    r.label("Tethered Armature: ")
    r.label(str(action.freehk.tetherFrame.name) if action.freehk.tetherFrame else "None")
    layout.operator("freehk.rescale_animation", icon_value=pcoll["FREEHK_RESAMPLE"].icon_id, text="Rescale Animation")
    

class ActionDataTools(bpy.types.Panel):
    bl_category = "MHW FreeHK"
    bl_idname = "panel.action_props"
    bl_label = "Action Data"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    # bl_category = "Tools"
    addon_key = __package__.split('.')[0]
    def draw(self, context):
        addon = context.user_preferences.addons[self.addon_key]
        self.addon_props = addon.preferences
        layout = self.layout
        action = getActiveAction(context)
        if action:
            box = layout.box()
            self.draw_action_props(context,box,action)
            self.draw_mod_tools(context, box,action)
        #layout.prop(self, "starType", name="FreeHK Type")
        layout.separator()

    def draw_mod_tools(self, context, layout,action):
        #Convert Empty to Skeleton
        #Convert Skeleton to Empties
        #Create TIML Controller, Ignores if already exists
        #Global Untether
        #Global Transfer
        if action.freehk.starType == "TIML_Action":
            timlMapSettings(context,layout,action)
        if action.freehk.starType == "LMT_Action":
            lmtMapSettings(context,layout,action)

    def draw_action_props(self, context, layout,action):
        layout.prop(action.freehk,"starType",text = "FreeHK Action Type")
        if action.freehk.starType == "TIML_Action":
            #layout.separator()
            #layout.label("FreeHK TIML Paramaters")
            layout.prop(action.freehk,"timelineParam",text = "FreeHK Timeline Type")
            layout.prop(action.freehk,"unkn0",text = "FreeHK Unknown Parameter")
            
            col = layout.column(align = True)
            col.label("Property Export Order")
            row = col.row()
            row.prop(action.freehk,"timl_reorder",expand=True) 
            
            #layout.separator()
            layout.label(text = "TIML Remappping")
            col = layout.column(align = True)
            col.prop(action.freehk,"transx")
            col.prop(action.freehk,"transy")
            col.prop(action.freehk,"transz")
            col = layout.column(align = True)
            col.prop(action.freehk,"rotx")
            col.prop(action.freehk,"roty")
            col.prop(action.freehk,"rotz")
            col = layout.column(align = True)
            col.prop(action.freehk,"sclx")
            col.prop(action.freehk,"scly")
            col.prop(action.freehk,"sclz")
            
lmtTools = ["clear_tether","transform_tether_silent","transform_tether","update_name","update_bone_function",
            "complete_channels","synchronize_keyframes",
            "resample_fcurve","resample_action","create_fcurve_action",
            "clear_buffer_quality","maximize_buffer_quality",
            "check_export"
            ]
lmtDescriptions = ["Clear %sTethers","Transfer %sTethers","Transfer %s& Update","Update %sNames",
                   "Update %sBone Functions","Complete %sChannels","Synchronize %sKeyframes",
                   "Resample %sSelected FCurves","Resample %sFCurves","Enable %sFreeHK FCurves",
                   "Clear %sEncodings","Maximize %sEncodings",
                   "Check %sfor Export"]
lmtIcons = ["FREEHK_CLEAR","FREEHK_TRANSFER_SILENT","FREEHK_TRANSFER","FREEHK_NAMES","FREEHK_BONES",
            "FREEHK_CHANNELS","FREEHK_SYNCRHONIZE",
            "FREEHK_RESAMPLE","FREEHK_RESAMPLE","FREEHK",
            "FREEHK_CLEAR_ENCODE","FREEHK_MAX_ENCODE",
            "FREEHK_CHECK"]

#layout.operator("freehk.resample_fcurve",icon_value=pcoll["FREEHK"].icon_id, text="Add FreeHK Props")
#layout.operator("freehk.create_fcurve_action",icon_value=pcoll["FREEHK"].icon_id, text="Add FreeHK Props")

class ActionTools(LMTPanel,bpy.types.Panel):
    bl_category = "MHW FreeHK"
    bl_idname = "panel.action_tools"
    bl_label = "Action Tools"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    # bl_category = "Tools"
    addon_key = __package__.split('.')[0]
    
    def draw(self, context):
        addon = context.user_preferences.addons[self.addon_key]
        self.addon_props = addon.preferences
        layout = self.layout
        row = layout.row(align = True)
        row.prop(bpy.context.scene,"freehk_limit") 
        if bpy.context.scene.freehk_limit:
            actionName = ""
            iconName = ""
        else:
            actionName = "All "
            iconName = "_TOTAL"
        c = layout.column(align=True)
        for tool,desc,icon in zip(lmtTools,lmtDescriptions,lmtIcons):
            if "transform_tether" in tool or tool == "resample_action":
                l = c.row(align = True)
            else:
                l = c
            operator = l.operator("freehk.%s"%tool,icon_value=pcoll[icon+iconName].icon_id, text=desc%actionName)
            operator.limit = bpy.context.scene.freehk_limit
            if tool == "transform_tether" or tool == "transform_tether_silent":
                l.prop(context.scene,"freehk_tether",text = "")#,text = "Transfer Target")
            if tool == "resample_action":
                action = getActiveAction(context)
                l.prop(action.freehk,"resampleRate","")
            
class FCurveData(bpy.types.PropertyGroup):
    starType = bpy.props.EnumProperty(name = "Type",
                                      items = [("1","Float Vector Base","Base Absolute Transform"),
                                                ("2","Float Rotation Key","Pure Quaternion Values"),
                                                ("3","Float Vector Key","Pure 3D Values"),
                                                ("4","Short LERP","LERP Parameters casted to normalized ushort"),
                                                ("5","Byte LERP","LERP Parameters casted to normalized ubyte"),
                                                ("6","14-bit Absolute Quaternion","Pure Quaternion compressed to 14 bit per field"),
                                                ("7","7-bit Quaternion LERP","LERP Parameters for Quaternion compressed to 7-bits"),
                                                ("11","Mono-Axial Quaternion X","Single Axis Rotation on X-Axis"),
                                                ("12","Mono-Axial Quaternion Y","Single Axis Rotation on Y-Axis"),
                                                ("13","Mono-Axial Quaternion Z","Single Axis Rotation on Z-Axis"),
                                                ("14","11-bit Quaternion LERP","Pure Quaternion compressed to 11 bit per field"),
                                                ("15","9-bit Quaternion LERP","Pure Quaternion compressed to 9 bit per field"),
                                                ("0","Detect","Infer F-Curve type from context"),
                                                ("8","Reference Frame","Reference Frame for corresponding delta transform"),
                                                ],
                                      default = "0",)
    boneFunction = bpy.props.IntProperty(name = "Bone Function",description = "Bone Function ID")  

stringmap = {"location":"Location",
             "rotation_euler":"Euler Rotation",
             "rotation_quaternion":"Quaternion Rotation",
             "scale":"Scale","color":"Color"} 

def axislessDataPath(path):
    parts = path.split(".")
    transform = ""
    if parts[-1] in stringmap:
        transform = stringmap[parts[-1] ]
    root = path
    if '["' in path and '"]' in path:
        root = path[path.index('["')+2: path.index('"]')]
    return root+" "+transform

def actionDataPath(fcurve):
    path = fcurve.data_path
    parts = path.split(".")
    transform = ""
    if parts[-1] in stringmap:
        transform = stringmap[parts[-1] ]
        if transform == "Location" or transform == "Euler Rotation": 
            transform += ' '+['X','Y','Z','','Folded X','Folded Y','Folded Z'][fcurve.array_index]
        if transform == "Quaternion Rotation": 
            transform += ' '+['W','X','Y','Z','Folded W','Folded X','Folded Y','Folded Z'][fcurve.array_index]
    root = path
    if '["' in path and '"]' in path:
        root = path[path.index('["')+2: path.index('"]')]
    return root+" "+transform

def nameDataPath(fcurve):
    path = fcurve.data_path
    if path in stringmap:
        path = stringmap[path]
        if path == "Location" or path == "Euler Rotation": 
            path += ' '+['X','Y','Z'][fcurve.array_index]
        if path == "Quaternion Rotation": 
            path += ' '+['W','X','Y','Z'][fcurve.array_index]
        if path == "Color":
            path += ' '+['R','G','B','A'][fcurve.array_index]
    if path.split(".")[-1] in timl_propmap:
        path = timl_propmap[path.split(".")[-1]]
    return path

def encodingName(ix):
    if ix not in encodingMap:
        return "Illegal Encoding Type"
    return encodingMap[ix][1]

class FCurveTools(LMTPanel,bpy.types.Panel):
    bl_category = "MHW FreeHK"
    bl_idname = "panel.fcurve_props"
    bl_label = "F-Curve Data"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    # bl_category = "Tools"
    addon_key = __package__.split('.')[0]
    
    def draw(self, context):
        addon = context.user_preferences.addons[self.addon_key]
        self.addon_props = addon.preferences        
        layout = self.layout
        try:
            action = getActiveAction(context)
        except Exception as e:
            return
        count = 0
        limit = LIMIT
        if action and action.freehk.starType == "LMT_Action":
            col = layout.column(align=True)
            add = col.operator("freehk.add_keyframes",icon_value=pcoll["FREEHK_ERR_FIX"].icon_id)
            add.action = bpy.data.actions.find(action.name)
            fold = col.operator("freehk.fold_fcurve",text = "Fold Selected F-Curves",icon_value=pcoll["FREEHK_ERR_ERROR"].icon_id)
            fold.action = bpy.data.actions.find(action.name)            
            for fi,fcurve in enumerate(action.fcurves):
                if fcurve.select:
                    box = layout.box()
                    col = box.column(align = True)
                    col.label("%s F-Curve"%actionDataPath(fcurve))
                    modified = False
                    mod = fetchFreeHKCustom(fcurve)
                    if mod:
                        col.label(encodingName(round(mod.min_x)))
                        col.prop(mod,"min_x",text = "Encoding Type" )
                        col.prop(mod,"min_y",text = "Bone Function")
                        modified = True
                    if not modified:
                        creator = col.operator("freehk.create_fcurve",icon_value=pcoll["FREEHK"].icon_id, text="Add FreeHK Props")
                        creator.action = bpy.data.actions.find(action.name)
                        creator.fcurve = fi
                    #layout.separator()
                    count += 1
                if count >= limit: break


class KeyframeTools(bpy.types.Panel):
    bl_category = "MHW FreeHK"
    bl_idname = "panel.keyframe_props"
    bl_label = "Keyframe Data"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"
    addon_key = __package__.split('.')[0]
    
    def displayAction(self,layout,action):
        count = 0
        limit = LIMIT
        if action:
            for fcurve in action.fcurves :
                for p in fcurve.keyframe_points :
                    if p.select_control_point:
                        box = layout.box()
                        col = box.column(align=True)
                        #.array_index
                        if action.freehk.starType == "LMT_Action":
                            path = actionDataPath(fcurve)
                        else:
                            path = nameDataPath(fcurve)
                        col.label("%s Keyframe [%d]"%(path,p.co[0]))
                        if action.freehk.starType == "TIML_Action":
                            col.prop(p, "interpolation", text="FreeHK Interpolation")
                        row = col.row(align=True)
                        row.label("FreeHK Frame Value")
                        row.prop(p,"co",index=0,text="Time")
                        row.prop(p,"co",index=1,text="Value")
                        if action.freehk.starType == "TIML_Action":
                            col.prop(p, "back", text="FreeHK Parameter 1")
                            col.prop(p, "period", text="FreeHK Parameter 2")
                        #layout.separator()
                        count += 1    
                        if count >= limit: return
    def draw(self, context):
        addon = context.user_preferences.addons[self.addon_key]
        self.addon_props = addon.preferences        
        layout = self.layout     
        try:
            action = getActiveAction(context)
        except Exception as e:
            return
        self.displayAction(layout,action) 
                    
        self.draw_mod_tools(context, layout)
        layout.separator()
        
    def draw_mod_tools(self, context, layout):
        #Create freehk timl       
        pass

    
classes = [
    AnimData,ActionTools,FCurveData,KeyframeData,ActionDataTools,FCurveTools,KeyframeTools,TIMLControllerObjectPanel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Action.freehk = bpy.props.PointerProperty(type=AnimData)
    bpy.types.Scene.freehk_showall =  bpy.props.BoolProperty(name = "Display All",default = False)
    bpy.types.Scene.freehk_tether =  bpy.props.PointerProperty(name = "Tether Target",type = bpy.types.Object,poll = armaturePoll)
    bpy.types.Scene.freehk_limit =  bpy.props.BoolProperty(name = "Limit Operator",default = True)
    
def unregister():
    del bpy.types.Scene.freehk_limit
    del bpy.types.Scene.freehk_tether
    del bpy.types.Scene.freehk_showall
    del bpy.types.Action.freehk
    for cls in classes:
        bpy.utils.unregister_class(cls)

