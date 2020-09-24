import bpy
from mathutils import *
from math import *
import bmesh, random, time, os, sys, os.path

from .Global import svglob


#START

last_view = Vector([0, 0, 1])
did_render = False

def getKey(shapeview, key):
    for sk in shapeview.skeys:
        if sk.shapekey == key:
            return sk
    
    ret = shapeview.skeys.add()
    ret.shapekey = key
    return ret

def getTargetMatrix(ob):
  shapeview = ob.data.shape_keys.shapeview
  target = shapeview.target
  
  mat = ob.matrix_world
  
  if target.object is not None:
    ob2 = target.object
    mat = ob2.matrix_world
    bone = None
    
    if type(ob2.data) == bpy.types.Armature:
      bone = target.bone
      if bone in ob2.pose.bones:
        bone = ob2.pose.bones[bone]
      else:
        bone = None
    
    if bone:
      mat = mat @ bone.matrix
  
  loc, quat, scale = mat.decompose()
  
  return quat.to_matrix()
  
def getView():
    global last_view, did_render
    
    if svglob.is_rendering:
      did_render = True
      
      print("IS RENDERING", svglob.is_rendering)
      camera = bpy.context.scene.camera
      if not camera:
        print("ERROR: no camera?!!")
      else:
        mat2 = camera.matrix_world
        mat2 = Matrix(mat2)
        mat2.invert()
        
        last_view = Vector(mat2[2][:3])
        return
        
    view3d = None
    
    first = None
    i = 0
    if bpy.context.window and bpy.context.window.screen:
      for area in bpy.context.window.screen.areas:
        if area.type == "VIEW_3D":
          if not first:
            first = area.spaces[0].region_3d
          if i == bpy.context.workspace.shapeview.active_view3d:
            view3d = area.spaces[0].region_3d
            
          i += 1
      
      if first and not view3d:
        print("warning, failed to find correct view3d for index %i"%(bpy.context.workspace.shapeview.active_view3d));
        view3d = first
        
      if view3d:
        mat2 = view3d.view_matrix
        last_view = Vector(mat2[2][:3])
        
    return last_view

def getKeyVal(ob, key):
    global last_view
    
    ctx = bpy.context
    
    shapeview = ob.data.shape_keys.shapeview
    
    sv = getKey(shapeview, key)
    
    scene = ctx.scene
    
    view3d = None
    
    getView()

    mat1 = getTargetMatrix(ob)
    
    z1 = mat1 @ Vector(sv.vector)
    z2 = last_view
    
    z1.normalize()
    z2.normalize()   
    
    dot = z1.dot(z2)
    if sv.both_sides:
        dot = abs(dot)
        
    th = abs(acos(dot*0.99999))
    
    imat = Matrix(ob.matrix_world)
    imat.invert()
    
    th /= pi*0.5
    
    th = min(max(th, 0.0), 1.0)
    
    th = 1.0 - th;
    
    th = pow(th, 1.5)
    
    return th;
   
def _sv_getview(obname, key):
    ob = bpy.data.objects[obname]
    print("OB", ob)

    shape_keys = ob.data.shape_keys
    shapeview = shape_keys.shapeview
    sv = getKey(shapeview, key)
    
    kval = getKeyVal(ob, key)
    
    sum = 0.0
    tot = 0.0
    for sv in shapeview.skeys:
        if isBasisKey(sv.shapekey, shape_keys): continue
        if sv.shapekey not in shape_keys.key_blocks: continue
        
        kval = getKeyVal(ob, sv.shapekey)
        sum += kval
        tot += 1.0
    
    if tot == 0.0:
        return 0.0
        
    kval = getKeyVal(ob, key)
    print(key, "single", kval, "tot", tot, "sum", sum)
    if tot == 1.0:
        return kval
    
    return kval / sum
    print(key, "sum", kval)
    
    return kval

# Add variable defined in this script into the drivers namespace.
bpy.app.driver_namespace["_sv_getview"] = _sv_getview

def setView(ob):
    shapeview = ob.data.shape_keys.shapeview
    key = ob.active_shape_key_index
    
    key = ob.data.shape_keys.key_blocks[key]
    sv = getKey(shapeview, key.name)
    
    view = getView()
    print("view", view)
    
    mat = Matrix(getTargetMatrix(ob))
    mat.invert()
    
    print(mat)
    print((mat @ view))
    
    vec = mat @ view
    vec.normalize()
    
    sv.vector = vec
    print(vec)

last_update_view = Vector()

def needUpdate():
    getView()
    
    #timer might not be called during render, and thus it might think
    #view hasn't changed
    
    global did_render
    global last_update_view
    global last_view
    
    if did_render:
      did_render = False
      last_update_view = last_view
      return True
      
    if (last_view - last_update_view).length > 0.001:
        last_update_view = last_view
        return True
    
    return False

def checkViews():
    #print("need update?", needUpdate())
    if needUpdate():
        ob = bpy.data.objects[obname]
        
        if ob.mode in ["OBJECT", "POSE"]:
            print("view update detected")
            dgraph = bpy.context.evaluated_depsgraph_get()
            scene = bpy.context.scene
            ob.data.shape_keys.update_tag()
    pass


def isBasisKey(name, skeys):
  return name == skeys.key_blocks[0].name
  
def getKeyIndex(name, skeys):
  for i in range(len(skeys.key_blocks)):
    if skeys.key_blocks[i].name == name:
      return i
      
def getDriver(ob, skeys, keyname, animdata, path):
  for d in animdata.drivers:
    if d.data_path == path:
      return d
      
  ret = ob.data.shape_keys.driver_add(path)
  
  return ret
  
def makeDriver(ob, keyname, skeys, target):
  key = skeys.key_blocks[keyname]
  
  if skeys.animation_data is None:
    skeys.animation_data_create()
  
  path = "key_blocks[\"" + keyname + "\"].value"
  print(path)
  print(skeys)
  
  animdata = skeys.animation_data 
  
  d = getDriver(ob, skeys, keyname, animdata, path)
  
  for v in d.driver.variables[:]:
    d.driver.variables.remove(v)
  
  var1 = d.driver.variables.new()
  var1.name = "obself"
  var1.targets[0].id = ob
  
  d.driver.expression = "_sv_getview(\""+ob.name+"\", \"" + keyname + "\")"
  
  if target.object is not None:
    var2 = d.driver.variables.new()
    var2.name = "dgraph_link"
    var2.targets[0].id = target.object
    
    var2.type = "TRANSFORMS"
    
    if type(target.object.data) == bpy.types.Armature:
      var2.targets[0].bone_target = target.bone
  
def createDrivers(ob):
  mesh = ob.data
  shapeview = mesh.shape_keys.shapeview
  skeys = mesh.shape_keys
  target = shapeview.target 
  
  for sv in shapeview.skeys:
    if isBasisKey(sv.shapekey, skeys):
      continue
    if not sv.shapekey in skeys.key_blocks:
      print("Warning, missing key " + sv.shapekey)
      continue
      
    makeDriver(ob, sv.shapekey, skeys, target)
    
    print(sv.shapekey)

#END

from . import utils
bpy_exports = utils.Registrar([
])
