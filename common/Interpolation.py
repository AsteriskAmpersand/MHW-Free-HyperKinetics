# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 17:17:21 2020

@author: AsteriskAmpersand
"""
from ..common import InterpolationAlgorithms as algo
from math import sqrt,log,acos,exp,cos

def interpolation(lframe,rframe,fraction):
    if lframe.interpolation == "CONSTANT":
        return lframe.value
    if lframe.interpolation == "LINEAR":
        return lframe.value*(1-fraction)+rframe.value*(fraction)
    if lframe.interpolation == "BEZIER":
        return bezier(lframe,rframe,fraction)
    if lframe.interpolation == "CUADRATIC":
        classBase = eval("algo.Quad"+easeType(lframe))
    if lframe.interpolation == "CUBIC":
        classBase = eval("algo.Cubic"+easeType(lframe))         
    if lframe.interpolation == "QUART":
        classBase = eval("algo.Quartic"+easeType(lframe))         
    if lframe.interpolation == "QUINT":
        classBase = eval("algo.Quintic"+easeType(lframe))
    if lframe.interpolation == "EXPO":
        classBase = eval("algo.Exponential"+easeType(lframe))         
    if lframe.interpolation == "SINE":
        classBase = eval("algo.Sine"+easeType(lframe))
    if lframe.interpolation == "CIRC":
        classBase = eval("algo.Circular"+easeType(lframe))
    if lframe.interpolation == "BACK":
        classBase = eval("algo.Back"+easeType(lframe))
    if lframe.interpolation == "BOUNCE":
        classBase = eval("algo.Bounce"+easeType(lframe))
    if lframe.interpolation == "ELASTIC":
        classBase = eval("algo.Elastic"+easeType(lframe))
    return classBase(start = lframe.value,end = rframe.value).ease(fraction)

FLT_EPSILON = 1.19209290E-07
SMALL = -1.0e-10

def bezier(l,r,ti):
    x0 = l.index
    x3 = r.index
    y0 =  l.value
    x1,y1 = l.handle_right
    x2,y2 = r.handle_left
    y3 = r.value
    v1 = [x0,y0]
    v2 = [x1,y1]
    v3 = [x2,y2]
    v4 = [x3,y3]
    if (abs(v1[1] - v4[1]) < FLT_EPSILON and abs(v2[1] - v3[1]) < FLT_EPSILON and
        abs(v3[1] - v4[1]) < FLT_EPSILON):
        # Optimization: If all the handles are flat/at the same values,
        # the value is simply the shared value
        return v1[1]
    correct_bezpart(v1,v2,v3,v4)   
    bf = lambda v0,v1,v2,v3: (lambda t: (1-t)**3*v0 + 3*(1-t)**2*t*v1+3*(1-t)*t**2*v2+t**3*v3)
    bi= lambda i: (lambda v0,v1,v2,v3: bf(*map(lambda x: x[i],[v0,v1,v2,v3])))
    bx = bi(0)
    by = bi(1)
    b = lambda v0,v1,v2,v3: (lambda t: (bx(v0,v1,v2,v3)(t),by(v0,v1,v2,v3)(t)))
    f = b(v1,v2,v3,v4)
    eps = 1/(2*(x3-x1))
    x = (1-ti)*x0 + ti*x3
    return f(binary_search(lambda t: f(t)[0],x,eps))[1]
    
def binary_search(function,x,eps):
    l = 0
    r = 1
    while (r-l>eps):
        mid = (l+r)/2
        val = function(mid)
        if val > x:
            r = mid
        else:
            l = mid
    return l
            
    
def correct_bezpart(v1,v2,v3,v4):
    h1 = [0,0]
    h2 = [0,0]
    #Calculate handle deltas
    h1[0] = v1[0] - v2[0]
    h1[1] = v1[1] - v2[1]
    h2[0] = v4[0] - v3[0]
    h2[1] = v4[1] - v3[1]
    # Calculate distances:
    # len  = span of time between keyframes
    # len1 = length of handle of start key
    # len2 = length of handle of end key
    len0 = v4[0] - v1[0]
    len1 = abs(h1[0])
    len2 = abs(h2[0])
    # If the handles have no length, no need to do any corrections. */
    if ((len1 + len2) == 0.0): return    
    # To prevent looping or rewinding, handles cannot
    # exceed the adjacent key-frames time position. */
    if (len1 > len0):
      fac = len0 / len1
      v2[0] = (v1[0] - fac * h1[0])
      v2[1] = (v1[1] - fac * h1[1])    
    if (len2 > len0):
      fac = len0 / len2
      v3[0] = (v4[0] - fac * h2[0])
      v3[1] = (v4[1] - fac * h2[1])

def sqrt3d(d):
    if(d==0.0): return 0
    if(d<0): return -exp(log(-d)/3)
    else: return exp(log(d)/3)

def find_zero(x,q0,q1,q2,q3,q4,o):
  nr = 0
  c0 = q0 - x
  c1 = 3.0 * (q1 - q0)
  c2 = 3.0 * (q0 - 2.0 * q1 + q2)
  c3 = q3 - q0 + 3.0 * (q1 - q2)
  if (c3 != 0.0):
    a = c2 / c3
    b = c1 / c3
    c = c0 / c3
    a = a / 3
    p = b / 3 - a * a
    q = (2 * a * a * a - a * b + c) / 2
    d = q * q + p * p * p
    if (d > 0.0):
      t = sqrt(d)
      o[0] = (sqrt3d(-q + t) + sqrt3d(-q - t) - a)
      if ((o[0] >= SMALL) and (o[0] <= 1.000001)):
        return 1
      return 0
    if (d == 0.0):
      t = sqrt3d(-q);
      o[0] = (2 * t - a)
      if ((o[0] >= SMALL) and (o[0] <= 1.000001)):
        nr+=1
      o[nr] = (-t - a);
      if ((o[nr] >= SMALL) and (o[nr] <= 1.000001)):
        return nr + 1
      return nr;
    phi = acos(-q / sqrt(-(p * p * p)));
    t = sqrt(-p);
    p = cos(phi / 3);
    q = sqrt(3 - 3 * p * p)
    o[0] = (2 * t * p - a)
    if ((o[0] >= SMALL) and (o[0] <= 1.000001)):
      nr+=1
    o[nr] = (-t * (p + q) - a)
    if ((o[nr] >= SMALL) and (o[nr] <= 1.000001)) :
      nr+=1
    o[nr] = (-t * (p - q) - a);
    if ((o[nr] >= SMALL) and (o[nr] <= 1.000001)):
      return nr + 1
    return nr
  a = c2
  b = c1
  c = c0
  if (a != 0.0):
    # discriminant */
    p = b * b - 4 * a * c
    if (p > 0):
      p = sqrt(p)
      o[0] = ((-b - p) / (2 * a))

      if ((o[0] >= SMALL) and (o[0] <= 1.000001)):
        nr+=1
      o[nr] = ((-b + p) / (2 * a))
      if ((o[nr] >= SMALL) and (o[nr] <= 1.000001)):
        return nr + 1
      return nr
    if (p == 0):
      o[0] = (-b / (2 * a));
      if ((o[0] >= SMALL) and (o[0] <= 1.000001)):
        return 1
    return 0
  if (b != 0.0):
    o[0] = (-c / b)
    if ((o[0] >= SMALL) and (o[0] <= 1.000001)):
      return 1
    return 0
  if (c == 0.0):
    o[0] = 0.0
    return 1
  return 0

    
def easeType(frame):
    if frame.easing == "AUTO":
        return "EaseInOut"
    if frame.easing == "EASE_IN":
        return "EaseIn"
    if frame.easing == "EASE_OUT":
        return "EaseOut"
    if frame.easing == "EASE_IN_OUT":
        return "EaseInOut"