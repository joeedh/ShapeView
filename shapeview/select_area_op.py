import bpy
from bpy.props import *

from .utils import Registrar

import bpy
import bgl
import blf
import gpu
from gpu_extras.batch import batch_for_shader

types = {
  "VIEW_3D" : bpy.types.SpaceView3D
}

def draw_callback_px(self, context):
    font_id = 0  # XXX, need to find out how best to get this.

    if context.area == self.active_area:
      # draw some text
      blf.position(font_id, 15, 30, 0)
      blf.size(font_id, 20, 72)
      blf.draw(font_id, "Select Area " + str(self.active_area_i))


class SelectAreaOp(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "screen.select_area"
    bl_label = "Select Area"

    areaType : bpy.props.StringProperty(default="VIEW_3D")
    targetPath : bpy.props.StringProperty()
    targetProp : bpy.props.StringProperty()
    
    _x = None
    _y = None
    
    def find_area(self, screen, x, y):
      i = 0
      
      for area in screen.areas:
        if area.type != self.areaType:
          continue
        if x >= area.x and y >= area.y and x < area.x + area.width and y < area.y + area.height:
          self.active_area = area
          self.active_area_i = i
        i += 1
        
    def modal(self, context, event):
        for area in context.screen.areas:
          if area.type != self.areaType:
            continue
          area.tag_redraw()

        print(dir(event), "event!!")
        if event.type == 'MOUSEMOVE':
            self._x = event.mouse_x
            self._y = event.mouse_y
            self.find_area(context.screen, self._x, self._y)
            
            return {'RUNNING_MODAL'}
        
        elif event.type == 'LEFTMOUSE' or event.type == "RIGHTMOUSE" or event.type == "MIDDLEMOUSE":
            self._x = event.mouse_x
            self._y = event.mouse_y
            self.find_area(context.screen, self._x, self._y)
            
            types[self.areaType].draw_handler_remove(self._handle, 'WINDOW')
            
            obj = bpy.data.path_resolve(self.targetPath)
            setattr(obj, self.targetProp, self.active_area_i)            
            
            #make sure ui redraws
            for area in context.screen.areas:
              area.tag_redraw()
              
            return {'FINISHED'}

        elif event.type in {'ESC'}:
            types[self.areaType].draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
      # the arguments we pass the the callback
      args = (self, context)
      # Add the region OpenGL drawing callback
      # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
      self._handle = types[self.areaType].draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

      self._x = event.mouse_prev_x
      self._y = event.mouse_prev_y

      self.mouse_path = []
      self.active_area = None
      self.active_area_i = 0

      context.window_manager.modal_handler_add(self)
      return {'RUNNING_MODAL'}

bpy_exports = Registrar([
  SelectAreaOp
])
