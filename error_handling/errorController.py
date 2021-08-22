# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 06:17:45 2021

@author: AsteriskAmpersand
"""
import bpy
import os
from pathlib import Path
from .errorLists import (error_types,error_map,
                            GRAPH,ACTION,FCURVE,
                            errorTextLevel,errorDisplayLevel)

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

separator = '='*32
#Option to Output error log
class ErrorLevel():
    def __init__(self,level):
        self.level = {"Fix":2,"Ignore":1,"Error":0}[level]
        self.error = True
        self.omit = level in ["Ignore","Fix"]
        self.fix = level == "Fix"

class ErrorEntry():
    def __init__(self,owner,code,lvl,*args):
        self.owner = owner
        self.code = code
        self.type = error_types[code]
        self.typeMap = error_map[code]
        self.description = self.typeMap[code][0]%args
        self.solutions = self.typeMap[code][1]
        self.fix = "" 
        self.level = {GRAPH:lvl.graphError.level,
                      ACTION:lvl.actionError.level,
                      FCURVE:lvl.fcurveError.level}[self.type]
        self.output = print
    def unsolve(self):
        self.level = 0
    def fix(self,fix):
        self.fix = fix
    def __repr__(self):
        lvls = [self.code,self.description,'\n'.join(map(lambda x: "\t\t"+x,self.solutions))]
        joins = ["\n\t", ": ","\n",""]
        rstr = str(self.owner)
        for j,l in zip(lvls[:self.level+1],joins):
            rstr += j+l
        return rstr+"\n"
    def present(self,prev=None,verbose=0,output = None):
        if output is None:
            output = self.output
        qualifier = ["ERROR","WARNING","FIXED"][self.level]
        
        if verbose == 0:
            output("["+qualifier+"] "+'.'.join(filter(lambda x: x,self.owner.tuple()))+" - "+self.code)
            return            
        if verbose == 1:
            output("["+qualifier+"] "+'.'.join(filter(lambda x: x,self.owner.tuple()))+" - "+self.code)
            output("\t"+self.description)
            return
        
        max_depth = 0
        if prev is None:
            mismatchDepth = 0
        else:
            mismatchDepth = self.owner.mismatchDepth(prev)
        for ix,level in enumerate(self.owner.tuple()):
            if level and ix >= mismatchDepth:
                if ix == 0:
                    output("=================================================")
                output("\t"*max(0,ix-1)+level)
                max_depth = ix
                if ix == 0:
                    output("=================================================")
        pref = "\t"*(max_depth)
        poutput = lambda x: output(pref+str(x))
        poutput("["+qualifier+"] "+self.code+":")
        poutput("\t"+self.description)
        for suggestion in self.solutions:
            poutput("\t\t"+suggestion)
        if self.fix:
            poutput("\t Used the following fix: "+self.fix)
        return
                    
    def tuple(self):
        return (*self.owner.tuple(),self.code)
    def __eq__(self,err):
        return self.tuple() == err.tuple()
    def __lt__(self,err):
        return self.tuple() < err.tuple()
    def __hash__(self):
        return hash(self.tuple())

def noneToNull(var):
    return var if var is not None else ""

class errorOwner():
    def __init__(self,metaowner,owner,animowner,fcowner):
        self.meta_owner = Path(metaowner.filepath).stem
        self.owner = self.parseNode(owner) if owner else owner
        self.anim_owner = animowner.name if animowner else animowner
        self.fcowner = fcowner.data_path if fcowner else fcowner
    def parseNode(self,owner):
        x,my = owner.location        
        return "%s (%d,%d)"%(owner.name,x,my)
    def mismatchDepth(self,owner):
        ix = 0
        for ix,(l,r) in enumerate(zip(self.tuple(),owner.tuple())):
            if l != r:
                return ix       
        return ix
    def __repr__(self):
        rstr = ""
        levels = [self.owner,self.anim_owner,self.fcowner]
        titles = ["Node","Animation","FCurve"]
        for lvl,title in zip(levels,titles):
            if lvl is None:
                if not rstr: return rstr
                return rstr[:-1]
            rstr += " "
            rstr += titles + ": " + lvl 
        return rstr[:-1]
    def tuple(self):
        return tuple(map(noneToNull,(self.meta_owner,self.owner,self.anim_owner,self.fcowner)))
    def __lt__(self,owner):
        return self.tuple() < owner.tuple()
    def __eq__(self,owner):
        return self.tuple() == owner.tuple()
     
class ErrorHandler():
    def __init__(self,owner,options = None):
        if options is None:
            options = owner
        self.errorTextLevel = [e[0] for e in errorTextLevel].index(options.error_text_level)
        self.errorDisplayLevel = [e[0] for e in errorDisplayLevel].index(options.error_log_level)
        self.fcurveError = ErrorLevel(options.fcurve_error)
        self.actionError = ErrorLevel(options.action_error)
        self.graphError = ErrorLevel(options.graph_error)
        self.export_owner = owner
        self.owner = None        
        self.anim_owner = None
        self.fcurve_owner = None
        self.valid = True
        self.log = []
        #self.outputFolder 
    def takeOwnership(self,owner):
        self.owner = owner
        self.anim_owner = None
        self.fcurve_owner = None
    def actionOwnership(self,owner):
        self.anim_owner = owner
        self.fcurve_owner = None
    def curveOwnership(self,owner):
        self.fcurve_owner = owner
    def meta_owner(self):
        return errorOwner(self.export_owner,self.owner,self.anim_owner,self.fcurve_owner)
    def append(self,errorEntry):
        error = ErrorEntry(self.meta_owner(),errorEntry[0],self,*errorEntry[1:])
        self.valid = {GRAPH:self.graphError.omit,
                     ACTION:self.actionError.omit,
                     FCURVE:self.fcurveError.omit}[error.type] and self.valid        
        self.log.append(error)
    def logSolution(self,solution):
        self.log[-1].fix = solution
    def logUnsolved(self):
        self[-1].fix("Failed to apply automated solution")
        self[-1].unsolve()
        self.valid = False
    def verifyGraph(self):
        return self.valid
    def verifyAnimations(self):
        return self.valid
    def verifyExport(self):
        return self.valid
    def groupFilterSortErrors(self):
        return list(filter(lambda x: x.level <= self.errorDisplayLevel,sorted(set(self.log))))
    def raiseAlert(self):
        if not self.groupFilterSortErrors():
            ShowMessageBox("No Errors Found - Actions Would Export Succesfully", "No Errors")
        else:
            ShowMessageBox("Potential Errors were found see a list in the Windows Console (Window > Toggle System Console)", "Errors Found", 'ERROR')

    def display(self,output = print):
        grouped = self.groupFilterSortErrors()
        prev = None
        output(separator)
        try:
            output(self.export_owner.name+" - "+os.path.realpath(bpy.path.abspath(self.export_owner.filepath)))
        except:
            output("Export Process Errors")
        output(separator)
        for err in grouped:
            err.present(prev,self.errorTextLevel,output)
            prev = err
        output(separator)
        return bool(grouped)
    def writeLog(self,exportpath,logpath):
        cannonicalPath = os.path.realpath(bpy.path.abspath(logpath))
        exportpath = os.path.realpath(bpy.path.abspath(exportpath))
        outpath = cannonicalPath+'\\'+Path(exportpath).stem+".txt"
        try:
            with open(outpath,"w") as outf:
                output = lambda x: outf.write(str(x)+'\n')
                self.display(output)
            print("Wrote Error Log to file %s"%outpath)
        except:
            print("[LOG ERROR] Log File Location unavailable %s"%outpath)   
        
    def rawprint(self):
        for err in self.log:
            print(err)

class DebugOptions():
    def __init__(self,addonOptions):
        #self.filepath = "Export Verifier"
        self.error_text_level = addonOptions.error_text_level
        self.error_log_level = addonOptions.error_log_level
        self.fcurve_error = addonOptions.fcurve_error
        self.action_error = addonOptions.action_error
        self.graph_error = addonOptions.graph_error

class DebugVerifier(ErrorHandler):
    def __init__(self,options):
        self.filepath = "FreeHK Export Verifier"
        super().__init__(self,DebugOptions(options))
    def display(self,true_output = print):
        #for entry in self.log:
        #    if entry.fix:
        #        entry.fix = "Exporter Action: " + entry.fix
        result = []
        output = result.append
        displayed_errors = super().display(output = output)
        #print('\n'.join(result))
        true_output(('\n'.join(result)).replace("[FIXED]","[FIXABLE]").replace("Used the following fix:","Exporter would use the following fix:"))
        return displayed_errors