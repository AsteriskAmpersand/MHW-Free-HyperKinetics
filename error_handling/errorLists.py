# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 16:46:39 2021

@author: AsteriskAmpersand
"""

def intiter():
    i = 0
    while(True):
        yield i
        i+=1
#
idGen = intiter()

GRAPH = 0
ACTION = 1
FCURVE = 2    
FILE = 3
    
from ..ui.HKIcons import pcoll

errorItems = [("Error","Stop and Report","Stop on errors and report them, halting the export process",pcoll["FREEHK_ERR_ERROR"].icon_id,0),
              ("Ignore","Omit","Continue the export proceess omitting entries with errors",pcoll["FREEHK_ERR_OMIT"].icon_id,1),
              ("Fix","Fix","Attempt to correct the errors, omit if unfixable",pcoll["FREEHK_ERR_FIX"].icon_id,2)]
errorTextLevel = [("Abbreviation","Error Code","Reports only the error code",pcoll["FREEHK_ERR_ERROR"].icon_id,0),
              ("Short","Short Description","Report each error",pcoll["FREEHK_ERR_OMIT"].icon_id,1),
              ("Verbose","Description and Solution","Report each error and suggest possible fixes",pcoll["FREEHK_ERR_FIX"].icon_id,2),
              ]
errorDisplayLevel = [("Error","Errors Only","Displays only Export Stopping Errors",pcoll["FREEHK_ERR_ERROR"].icon_id,0),
                     ("Warnings","Errors and Warnings","Displays errors, omitted segments and potentially problematic situations",pcoll["FREEHK_ERR_OMIT"].icon_id,1),
                     ("All","All","Displays errors, omitted segments, problematic situations and cases where the exporter attempted a fix and its outcome",pcoll["FREEHK_ERR_FIX"].icon_id,2)]

graphErrors = {"G_LOW_ENTRY_COUNT":("Output Node %s has lower Entry Count than maximum Entry ID (ID:%d)",
                                ["Multiple Posssible Solutions:",
                                 "-Increase Entry Count on the Output Node",
                                 "-Change Entry ID to be on the range of the Entry Count",
                                 "-Set Entry Count on Output Node to -1 for it to automatically be set to the max id on it's Entries (Not Recommended on LMTs or EFXs)"] ),
               "G_REPEATED_ID":("Multiple Entry Nodes %s have the same Entry ID %d",
                            ["Multiple Posssible Solutions:",
                             "-Change the Entry ID on each entry node to be different",
                             "-Set them to -1 for autonumbering (Not Recommended on LMTs or EFXs)"] ),
               "G_INJECTION_ENTRY_COUNT":("Output Node %s has higher Entry Count than File has injection positions (%d)",
                                ["Reduce the number of entries or their ids so they fit on the existing injections spots",
                                 ] ),               
               "G_INPUT_TYPE_MISMATCH":("Node %s expected inputs of type %s but instead has input %s of type %s",
                                        ["Disconnect incorrectly matched nodes",
                                         "Nodes list the type of connection they expect and also the type of connection they output."
                                         "Ensure the recieving end type matches the source's type."
                                         ])   
               }

fileErrors = {"G_MASTER_FILE_ERROR":("Output Node's %s Injection Target File %s is invalid",
                                  ["Select a valid injection target"])   
               }

actionErrors = {"A_LMT_FRAME_COUNT_LOW":("Animation %s has fcurves with frames going beyond the animation's frame count",
                                         ["Multiple Possible Solutions:",
                                          "-Set Animation Frame Count to the position of the last keyframe",
                                          "-Remove keyframes after the Animation's Frame Count",
                                          "-Set Animation Frame Count to -1 for it to be automatically calculated"]),
                "A_LMT_INVALID_ACTION_TYPE":("Action %s is not an LMT Action",
                                                  ["Manually set the action to LMT Type on the Action Data Sidebar on the Action Editor"]),
                "A_TIML_INVALID_ACTION_TYPE":("Action %s is not a TIML Action",
                                                  ["Manually set the action to TIML Type on the Action Data Sidebar on the Action Editor"]),
                }

fcurveErrors = {"F_LMT_DUPLICATE_FCURVE":("FCurve %s in Animation %s occurs more than once",
                                               ["FCurve's targets (Bone + Transform + Axis) must be unique",
                                                "Delete the repeated fcurves"]),
                "F_LMT_INVALID_ENCODING_TYPE":("FCurve %s in Animation %s has illegal type %d",
                                               ["FCurve Type must be a value in (0-7) or (11 to 15)",
                                                "Specify a legal value or set it to 0 for automatic detection"]),
                "F_LMT_INVALID_ENCODING_NONROT":("FCurve %s in Animation %s has type %d which is reserved for rotations",
                                               ["Quaternion interpolation types and keys cannot be used with translations or scale",
                                                "Change the transform encoding type to 0 for auto-detection or one of the non-quaternion types"]),                
                "F_LMT_INVALID_ENCODING_ROT":("FCurve %s in Animation %s has type %d which is reserved for non-rotations",
                                               ["Translation and Scale Interpolation types and keys cannot be used with translations or scale",
                                                "Change the transform encoding type to 0 for auto-detection or one of the quaternion types"]),
                "F_LMT_INVALID_ENCODING_KEY":("FCurve %s in Animation %s has type %d which is reserved for non-keys",
                                               ["Key Types (1 and 2 VectorBase and VectorRotationBase respectively) are reserved for keyframeless data",
                                                "Change the transform encoding type to 0 for auto-detection or one of the non-key types"]),
                "F_LMT_INVALID_ENCODING_NONKEY":("FCurve %s in Animation %s has type %d which is reserved for keys",
                                               ["Key Types (1 and 2 VectorBase and VectorRotationBase respectively) are reserved for keyframeless data",
                                                "Change the transform encoding type to 0 for auto-detection or one of the key types"]),                
                "F_LMT_CONFLICTING_ENCODING_TYPE":("Transform %s in Animation %s has mismatched Encoding Types",
                                               ["FCurve Type must match between curves of the same transform",
                                                "Match the Type between all of the curves on the same transform or set all except one to 0 (or all of them)"]),
                "F_LMT_INVALID_BONE_FUNCTION":("FCurve %s in Animation %s has illegal bone function %d",
                                               ["Bone Functions must be -2 for autodetect from armature, -1 for the root or a positive integer number",
                                                "Set the Bone Function for the FCurve to -2, -1 (if the root) or a positive integer",
                                                "Or delete the fcurve"]),
                "F_LMT_MISSING_BONE_FUNCTION":("Transform %s in Animation %s has no Bone Functions and neither does its armature",
                                               ["FCurves must have either an explicit bone function or have a tether with a relevant bone to autodetect",
                                                "You can set the bone function to -2 for all members but one for auto-detect on those",
                                                "You can set the boen function to -2 for all members so they use the skeleton's bone function",
                                                "You can also use 'Update Bone Functions' button to sync Bone Functions to the Tether bones"]),
                "F_LMT_CONFLICTING_BONE_FUNCTION":("Transform %s in Animation %s has mismatched Bone Functions",
                                               ["Bone Functions must match between members of the same transform",
                                                "You can set the bone function to -2 for all members but one for auto-detect on those",
                                                "You can set the boen function to -2 for all members so they use the skeleton's bone function",
                                                "You can also use 'Update Bone Functions' button to sync Bone Functions to the Tether bones"]),
                "F_LMT_NAME_FUNCTION_CONFLICT":("Transform %s in Animation %s Bone Function does not match the Bone it Animates",
                                               ["The bone function in the fcurve data does not match that of the bone it animates",
                                                "on the tethered skeleton attached to this animation.",
                                                "You can use the 'Update Bone Functions' button to sync Bone Functions to the Tether bones"]),
                "F_LMT_FUNCTION_MISSING":("Transform %s in Animation %s lacks sufficient data to reconstruct a Bone Function",
                                               ["The transform has no bone with an explicit bone function",
                                                "additionally the skeleton doesn't have a matching bone or doesn't have a bone function in said bone",
                                                "You must 'Add FreeHK Props' if needed and manually set the bone function for the relevant fcurves"]),
                "F_LMT_UNCUSTOMIZED_FCURVE":("FCurve %s in Animation %s is uncustomized",
                                             ["FCurves need to be customized to be exportable.",
                                              "In the Action Editor click on the FCurve and the 'Add FreeHK Props' button"]),
                "F_LMT_MISSING_CHANNEL":("Transform %s in Animation %s is missing a transform channel",
                                             ["Click the 'Complete Channels' button on the relevant action",
                                              "Or manually add an FCurve for the missing axis of the transform",
                                              "LMTs require an FCurve for each axis for each transform"]),
                "F_LMT_EMPTY_FCURVE":("Transform %s in Animation %s is devoid of keyframes",
                                             ["Delete the fcurve or add keyframes to it"]),
                "F_LMT_UNSYNCHRONIZED_KEYFRAMES":("Transform %s in Animation %s has unsynchronized frames",
                                                  ["Click the 'Synchronize Keyframes' button on the relevant action",
                                                   "Alternatively manually add a keyframe to the relevant fcurves so they match others in the same transform",
                                                   "The keyframes on each axis of an LMT transform must be on the same frames",
                                                   "If there's missing channels this error will show up because the missing channels are coonsidered to have 0 keyframes"]),
                "F_LMT_MISSING_REFERENCE_FRAME":("FCurve %s in Animation %s is missing its reference frame",
                                                 ["FCurve's frame 0 is used as the LMT Reference Frame",
                                                  "Add a keyframe at frame 0 as the LMT Reference Frame"]),
                "F_LMT_MISSING_FIRST_FRAME":("FCurve %s in Animation %s is missing its start frame",
                                                 ["FCurve's frame 1 is used as the starting point of the animation",
                                                  "Add a keyframe at frame 1 as the FCurve Starting Frame"]),
                "F_LMT_MISSING_LAST_FRAME":("FCurve %s in Animation %s is missing its last frame",
                                                 ["FCurve's frame at the frame count is used as the end point of the animation",
                                                  "Add a keyframe at the last frame as the FCurve End Frame"]),
                "F_LMT_MISSING_BASIS_FRAME":("FCurve %s in Animation %s is a Root transform and is missing its frame past the last",
                                                 ["For the Root Transforms, the frame at one past the frame count is used as the basis of blending to the next animation",
                                                  "Add a keyframe one past the last frame for Root Transforms"]),
                "F_LMT_UNEXPORTABLE_PROPERTY":("FCurve %s in Animation %s is not an LMT Animatable Transform",
                                               ["LMT Actions can only contain geometrical transformations",
                                                "Delete FCurves corresponding to non-geometrical properties",
                                                "Geometrical Properties are any of the following: Euler Rotation, Quaternion Rotation, Translation and Scale"]),
                "F_LMT_UNINVERSIBLE_MATRIX":("FCurve %s in Animation %s is tied to Bone %s in Armature %s which has non-inversible transformation",
                                             ["The bone has been transformed in such a way that it cannot be transformed back to a default bone",
                                              "This is normally caused by the scale of a bone being set to 0. Set the bone dimensions to a value with non 0 size.",
                                              "Uninversible matrices clash with the tether system which requires coordinate changes because of Blender Limitations"]),
                "F_TIML_CLASS_CONFLICT":("Property %s in Animation %s conflicts with the class Timeline Type",
                                         ["Not all Timeline types support all property types",
                                          "Using a unexpected property type on the wrong Timeline Type might result in improper behaviour"]), 
                "F_TIML_MISSING_CHANNEL":("RGBA Transform %s in Animation %s is missing channels",
                                             ["Manually add an FCurve for the missing axis of the transform",
                                              "TIML RGBA Transforms must have one fcurvel per colour and one for Alpha"]),
                "F_TIML_UNSYNCHRONIZED_KEYFRAMES":("RGB Transform %s in Animation %s has unsynchronized frames",
                                                  ["Manually add a keyframe to the relevant fcurves so they match others in the same transform",
                                                   "The keyframes on each axis of a TIML RGBA transform must be on the same frames"]),
                "F_TIML_INVALID_PROPERTY":("FCurve %s in Animation %s is not a valid TIML Property",
                                             ["Delete the offending curve."])
                }

keyframeErrors = {
                "K_TIML_INVALID_INTERPOLATION":("Keyframes on FCurve %s on Animation %s has invalid interpolation type %s",
                                                ["TIML Keyframe interpolation must be of one of the following types",
                                                 "CONSTANT,LINEAR,QUAD,CUBIC,QUART,EXPO,SINE",
                                                 "Change the keyframe's interpolation type to one of the above"]),
                "K_TIML_INVALID_CONTROL_VALUE_SINT":("Keyframes on FCurve %s on Animation %s have an illegal control value for it's property type INT",
                                                ["Some property types do not admit all control values",
                                                 "This property only allows 0 on its control parameters"]),
                "K_TIML_INVALID_CONTROL_VALUE_UINT":("Keyframes on FCurve %s on Animation %s have an illegal control value for it's property type UINT",
                                                ["Some property types do not admit all control values",
                                                 "This property expects an Integer Value on the first parameter",
                                                 "and only 0 on the second parameter"]),
                "K_TIML_INVALID_CONTROL_VALUE_BOOL":("Keyframes on FCurve %s on Animation %s have an illegal control value for it's property type BOOL",
                                                ["Some property types do not admit all control values",
                                                 "This property only allows 0 on its control parameters"]),
                }

def mapCheck(key):
    if key in fileErrors:
        return fileErrors
    if key in graphErrors:
        return graphErrors
    if key in actionErrors:
        return actionErrors
    if key in fcurveErrors:
        return fcurveErrors
    if key in keyframeErrors:
        return keyframeErrors
    
def typeCheck(key):
    if key in fileErrors:
        return FILE
    if key in graphErrors:
        return GRAPH
    if key in actionErrors:
        return ACTION
    if key in fcurveErrors:
        return FCURVE
    if key in keyframeErrors:
        return FCURVE
    
error_map = {key:mapCheck(key) for key in sum(map(lambda x: list(x.keys()), [graphErrors, fileErrors, actionErrors, fcurveErrors, keyframeErrors]),[])}
error_types = {key:typeCheck(key) for key in sum(map(lambda x: list(x.keys()), [graphErrors, fileErrors, actionErrors, fcurveErrors, keyframeErrors]),[])}


#for key in sum(map(lambda x: list(x.keys()), [graphErrors, actionErrors, fcurveErrors, keyframeErrors]),[]):
#    print("#",key)
# G_LOW_ENTRY_COUNT
# G_REPEATED_ID
# G_EFX_HIGH_ENTRY_COUNT
# G_INPUT_TYPE_MISMATCH
# A_LMT_FRAME_COUNT_LOW
# A_LMT_FRAME_COUNT_HIGH
# A_LMT_ASYMMETRIC_FOLD
# A_LMT_DYNAMIC_FRAME_COUNT_FOLD
# A_LMT_INVALID_ACTION_TYPE
# A_TIML_INVALID_ACTION_TYPE
# F_LMT_DUPLICATE_FCURVE
# F_LMT_INVALID_ENCODING_TYPE
# F_LMT_INVALID_ENCODING_NONROT
# F_LMT_INVALID_ENCODING_ROT
# F_LMT_INVALID_ENCODING_KEY
# F_LMT_INVALID_ENCODING_NONKEY
# F_LMT_CONFLICTING_ENCODING_TYPE
# F_LMT_INVALID_BONE_FUNCTION
# F_LMT_CONFLICTING_BONE_FUNCTION
# F_LMT_NAME_FUNCTION_CONFLICT
# F_LMT_FUNCTION_MISSING
# F_LMT_UNCUSTOMIZED_FCURVE
# F_LMT_MISSING_CHANNEL
# F_LMT_EMPTY_FCURVE
# F_LMT_UNSYNCHRONIZED_KEYFRAMES
# F_LMT_MISSING_REFERENCE_FRAME
# F_LMT_MISSING_FIRST_FRAME
# F_LMT_MISSING_LAST_FRAME
# F_LMT_MISSING_BASIS_FRAME
# F_LMT_UNEXPORTABLE_PROPERTY
# F_LMT_UNINVERSIBLE_MATRIX
# F_TIML_CLASS_CONFLICT
# F_TIML_MISSING_CHANNEL
# F_TIML_UNSYNCHRONIZED_KEYFRAMES
# F_TIML_INVALID_PROPERTY
# K_TIML_INVALID_INTERPOLATION
# K_TIML_INVALID_CONTROL_VALUE_SINT
# K_TIML_INVALID_CONTROL_VALUE_UINT
# K_TIML_INVALID_CONTROL_VALUE_BOOL