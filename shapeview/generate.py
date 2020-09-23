import os, sys, os.path

def getStartEnd(buf):
  lines = buf.split("\n")
  out = ""
  started = False
  for l in lines:
    if l.strip() == "#START":
      started = True
    elif l.strip() == "#END":
      started = False
    elif started:
      out += l + "\n"

  return out
  
def generate():
  print("file", __file__) 
  path = os.path.split(__file__)[0]
  path1 = os.path.join(path, "shapeview.py")
  
  file = open(path1, "r")
  buf = file.read()
  file.close()
  
  lines = buf.split("\n");
  
  out = """#VERSION 0.0.1
#WARNING: Auto-generated file, DO NOT EDIT!

import bpy
import bpy
from mathutils import *
from math import *
import bmesh, random, time, os, sys, os.path

class SVGlob:
    def __init__(self):
        self.timergen = 0

    def startTimer(self, timerfunc):
        self.timergen += 1
        
        timergen = [self.timergen]
        def timer():
            if self.timergen != timergen[0]:
                print("Timer stop")
                return None
            timerfunc()
            return 0.1
        
        bpy.app.timers.register(timer)
    
    def stopTimers(self):
      self.timergen += 1

if not hasattr(bpy, "_shapeview_global"):
  bpy._shapeview_global = SVGlob()

svglob = bpy._shapeview_global

"""
  
  
  path2 = os.path.join(path, "props.py")
  file = open(path2, "r")
  buf2 = file.read()

  out += getStartEnd(buf2)
  out += "\nregister()\n"
  
  out += getStartEnd(buf)
  
  out += """
svglob.stopTimers()

def checkViews():
    #print("need update?", needUpdate())
    if needUpdate():
        for ob in bpy.context.visible_objects:
          if ob.mode not in ["OBJECT"] or type(ob.data) != bpy.types.Mesh:
            continue
          if not ob.data.shape_keys or not ob.data.shape_keys.animation_data:
            continue
          
          if len(ob.data.shape_keys.shapeview.skeys) == 0:
            continue
          
          print("updating object. . .", ob.name)
          print("view update detected")
          dgraph = bpy.context.evaluated_depsgraph_get()
          scene = bpy.context.scene
          ob.data.shape_keys.update_tag()
    pass

svglob.startTimer(checkViews)
"""
  return out
  