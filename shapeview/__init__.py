bl_info = {
    "name": "Shape View",
    "author": "Joseph Eagar",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "Properties > Object > GearGen",
    "description": "Generate rig to change shapekeys based on camera viewpoint",
    "warning": "",
    "wiki_url": "",
    "category": "Rigging",
    }

import bpy

from . import Global, ops, props, spline, ui, utils, shapeview, timer, generate
from . import select_area_op

import imp

imp.reload(utils)
imp.reload(spline)
imp.reload(props)
imp.reload(shapeview)
imp.reload(generate)
imp.reload(ops)
imp.reload(ui)
imp.reload(timer)
imp.reload(select_area_op)

bpy_exports = utils.Registrar([
  props.bpy_exports,
  ops.bpy_exports,
  ui.bpy_exports,
  shapeview.bpy_exports,
  select_area_op.bpy_exports
])

def render_pre(a, b):
  Global.is_rendering = True
  
def render_post(a, b):
  Global.is_rendering = False
  
def register():
  from . import timer
  #timer.start()
  bpy_exports.register()
  
  bpy.app.handlers.render_init.append(render_pre)
  bpy.app.handlers.render_pre.append(render_pre)
  bpy.app.handlers.render_post.append(render_post)
  bpy.app.handlers.render_cancel.append(render_post)
  bpy.app.handlers.render_complete.append(render_post)
  
def unregister():
  from . import timer
  #timer.stop()
  
  if bpy_exports.registered:
    bpy.app.handlers.render_init.remove(render_pre)
    bpy.app.handlers.render_pre.remove(render_pre)
    bpy.app.handlers.render_post.remove(render_post)
    bpy.app.handlers.render_cancel.remove(render_post)
    bpy.app.handlers.render_complete.remove(render_post)
    
  bpy_exports.unregister()
