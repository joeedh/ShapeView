from .Global import svglob
from .shapeview import needUpdate
import bpy

#no longer used, embedded scripts are used instead

def start():
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


def stop():
  svglob.stopTimers()
  pass
  