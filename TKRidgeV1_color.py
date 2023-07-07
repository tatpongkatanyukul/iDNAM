import bpy
import bmesh
import math 
from mathutils import Vector 
import colorsys

import numpy as np


def super_train_poly(w, DataX, DataY):
    '''
    ```DataX```: np.array of shape (N,)
    ```DataY```: np.array of shape (N,)
    
    y [1 x N] = wt [1 x M] * Phi [M x N]

    Grad [M x 1] = Phi [M x N] * (yt [N x 1] - Yt [N x 1])
    Thus, at Grad = 0, solve for w in Phi [M x N] * (yt [N x 1] - Yt [N x 1]) = Phi * t(Phi) * w - Phi * Yt = 0
    '''

    Mp = len(w)
    N = len(DataX)

    # Compose Phi matrix [M x N]
    Phi = np.vstack((np.ones((1, N)),
                     np.tile(DataX, (Mp - 1, 1))
                     ))

    # Make it [1 .. 1; x0 x1 .. xn; x0^2, x1^2 .. xn^2; .. xn^M]
    Phi = np.cumprod(Phi, axis=0)

    # Use linear solver A x = b

    A = np.matmul(Phi, np.transpose(Phi))
    b = np.matmul(Phi, np.transpose(DataY))

    w = np.linalg.solve(A, b)

    return w


def fmodel(x, w):
    m = len(w)
    y = 0
    for i in range(m):
        y += w[i] * x**i
    
    return y


def find_poly(obj, marker=1, gen_mesh=True):
    '''
    ```marker```: material index
    '''
    
    # Prepare data
    DX = []
    DY = []
    
    me = obj.data
    for i, face in enumerate(me.polygons):
        if face.material_index == marker:
            print(face.center[0], face.center[1], face.center[2])        
            DX.append(face.center[0])
            DY.append(face.center[1])
    
    ids = np.argsort(DX).tolist()
    
    DX = np.array(DX)
    DY = np.array(DY)
    
    DX = DX[ids]
    DY = DY[ids]
    N = DX.shape[0]

#    print('N=', N)    
#    print('DX=', DX.shape,':', DX)
#    print('DY=', DY.shape,':', DY)
    
    # Choose degree
    w0 = [0, 0, 0]
    
    # Find params*
    w =super_train_poly(w0, DX, DY)
    print('w =', w)
    
    z = 0
    if gen_mesh:
        vertices = [ [DX[i], fmodel(DX[i], w), z] for i in range(N)]
        return w, vertices
            
    return w




##########################################################

def create_curve(vertices, curve_name="ridge", coll=None):
    '''
    Create curve by the given vertice coordinates in order.
    ```vertices```, e.g., [[x, y, z], [x, y, z], ... ] 

    '''

    if len(vertices) < 2:
        print('vertices have to have more than one vertex.')
        return

    v0 = vertices[0]

    # Create object with ```name```    
#    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0, 0, 0))  
    bpy.ops.mesh.primitive_grid_add(size=1, 
        enter_editmode=False, align='WORLD', 
        location=(v0[0], v0[1], v0[2]), scale=(1, 1, 1))


    obj = bpy.context.object
    obj.name = curve_name

    bpy.ops.object.mode_set(mode='OBJECT')

    if coll is not None:
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)

    bpy.ops.object.mode_set(mode='EDIT')


    bm = bmesh.from_edit_mesh(obj.data)


    if hasattr(bm.verts, "ensure_lookup_table"): 
        bm.verts.ensure_lookup_table()

    # Create vertices
    vb = bm.verts.new((v0[0], v0[1], v0[2]))    

    for co in vertices[1:]:
        ve = bm.verts.new((co[0], co[1], co[2]))
        
        # Create an edge
        bm.edges.new((vb, ve))
        
        vb = ve            
    
        
    bmesh.update_edit_mesh(obj.data)

    # This is optional, you could also stay in editmode.
    bpy.ops.object.mode_set(mode='OBJECT')

     


def ridge_morphogen(obj, center_morphogen, tau=17):
    me = obj.data
    for i, face in enumerate(me.polygons):
        z = Vector((0,0,1))
        fn = face.normal
        ang = abs(z.angle(fn))
        vinx = face.vertices[0]
        vco = me.vertices[vinx].co[2]

        # Radial vector from center of morphogen
#        print('face.center=', face.center)
        radial = face.center - center_morphogen
#        print('radial=', radial)
        
        Xprod = fn.cross(radial)
        Dotprod = fn.dot(radial)
#        print('cross =', Xprod)
#        print('dir(Xprod)=', dir(Xprod))
#        print('Xprod.magnitude=', Xprod.magnitude)
        
        
        face.material_index = 0        
        if abs(Xprod.magnitude) > tau and vco > 0:
            face.material_index = 1            
        elif Dotprod > 0 and vco > 0:
            face.material_index = 2
        elif Dotprod < 0 and vco > 0:
            # Negative result
            face.material_index = 3
#            print('(neg) Xprod.magnitude=', Xprod.magnitude)
                
        
        
def make_mats(obj, num_colors):
    hsv=[]
    for i in range(num_colors):
        hue = i/num_colors
        sat = 0.8
        val = 0.3
        hsv.append((hue, sat, val))
    # clear current materials
    while len(obj.material_slots) > 0:
        bpy.ops.object.material_slot_remove()
    for col in hsv:
        if f'{obj.name}_{col[0]}' not in bpy.data.materials:
            mat = bpy.data.materials.new(f'{obj.name}_{str(col[0])}')
            r,g,b = colorsys.hsv_to_rgb(col[0], col[1], col[2])
            mat.diffuse_color = (r,g,b,1)
        else:
            mat = bpy.data.materials[f'{obj.name}_{str(col[0])}']
        bpy.context.object.data.materials.append(mat)


def assign_mats_normal(obj):
    me = obj.data
    for i, face in enumerate(me.polygons):
        z = Vector((0,0,1))
        fn = face.normal
        ang = abs(z.angle(fn))
        vinx = face.vertices[0]
        vco = me.vertices[vinx].co[2]
        
        if ang < math.pi/8 and vco > 0:
            face.material_index = 1
        elif ang > math.pi/6 and vco > 0:
            face.material_index = 2
        else:
            face.material_index = 0
        
        
def assign_mats_angle_faces(obj):
    bpy.ops.object.mode_set(mode = 'EDIT')
    bm = bmesh.from_edit_mesh(me)    
    for i, edge in enumerate(bm.edges):
        linked = edge.link_faces       
        if len(linked) == 2:            
           p1 = linked[0].normal
           p2 = linked[1].normal
           ang = p1.angle(p2)
           if ang > 0.2:
                linked[0].material_index = 1
    bpy.ops.object.editmode_toggle()
    print("assign_mats_angle_faces: done")       
        
        
def assign_mats_bm(obj):
    bpy.ops.object.mode_set(mode = 'EDIT')
    bm = bmesh.from_edit_mesh(me)
    for face in bm.faces:
        face.material_index = 2
    #bm.to_mesh(me)
    bpy.ops.object.editmode_toggle()        
  

                                          
               

def clear_material(obj):
    for i, face in enumerate(obj.data.polygons):
        face.material_index = 0


if __name__ == '__main__':

    print('\nMain')
    
    
    num_colors = 4
    repeat_color = 2
    face_idx = 2
    runlength = 4
    mat_idx = 2
    obj = bpy.context.object

    print('object:', obj.name)
    bpy.ops.object.mode_set(mode='OBJECT')


    make_mats(obj, num_colors) # Make colors
    clear_material(obj)                 # Clear colors


    # 1. Find center of morphogen: cm = (T1 +T1p)/2
    T = bpy.data.objects["T1"].location
    Tp = bpy.data.objects["T1'"].location
    
    cm = (T + Tp)/2
    print('cm=', cm)
    
    
    print('   ridge_morphogen')
    ridge_morphogen(obj, cm, 17.4)


#    print('   create_curve')
#    vertices = [[-17,27,-18], [-17.1, 8.1, 3.0], [-18, 0, 0]]
#    create_curve(vertices, "ridge")
#    
    
    print('   find_poly')
    w, verts = find_poly(obj, marker=1, gen_mesh=True)
    
    print('verts=', verts)
    create_curve(verts, "ridge")
    
    print('Done\n')