import bpy
from bpy.props import *
from . import utils
from .shapeview import isBasisKey

class ShapeKeyPanel (bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
      return utils.ctxHasShapeKeys(context)
      
class DATA_PT_ShapeView(ShapeKeyPanel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Shape View"

    def draw(self, context):
      layout = self.layout
      
      ob = context.object
      mesh = ob.data
      skey = ob.active_shape_key
      shapeview = mesh.shape_keys.shapeview
      
      
      #print(dir(layout))
        
      box = layout.box()
      target = ob.data.shape_keys.shapeview.target
      
      row = layout.row()
      row.prop(context.workspace.shapeview, "active_view3d")
      op = row.operator("screen.select_area")
      
      op.targetPath = "workspaces[\"%s\"].shapeview" % (bpy.context.workspace.name)
      op.targetProp = "active_view3d"
      
      box.label(text="Front Axis Target")
      box.prop(target, "object")
      if target.object:
        if type(target.object.data) == bpy.types.Armature:
          box.prop_search(target, "bone", target.object.data, "bones")
        
        #box.prop(target, "axis")
      
      layout.operator("object.shapeview_create_drivers")
      layout.operator("object.shapeview_create_script")
      
      box = layout.box()
      
      for sv in shapeview.skeys:
        if sv.shapekey == skey.name and not isBasisKey(sv.shapekey, mesh.shape_keys):          
          box.prop(sv, "vector", text=sv.shapekey)
          box.prop(sv, "both_sides")

      layout.operator("object.shapeview_set_view", text="Set View Vector")
      
      """
      layout.label(text="Shape Key: " + skey.name);
      layout.operator("object.shapeview_create_drivers")
      for sv in shapeview.skeys:
        box = layout.box()
        
        if sv.name == "Basis": continue
        
        box.operator("object.shapeview_set_view", text="Set View Vector")
        box.prop(sv, "vector", text=sv.shapekey)
      """
      
from .utils import Registrar

bpy_exports = Registrar([
  DATA_PT_ShapeView
])

