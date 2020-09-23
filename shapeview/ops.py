import bpy 
from mathutils import *
from math import *
import bmesh
      
from .utils import Registrar, ctxHasShapeKeys
from .shapeview import setView, createDrivers

import bpy

class CreateDriversOp(bpy.types.Operator):
    """Set view vector from active viewport camera"""
    bl_idname = "object.shapeview_create_drivers"
    bl_label = "Create Drivers"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return ctxHasShapeKeys(context)

    def execute(self, context):
        ob = context.object
        print("Making drivers")
        
        createDrivers(ob)
        
        return {'FINISHED'}


class SetViewVectorOp(bpy.types.Operator):
    """Set view vector from active viewport camera"""
    bl_idname = "object.shapeview_set_view"
    bl_label = "Set View"
    bl_options = {'UNDO'}

    both_sides : bpy.props.BoolProperty()
    
    @classmethod
    def poll(cls, context):
        return ctxHasShapeKeys(context)

    def execute(self, context):
        ob = context.object
        setView(ob, self.both_sides)
        
        return {'FINISHED'}

class CreateEmbeddedScript(bpy.types.Operator):
    """Create embedded script to run rig without addon"""
    bl_idname = "object.shapeview_create_script"
    bl_label = "Create Script"
    bl_options = {'UNDO'}

    both_sides : bpy.props.BoolProperty()
    
    @classmethod
    def poll(cls, context):
        return ctxHasShapeKeys(context)

    def execute(self, context):
        ob = context.object
        setView(ob, self.both_sides)
        from . import generate
        
        buf = generate.generate()
        name = "shapeview_run.py"
        
        if name not in bpy.data.texts:
          bpy.data.texts.new(name)
        
        text = bpy.data.texts[name];
        text.clear()
        text.write(buf)
        text.use_module = True
        text.as_module() #run
        
        return {'FINISHED'}

bpy_exports = Registrar([
  SetViewVectorOp,
  CreateDriversOp,
  CreateEmbeddedScript
])

