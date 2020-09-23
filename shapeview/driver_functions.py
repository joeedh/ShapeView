import bpy
from math import *
from mathutils import *


obname = "Topology.001"
last_view = Vector([0, 0, 1])

class ShapeViewKey (bpy.types.PropertyGroup):
    vector : bpy.props.FloatVectorProperty(size=3)
    shapekey : bpy.props.StringProperty()
    both_sides = bpy.props.BoolProperty()
 
bpy.utils.register_class(ShapeViewKey)
   
class ShapeView (bpy.types.PropertyGroup):
    skeys : bpy.props.CollectionProperty(type=ShapeViewKey)

bpy.utils.register_class(ShapeView)

bpy.types.Key.shapeview = bpy.props.PointerProperty(type=ShapeView)    

def getKey(shapeview, key):
    for sk in shapeview.skeys:
        if sk.shapekey == key:
            return sk
    
    ret = shapeview.skeys.add()
    ret.shapekey = key
    return ret

def getView():
    view3d = None
    global last_view

    if bpy.context.window and bpy.context.window.screen:
        for area in bpy.context.window.screen.areas:
            if area.type == "VIEW_3D":
                view3d = area.spaces[0].region_3d
                
#        print("view3d:", view3d)
        if view3d:
#            print(view3d.view_matrix)
            mat2 = view3d.view_matrix
            last_view = Vector(mat2[2][:3])
    return last_view

def getKeyVal(key):
    global last_view
    
    ctx = bpy.context
    ob = bpy.data.objects[obname]
    
    shapeview = ob.data.shape_keys.shapeview
    
    sv = getKey(shapeview, key)
    
    scene = ctx.scene
    
    view3d = None
    
    getView()

    mat1 = ob.matrix_world
    
    #z1 = Vector(mat1[2][:3])
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
    
    print("th", th, imat @ z2)
    th /= pi*0.5
    
    th = min(max(th, 0.0), 1.0)
    
    th = 1.0 - th;
    
    th = pow(th, 1.5)
    
    return th;
   
def hv(key):
    ob = bpy.data.objects[obname]
    shapeview = ob.data.shape_keys.shapeview
    sv = getKey(shapeview, key)
    
    kval = getKeyVal(key)
    
    sum = 0.0
    tot = 0.0
    for skey in shapeview.skeys:
        if skey.shapekey == "Basis": continue
    
        kval = getKeyVal(skey.shapekey)
        sum += kval
        tot += 1.0
    
    if tot == 0.0:
        return 0.0
        
    print(key, "single", kval)

    kval = getKeyVal(key)
    if tot == 1.0:
        return kval
    
    return kval / sum
    print(key, "sum", kval)
    
    return kval

# Add variable defined in this script into the drivers namespace.
bpy.app.driver_namespace["hv"] = hv

def setView(both_sides=False):
    ob = bpy.data.objects[obname]
    shapeview = ob.data.shape_keys.shapeview
    key = ob.active_shape_key_index
    
    key = ob.data.shape_keys.key_blocks[key]
    sv = getKey(shapeview, key.name)
    
    sv.both_sides = both_sides
    
    print(shapeview, sv, sv.shapekey)
    
    view = getView()
    print(view)
    
    sv.vector = view
    print(sv.vector)

last_update_view = Vector()

def needUpdate():
    getView()
    
    global last_update_view
    global last_view

    if (last_view - last_update_view).length > 0.001:
        last_update_view = last_view
        return True
    
    return False

class SVGlob:
    def __init__(self):
        self.timergen = 0

    def startTimer(self, timerfunc):
        self.timergen += 1
        bpy.app.timers.register(bpy.svglob.ontimer)
        
        timergen = [self.timergen]
        def timer():
            if self.timergen != timergen[0]:
                print("Timer stop")
                return None
            timerfunc()
            return 0.1
        
        bpy.app.timers.register(timer)

    def ontimer(self):
        pass
            
if not hasattr(bpy, "svglob"):
    bpy.svglob = SVGlob()
    print("instantiating SVGlob...")
    

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

#bpy.svglob.startTimer(checkViews)
#setView(True)
