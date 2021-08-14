# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 00:06:50 2021

@author: AsteriskAmpersand
"""
import bpy

def clearScene():
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)
    for tree in bpy.data.node_groups:
        if tree.bl_idname == 'FreeHKNodeTree':
            bpy.data.node_groups.remove(tree)

GRID = 20.0

LMTACTION = 'LMTActionNode'
TIMLACTION = 'TIMLActionNode'
ACTIONS = [LMTACTION,TIMLACTION]
ACTIONSIZE = GRID*5

TIMLDATA = 'TIMLDataNode'
DATA = [TIMLDATA]
DATASIZE = GRID*14

LMTENTRY = 'LMTEntryNode'
LMTSIZE = GRID*15
EFXENTRY = 'EFXEntryNode'
TIMLENTRY = 'TIMLEntryNode'
LIGHTENTRY = [EFXENTRY,TIMLENTRY]
ENTRYSIZE = GRID*7

LMTFILE = 'LMTFileNode'
EFXFILE = 'EFXFileNode'
TIMLFILE = 'TIMLFileNode'
FILE = [LMTFILE,EFXFILE,TIMLFILE]
FILESIZE = GRID*6

HORIZONTAL = GRID*15

HIDE = GRID*1.5

SIZEMAP = {**{f:FILESIZE for f in FILE},
           **{f:ENTRYSIZE for f in LIGHTENTRY},
           LMTENTRY:LMTSIZE,
           TIMLDATA:DATASIZE,
           **{f:ACTIONSIZE for f in ACTIONS},
           }

TYPEINDEX = {**{f:3 for f in FILE},
           **{f:2 for f in LIGHTENTRY},
           LMTENTRY:1,
           TIMLDATA:1,
           **{f:0 for f in ACTIONS},
           }

def flagBreak(intVal):
    return [bool((intVal>>(7-i))&1) for i in range(8)]

#.location
class uiNodeManager():
    def __init__(self,tree,hide = False):
        #action,data,entry,output
        self.nodeCoords = [0,0,0,0]
        for node in tree.nodes:
            ntype = node.bl_idname 
            ix = TYPEINDEX[ntype]
            self.nodeCoords[ix] = max(self.nodeCoords[ix],node.location[1]+SIZEMAP[ntype])
        mx = max(self.nodeCoords)+2*GRID
        self.nodeCoords = [mx,mx,mx,mx]
        self.tree = tree
        self.hide = hide
    def updateAbove(self,index):
        for ix in range(index+1,4):
            self.nodeCoords[ix] = max(self.nodeCoords[index],self.nodeCoords[ix])
    def updateBelow(self,index):
        mx = max(self.nodeCoords[0:index+1])
        for ix in range(0,index+1):
            self.nodeCoords[ix] = mx
    def pad(self,amount):
        self.nodeCoords = list(map(lambda x: x+amount,self.nodeCoords))
    def createActionNode(self,action=None,outputs=[],outputSocket="TIML Animation",nodeType = TIMLACTION):
        self.updateBelow(0)
        node = self.tree.nodes.new(nodeType)
        node.input_action = action
        for outx in outputs:
            self.tree.links.new(node.outputs[outputSocket],outx.inputs[outputSocket])
        node.location = (0*HORIZONTAL,-self.nodeCoords[0])
        self.nodeCoords[0] += ACTIONSIZE if not self.hide else HIDE
        if self.hide: node.hide = True
        self.updateAbove(0)
        return node
    def createTIMLActionNode(self,action=None,inputs = None, outputs = []):
        return self.createActionNode(action,outputs,"TIML Animation",nodeType=TIMLACTION)
    def createLMTActionNode(self,action=None,inputs = None, outputs = []):
        return self.createActionNode(action,outputs,"LMT Animation",nodeType=LMTACTION)
    def createTIMLDataNode(self,data,inputs = [], outputs = []):
        self.updateBelow(1)
        node = self.tree.nodes.new(TIMLDATA)
        node.name = "TIML Data Node"
        node.unkn1 = data.dataIx0
        node.unkn2 = data.dataIx1
        node.animLength = data.animationLength
        node.loopStartPoint = data.loopStartPoint
        node.loopControl = str(data.loopControl)
        for inpx in inputs:
            self.tree.links.new(inpx.outputs["TIML Animation"],node.inputs["TIML Animation"])
        for outx in outputs:
            self.tree.links.new(node.outputs["TIML Data"],outx.inputs["TIML Data"])
        node.location = (1*HORIZONTAL,-self.nodeCoords[1])
        self.nodeCoords[1] += DATASIZE if not self.hide else HIDE
        if self.hide: node.hide = True
        self.updateAbove(1)
        return node
    def createEntryNode(self,i=0,inputs = [], outputs = [],outputType = "TIML Entry",nodeType = TIMLENTRY):
        self.updateBelow(2)
        node = self.tree.nodes.new(nodeType) 
        node.entryNum = i
        for inpx in inputs:
            self.tree.links.new(inpx.outputs["TIML Data"],node.inputs["TIML Data"])
        for outx in outputs:
            self.tree.links.new(node.outputs[outputType],outx.inputs[outputType])
        node.location = (2*HORIZONTAL,-self.nodeCoords[2])
        if not self.hide:
            self.nodeCoords[2] += ENTRYSIZE if nodeType != LMTENTRY else LMTSIZE
        else:
            self.nodeCoords[2] += HIDE
        if self.hide: node.hide = True
        self.updateAbove(2)
        return node
    def createTIMLEntryNode(self,i=0,inputs = None, outputs = []):
        return self.createEntryNode(i,[inputs] if inputs else [],outputs,"TIML Entry",TIMLENTRY)
    def createEFXEntryNode(self,i=0,inputs = [], outputs = []):
        return self.createEntryNode(i,inputs,outputs,"EFX Entry",EFXENTRY)
    def createLMTEntryNode(self,entry,inputs = {}, outputs = []):
        tinputs = [inputs["TIML Data"]] if "TIML Data" in inputs else []
        i = entry.id
        node = self.createEntryNode(i,tinputs,outputs,"LMT Entry",LMTENTRY)
        #load the data node stuff here
        #node.frameCount = entry.frameCount
        node.loopFrame = entry.loopFrame
        #node.transVec = entry.Vec0
        #node.quatVec = entry.Vec2
        node.byteflag = flagBreak(entry.Flags)
        node.byteflag2 = flagBreak(entry.Flags2)
        
        if "LMT Animation" in inputs:
            self.tree.links.new(inputs["LMT Animation"].outputs["LMT Animation"],node.inputs["LMT Animation"])
        return node
    def createOutputNode(self,path="",inputs = [], outputs = None, inputType = "TIML Entry",nodeType = TIMLFILE):
        if self.hide: self.pad(GRID)
        self.updateBelow(3)
        node = self.tree.nodes.new(nodeType)
        node.filepath = path
        for inpx in inputs:
            self.tree.links.new(inpx.outputs[inputType],node.inputs[inputType])
        node.location = (3*HORIZONTAL,-self.nodeCoords[3])
        self.nodeCoords[3] += FILESIZE if not self.hide else HIDE
        if self.hide: node.hide = True
        self.updateAbove(3)
        return node
    def createTIMLOutputNode(self,path="",inputs = [], outputs = None):
        return self.createOutputNode(path,inputs,outputs,"TIML Entry",TIMLFILE)
    def createEFXOutputNode(self,path="",inputs = [], outputs = None):
        return self.createOutputNode(path,inputs,outputs,"EFX Entry",EFXFILE)
    def createLMTOutputNode(self,path="",inputs = [], outputs = None):
        return self.createOutputNode(path,inputs,outputs,"LMT Entry",LMTFILE)
    def connect(self,lnode,rnode,socket):
        self.tree.links.new(lnode.outputs[socket],rnode.inputs[socket])
    
def getCurrentTree(hide = False):
    current_tree = None
    for tree in bpy.data.node_groups:
        if tree.bl_idname == 'FreeHKNodeTree':
            current_tree = tree
            break
    if current_tree is None:
        current_tree = getNewTree()
    return uiNodeManager(current_tree,hide)

def getNewTree(name = "Free HK Tree", hide = False):
    return uiNodeManager(bpy.data.node_groups.new(name,"FreeHKNodeTree"),hide)
        