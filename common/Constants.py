# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 19:17:04 2020

@author: AsteriskAmpersand
"""

UNKN = -1
ROT_E = 0
POS = 1
SCL = 3
ROT_Q = 4

transform_map = {"rotation_quaternion":ROT_Q,
                 "rotation_euler":ROT_E,
                 "scale":SCL,
                 "location":POS,
                 "unknown":UNKN}
inverse_transform = {transform_map[k]:k for k in transform_map}