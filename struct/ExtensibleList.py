# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 17:11:11 2021

@author: AsteriskAmpersand
"""

class ExtensibleList(list):
    def extend(self,*args,**kwargs):
        super().extend(*args,**kwargs)
        return self