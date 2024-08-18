# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 06:36:59 2024

@author: Asterisk
"""
from collections import OrderedDict
from pathlib import Path
try:
    from ..common import Cstruct as C
    from ..common import FileLike as FL
    blenderEntry = True
except:
    import sys
    sys.path.append("..")
    from common import Cstruct as C
    from common import FileLike as FL
    blenderEntry = False


class PL(C.PyCStruct):
    fields = OrderedDict([
        ("magic", "byte[4]"),
        ("version", "uint"),
        ("entry_count", "uint"),
    ])
    defaultProperties = {"magic":b"PL\0\0",
                         "version":5610}
    def marshall(self,stream):
        super().marshall(stream)
        self.entries = [PLEntry().marshall(stream) for _ in range(self.entry_count)]
        return self
    
    def construct(self,data):
        if type(data) is list:
            data = {"entries":data}
        data["entry_count"] = len(data["entries"]) if "entries" in data else 0
        super().construct(data)
        self.entries = [PLEntry().construct(entry) for entry in data["entries"]]\
                        if "entries" in data else []
        return self
    def serialize(self):
        return super().serialize() + b''.join(map(lambda x: x.serialize(),self.entries))

    
class PLEntry(C.PyCStruct):
    fields = OrderedDict([
        ("viscon", "uint"),
        ("location", "float[3]")
    ])

PlFile = C.FileClass(PL)