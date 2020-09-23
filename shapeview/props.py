from .utils import Registrar

import bpy
from math import *
from mathutils import *


#START
class ShapeViewKey (bpy.types.PropertyGroup):
    vector : bpy.props.FloatVectorProperty(size=3)
    shapekey : bpy.props.StringProperty()
    both_sides = bpy.props.BoolProperty()
 
   
class ShapeView (bpy.types.PropertyGroup):
    skeys : bpy.props.CollectionProperty(type=ShapeViewKey)

def register():
  bpy.utils.register_class(ShapeViewKey)
  bpy.utils.register_class(ShapeView)
  bpy.types.Key.shapeview = bpy.props.PointerProperty(type=ShapeView)    
#END

def unregister():
  pass
  
bpy_exports = Registrar([
  [register, unregister]
])

