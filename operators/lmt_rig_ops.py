# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 19:00:29 2021

@author: AsteriskAmpersand
"""
import bpy
from bpy.app.handlers import persistent
from mathutils import Vector
from ..blender.blenderOps import fetchBoneFunction,animationLength,completeBasis
from ..blender.tetherOps import updateAnimationBoneFunctions
from ..ui.HKIcons import pcoll
# Left Leg Orientation and IK
# 250 -> 16
# Right Leg Orientation and IK
# 249 -> 20
# Head (No Rotation)
# 252 -> 4
# Neck (No Rotation)
# 254 -> 3
# Right Hand 
# 247 -> 12
# Left Hand
# 248 -> 8


def getRigs(self,context):
    return [(obj.name,obj.name,"") for obj in bpy.data.objects if obj.type == "ARMATURE" and "FreeHK_GuideClone_" not in obj.name]

def getMHWArmatures(self,context):
    return [(obj.name,obj.name,"") for obj in bpy.data.objects if obj.type == "ARMATURE" and "FreeHK_GuideClone_" not in obj.name]


class RigTransferData(bpy.types.PropertyGroup):
    #nextAction = bpy.props.PointerProperty(name = "Next Animation", type="Action")    
    rigType = bpy.props.EnumProperty(name = "Rig Type",
                                      items = [("Humanoid","Humanoid","Humanoid Rig"),#,pcoll["FREEHK_PL"].icon_id,0),
                                               ("Monster2","Biped Monster","Biped Monster"),#,pcoll["FREEHK_EM2"].icon_id,1),
                                               ("Monster4","Quadruped Monster","Quadruped Monster"),#,pcoll["FREEHK_EM4"].icon_id,2),
                                               ("Custom","Generic Rig","Generic Rig"),#,pcoll["FREEHK_Custom"].icon_id,3),
                                               ],
                                      default = "Humanoid")
    cat = bpy.props.BoolProperty(name = "CAT Rig", description = "Perform CAT Normalization Operations",default = False)                               
    sourceName = bpy.props.EnumProperty(name = "Source Rig", description = "Non-MHW Armature with Animation", items = getRigs)
    targetName = bpy.props.EnumProperty(name = "Target Rig", description = "MHW Armature to bake Animation into", items = getMHWArmatures) 
    bake = bpy.props.BoolProperty(name = "Bake",default = True)
    groundRoot = bpy.props.BoolProperty(name = "Root as Ground Level", description = "Set the Root as the ground level after baking",default = True)
    
    
class PlatformIKMapping(bpy.types.PropertyGroup):
    platformName = bpy.props.StringProperty(name = "Platform Role")
    platformBoneFunction = bpy.props.IntProperty(name = "Platform Function")
    platformBoneTarget = bpy.props.IntProperty(name = "Target Function")
    platformTracking = bpy.props.EnumProperty(name = "Tracking Type",
                                      items = [("Ground","Ground Shadow","Follows another bone at flat ground level (used for feet)"),
                                               ("Translation","Translation","Follows another bone position but not rotation (used for neck)"),
                                               ("Rotation","Rotation","Follows another bone's rotation (not used by platforms)"),
                                               ("Transform","Transform","Identically copies another bone (used by wrists)"),
                                               ])

class PlatformGroup(bpy.types.PropertyGroup):
    bone_presets = bpy.props.CollectionProperty(type=PlatformIKMapping)    


class PlatformSingleton(bpy.types.PropertyGroup):
    presets = bpy.props.CollectionProperty(type=PlatformGroup)

def setDefaultCollectionValue():
    registerPresetRigOps(bpy.context.scene.freehk_rig_ops_platform)

def onRegister(scene):
    setDefaultCollectionValue()
    # the handler isn't needed anymore, so remove it
    try:
        bpy.app.handlers.scene_update_post.remove(onRegister)    
    except:
        pass

@persistent
def onFileLoaded(scene):
    onRegister(scene)

def registerPresetRigOps(platformCollection):
    if not platformCollection.presets:
        for presetn,platforms in platformDefaults.items():
            preset = platformCollection.presets.add()
            preset.name = presetn
            for name,function,default,track in platforms:
                platform = preset.bone_presets.add()
                platform.name = name
                platform.platformName = name
                platform.platformBoneFunction = function
                platform.platformBoneTarget = default
                platform.platformTracking = track

class RigTransferTools(bpy.types.Panel):
    bl_category = "MHW Tools"
    bl_idname = "panel.rig_props"
    bl_label = "Rig Transfer Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    # bl_category = "Tools"
    addon_key = __package__.split('.')[0]
    def draw(self, context):
        addon = context.user_preferences.addons[self.addon_key]
        self.addon_props = addon.preferences
        props = bpy.context.scene.freehk_rig_ops
        layout = self.layout
        layout.prop(props,"cat")
        layout.prop(props,"rigType")        
        layout.prop(props,"sourceName")
        layout.prop(props,"targetName")
        layout.prop(props,"bake")
        if props.bake:
            layout.prop(props,"groundRoot")
        layout.operator("freehk.rig_transfer",text = "Transfer")
        #col = layout.column(align = True)
        platform = bpy.context.scene.freehk_rig_ops_platform
        for bone in platform.presets[props.rigType].bone_presets:
            box = layout.box()
            box = box.column(align=True)
            box.label(bone.platformName)
            row = box.row(align = True)
            if props.rigType == "Custom":
                row.prop(bone,"platformBoneFunction")
            else:
                row.label("Platform Function: "+str(bone.platformBoneFunction))
            row.prop(bone,"platformBoneTarget")
            box.prop(bone,"platformTracking")
                

platformDefaults = {
                    "Humanoid":[("Neck",254,3,"Translation"),
                                ("Head",252,4,"Translation"),
                                ("Right Wrist",247,12,"Transform"),
                                ("Left Wrist",248,8,"Transform"),
                                ("Right Leg",249,20,"Ground"),
                                ("Left Leg",250,16,"Ground")],
                    
                    "Monster2":[("Neck Base",251,3,"Translation"),
                                ("Head",252,3,"Translation"),
                                ("Neck",254,3,"Translation"),
                                ("Right Leg",249,90,"Ground"),
                                ("Left Leg",250,80,"Ground"),
                                ("Unknown",253,-1,"Ground")],
    
                    "Monster4":[("Neck Base",251,3,"Translation"),
                                ("Head",252,3,"Translation"),
                                ("Neck",254,3,"Translation"),
                                ("Front Right Leg",247,-2,"Ground"),
                                ("Front Left Leg",248,-2,"Ground"),
                                ("Back Right Leg",249,-2,"Ground"),
                                ("Back Left Leg",250,-2,"Ground"),
                                ("Unknown",253,-1,"Ground")],
    
                    "Custom":[("Platform 0",247,-2,"Transform"),
                            ("Platform 1",248,-2,"Transform"),
                            ("Platform 2",249,-2,"Transform"),
                            ("Platform 3",250,-2,"Transform"),
                            ("Platform 4",251,-2,"Transform"),
                            ("Platform 5",252,-2,"Transform"),
                            ("Platform 6",253,-2,"Transform"),
                            ("Platform 7",254,-2,"Transform"),
                            ("Platform 8",255,-2,"Transform")],
                    }
    

class AnimationMissing(Exception):
    pass

#Source is a MHW Metarig with exotic animations
#Target is a MHW Basic Rig with orthogonal arm elements etc.

source = ""
target = ""

def bakeAnimation(context,target):
    context.scene.update()
    prev_mode = target.mode # save
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    for obj in selection: obj.select = False
    active = bpy.context.scene.objects.active
    bpy.context.scene.objects.active = target
    target.select = True
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.nla.bake(frame_start=context.scene.frame_start, 
                     frame_end=context.scene.frame_end, 
                     step=1, 
                     only_selected=False, 
                     visual_keying=True, 
                     clear_constraints=True, 
                     clear_parents=False, 
                     use_current_action=True, 
                     bake_types={'POSE'})
    target.select = False
    for obj in selection: obj.select = True
    bpy.ops.object.mode_set(mode=prev_mode) # restore
    bpy.context.scene.objects.active = active

def muteGlobal(catAction):
    for fcurve in catAction:
        if "." not in fcurve.data_path:
            fcurve.mute = True

class RigAnimationTransfer(bpy.types.Operator):
    bl_idname = "freehk.rig_transfer"
    bl_label = "Rig Transfer"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Transfer Animation from Rig to MHW Skeleton"
    #sourceName = bpy.props.EnumProperty(name = "Source Rig", description = "Non-MHW Armature with Animation", items = getRigs)
    #targetName = bpy.props.EnumProperty(name = "Target Rig", description = "MHW Armature to bake Animation into", items = getMHWArmatures) 
    #bake = bpy.props.BoolProperty(name = "Bake",default = True)
    #groundRoot = bpy.props.BoolProperty(name = "Root as Ground Level", description = "Set the Root as the ground level after baking",default = True)

    #def invoke(self, context, event):
    #    return context.window_manager.invoke_props_dialog(self)

    #def draw(self, context):
    #    row = self.layout
    #    row.prop(self, "sourceName")
    #    row.prop(self, "targetName")
    #    row.prop(self, "bake")
    #    row.prop(self, "groundRoot")
    
    def addMissingTrackers(self,boneMapping):
        matchedPairs = self.constraintFallthrough.items()#[(250,16),(249,20),(252,4),(254,3),(247,12),(248,8)]
        for l,r in matchedPairs:
            if l not in boneMapping:
                if r in boneMapping:
                    boneMapping[l] = boneMapping[r]
        return
    
    def addSpecialCases(self,mapper,bone):
        if not self.humanoid:
            return
        candidate = None
        candidates = {"CTRL_Root":-1,
                        "CTRL_Leg_IK_L":250,
                        "CTRL_Leg_IK_R":249,
                        "CTRL_Hand_IK_L":248,
                        "CTRL_Hand_IK_R":247}
        if bone.name in candidates:
            candidate = candidates[bone.name]
        if candidate and candidate not in mapper:
            mapper[candidate] = bone    
    
    def groundedConstraint(self,bone,target):
        targetArmature,targetBone = target
        c = bone.constraints.new("COPY_LOCATION")
        c.target = targetArmature
        c.subtarget = targetBone.name
        c.use_y = False
        c = bone.constraints.new("COPY_ROTATION")
        c.target = targetArmature
        c.subtarget = targetBone.name
        c.use_x = False
        c.use_z = False
        if hasattr(self,"ground") and self.ground:
            c = bone.constraints.new("COPY_LOCATION")
            c.target = targetArmature
            c.subtarget = self.ground
            c.use_x = False
            c.use_z = False
    @staticmethod
    def translationConstraint(bone,target):
        targetArmature,targetBone = target
        c = bone.constraints.new("COPY_LOCATION")
        c.target = targetArmature
        c.subtarget = targetBone.name
    @staticmethod
    def localTranslationConstraint(bone,target):
        targetArmature,targetBone = target
        c = bone.constraints.new("COPY_LOCATION")
        c.target = targetArmature
        c.subtarget = targetBone.name
        c.target_space = "LOCAL_WITH_PARENT"
        c.owner_space = "LOCAL_WITH_PARENT"
    @staticmethod
    def rotationConstraint(bone,target):
        targetArmature,targetBone = target
        c = bone.constraints.new("COPY_ROTATION")
        c.target = targetArmature
        c.subtarget = targetBone.name
    @staticmethod
    def transformConstraint(bone,target):
        targetArmature,targetBone = target
        c = bone.constraints.new("COPY_TRANSFORMS")
        c.target = targetArmature
        c.subtarget = targetBone.name
    
    def getConstraintMaker(self,bf):
        if bf in [-1]:
            return self.transformConstraint
        if bf in [0]:
            return self.localTranslationConstraint
        if bf in self.constraintMapDict:
            return self.constraintMapDict[bf]
        #if bf in [252,254]:
        #    return self.translationConstraint
        #if bf in [-1,247,248]:
        #    return self.transformConstraint
        #if bf in [249,250]:
        #    return self.groundedConstraint
        return self.rotationConstraint
    
    
    @staticmethod
    def doubleBoneDict(repeatableDict):
        new = {}
        for key,val in repeatableDict.items():
            if val.name not in new:
                new[val.name] = set()
            new[val.name].add(key)
        return new
    
    def addConstraints(self,source,copy,target):
        targetMapper = {}
        for bone in target.pose.bones:
            if "boneFunction" in bone.bone:
                targetMapper[bone.bone["boneFunction"]] = bone
        
        boneMapper = {}
        for bone in copy.pose.bones:
            if "boneFunction" in bone and "__orthogonalizer__" in bone:
                boneMapper[bone["boneFunction"]] = bone
            self.addSpecialCases(boneMapper,bone)
        self.addMissingTrackers(boneMapper)
        clonableBones = self.doubleBoneDict(boneMapper)
        
        self.ground = boneMapper[-1].name if -1 in boneMapper else None            
            
        #clonableBones = { bone.name:func for func,bone in boneMapper.items()}
        for bone in copy.pose.bones:            
            subtarget = bone
            self.transformConstraint(bone,(source,subtarget))
            if bone.name in clonableBones:
                for bf in clonableBones[bone.name]:
                    #Create the constraint linking the pair of bones
                    if bf in targetMapper:
                        subtarget = bone
                        constraintMaker = self.getConstraintMaker(bf)
                        constraintMaker(targetMapper[bf],(copy,subtarget))
        return
    
    def generateOrthogonalizer(self,copy,target):
        boneMapper = {}
        for bone in target.pose.bones:
            if "boneFunction" in bone.bone:
                boneMapper[bone.bone["boneFunction"]] = bone      
        
        prev_mode = copy.mode # save
        active = bpy.context.scene.objects.active
        bpy.context.scene.objects.active = copy
        bpy.ops.object.mode_set(mode='EDIT')
        additions = []
        ebs = copy.data.edit_bones
        for bone,ebone in zip(copy.pose.bones,ebs):
            if "boneFunction" in bone:
                bf = bone["boneFunction"]
                if bf in boneMapper:
                    orthogonal = boneMapper[bf]
                    delta = (orthogonal.matrix*Vector((0,1,0,0))).normalized().to_3d()
                else:
                    delta = Vector((0,1,0))
                head = bone.tail
                additions.append(("__Animation_Tracker_Bone__"+bone.name,head,delta,ebone,bf))
    
        orthogonal = {}
        for name,head,delta,parent,bf in additions:
            eb = ebs.new(name)
            eb.parent = parent
            eb.tail = head+delta
            eb.head = head
            eb.hide = True
            orthogonal[eb.name] = bf
            
        bpy.ops.object.mode_set(mode=prev_mode) # restore
        bpy.context.scene.objects.active = active
        for bone in copy.pose.bones:
            if bone.name in orthogonal:
                bone["__orthogonalizer__"] = True
                bone["boneFunction"] = orthogonal[bone.name]
    
    def bakeOperation(self,context,source,target):
        if not source.animation_data or not source.animation_data.action:
            raise AnimationMissing("No animation data to bake")
        actionname = "FreeHK_"+source.animation_data.action.name
        if not target.animation_data:
            animData = target.animation_data_create()
        else:
            animData = target.animation_data
        newAction = bpy.data.actions.new(actionname)
        animData.action = newAction
        bakeAnimation(context,target)
        return newAction


    #Clone Armature
    @staticmethod
    def cloneArmature(source,copyAction = True):
        #copy = source.copy()
        copy = bpy.data.objects.new('FreeHK_GuideClone_'+source.name, source.data)
        bpy.context.scene.objects.link(copy)
        if copyAction and source.animation_data:
            if source.animation_data.action:
                new_action = bpy.data.actions.new(name = "FreeHK_"+source.animation_data.action.name)
                copy.animation_data_create()
                copy.animation_data.action = new_action
            else:
                raise AnimationMissing()
        bpy.context.scene.update()
        
        functionCloning = {}
        for sourcePB in source.pose.bones:
            if "boneFunction" in sourcePB:
                functionCloning[sourcePB.name] = sourcePB["boneFunction"]                
        for copyPB in copy.pose.bones:
            if copyPB.name in functionCloning:
                copyPB["boneFunction"] = functionCloning[copyPB.name]
                
        #copy.animation_data_clear()
        copy.modifiers.clear()
        copy.constraints.clear()
        return copy

    def deleteHelper(self,mesh):
        objs = bpy.data.objects
        objs.remove(objs[mesh.name], do_unlink=True)
        return
    
    def nullRootY(self,action):
        for fcurve in action.fcurves:
            if fetchBoneFunction(fcurve) == -1 and fcurve.array_index == 1 and "location" in fcurve.data_path.split(".")[-1]:
                for kf in fcurve.keyframe_points:
                    kf.co[1] = 0
                fcurve.update()
    
    def FreeHKProps(self,action,target):
        updateAnimationBoneFunctions(target,action)
        action.freehk.tetherFrame = target
        action.freehk.starType = "LMT_Action"
        action.freehk.frameCount = animationLength(action)
        completeBasis(action)
    
    def enumerateBoneFunctions(self,skeleton):
        bf = {}
        for bone in skeleton.pose.bones:
            if "boneFunction" in bone:
                bf[bone["boneFunction"]] = bone.name
            if "boneFunction" in bone.bone:
                bf[bone.bone["boneFunction"]] = bone.name
        return bf
    
    def mapNames(self,context,source,target):
        bfs = self.enumerateBoneFunctions(source)
        mapper = {}
        for bone in target.pose.bones:
            if "boneFunction" in bone.bone:
                bf = bone.bone["boneFunction"]
                if bf in bfs:
                    mapper[bfs[bf]] = bone.name
        for mesh in context.scene.objects:
            if mesh.type == "MESH":
                for mod in mesh.modifiers:
                    if mod.type == "ARMATURE" and mod.object == source:
                        for group in mesh.vertex_groups:
                            if group.name in mapper:
                                group.name = mapper[group.name]
                        mod.object = target
    
    def generatePlatformMapping(self,mapping):
        trackingMap = {"Ground":self.groundedConstraint,
                        "Translation":self.translationConstraint,
                        "Rotation":self.rotationConstraint,
                        "Transform":self.transformConstraint,
                        }
        constraintMapDict = {}#From true bone function to constraint
        constraintFallthrough = {}#From platform  to substitute
        for boneEntry in mapping:
            function = boneEntry.platformBoneFunction
            target = boneEntry.platformBoneTarget
            tracking = boneEntry.platformTracking
            constraintMapDict[function] = trackingMap[tracking]
            constraintFallthrough[function] = target
        self.constraintMapDict = constraintMapDict
        self.constraintFallthrough = constraintFallthrough
    
    def extractPanelData(self,ctx):
        options = ctx.scene.freehk_rig_ops
        mapping = ctx.scene.freehk_rig_ops_platform.presets[options.rigType].bone_presets
        self.sourceName = options.sourceName
        self.targetName = options.targetName
        self.cat = options.cat
        self.humanoid = options.rigType == "Humanoid"
        self.bake = options.bake
        self.groundRoot = options.groundRoot
        self.platformMapping = self.generatePlatformMapping(mapping)
    
    def execute(self,context):
        self.extractPanelData(context)
        if self.sourceName not in bpy.data.objects:
            return {'FINISHED'}
        if self.targetName not in bpy.data.objects:
            return {'FINISHED'}
        if self.sourceName == self.targetName:
            return {'FINISHED'}
        source = bpy.data.objects[self.sourceName]
        target = bpy.data.objects[self.targetName]
        if not self.source.animation_data or not self.source.animation_data.action:
            return {'FINISHED'}
        if self.cat:
            functionalizeArmature(source)
            applyTransformSkeleton(source,context)  
            muteGlobal(source.animation_data.action)
        copy = self.cloneArmature(source,copyAction = False)
        self.generateOrthogonalizer(copy, target)
        self.addConstraints(source,copy,target)
        if self.bake:
            action = self.bakeOperation(context,source,target)
            self.FreeHKProps(action,target)
            if self.groundRoot:
                self.nullRootY(action) 
            self.deleteHelper(copy)
            self.mapNames(context,source,target)
        return {'FINISHED'}


def boneFunctionFromString(string):
    try:
        return int(string.split(".")[-1])
    except:
        None
    
def functionalizeArmature(target):
    for bone in target.pose.bones:
        bf = boneFunctionFromString(bone.name)
        if bf is not None:
            bone.bone["boneFunction"] = bf
            bone["boneFunction"] = bf

def applyTransform(obj):
    sel_objs = [objs for objs in bpy.context.selected_objects]
    for objs in sel_objs: objs.select = False    
    prev_mode = obj.mode # save
    old_active = bpy.context.scene.objects.active
    #    
    bpy.context.scene.objects.active = obj        
    obj.select = True    
    bpy.ops.object.mode_set(mode='OBJECT')   
    bpy.ops.object.transform_apply( location = True, scale = True, rotation = True)
    #
    bpy.ops.object.mode_set(mode=prev_mode) # restore    
    bpy.context.scene.objects.active = old_active
    obj.select = False
    for objs in sel_objs: obj.select = True
    bpy.context.scene.update()
    
def applyTransformSkeleton(skeleton,context):
    applyTransform(skeleton)
    for mesh in context.scene.objects:
        if mesh.type == "MESH":
            for mod in mesh.modifiers:
                if mod.type == "ARMATURE" and mod.object == source:
                    applyTransform(mod)
                        
class CATBoneFunction(bpy.types.Operator):
    bl_idname = "freehk.cat_bone_function"
    bl_label = "Bone Functions for CAT Rig"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    bl_description = "Assign Bone Functions to CAT rig"
    
    @classmethod
    def poll(cls,context):
        return context.active_object and context.active_object.type == "ARMATURE"
    
    def execute(self,context):
        functionalizeArmature(context.active_object)
        return {"FINISHED"}
    
    
classes = [RigTransferData, PlatformIKMapping, PlatformGroup, PlatformSingleton, RigTransferTools,RigAnimationTransfer,CATBoneFunction]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.freehk_rig_ops = bpy.props.PointerProperty(type=RigTransferData)
    bpy.types.Scene.freehk_rig_ops_platform = bpy.props.PointerProperty(type=PlatformSingleton)
    bpy.app.handlers.scene_update_post.append(onRegister)
    bpy.app.handlers.load_post.append(onFileLoaded)
    
def unregister():
    del bpy.types.Scene.freehk_rig_ops
    del bpy.types.Scene.freehk_rig_ops_platform
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.handlers.load_post.remove(onFileLoaded)

