from .utils import Registrar

import bpy
from math import *
from mathutils import *


#START
class ShapeViewKey (bpy.types.PropertyGroup):
    vector     : bpy.props.FloatVectorProperty(size=3)
    shapekey   : bpy.props.StringProperty()
    both_sides : bpy.props.BoolProperty()
 
class ShapeViewTarget (bpy.types.PropertyGroup):
    object : bpy.props.PointerProperty(type=bpy.types.Object, description="Object defining front axis, if unset owning object will be used")
    bone   : bpy.props.StringProperty()
    axis   : bpy.props.EnumProperty(items=[("X", "X", "X", 0), ("Y", "Y", "Y", 1), ("Z", "Z", "Z", 2)])

class ShapeView (bpy.types.PropertyGroup):
    skeys  : bpy.props.CollectionProperty(type=ShapeViewKey)
    target : bpy.props.PointerProperty(type=ShapeViewTarget)
    
def register():
  bpy.utils.register_class(ShapeViewKey)
  bpy.utils.register_class(ShapeViewTarget)
  bpy.utils.register_class(ShapeView)
  bpy.types.Key.shapeview = bpy.props.PointerProperty(type=ShapeView)    
#END

def unregister():
  pass
  
bpy_exports = Registrar([
  [register, unregister]
])

