import bpy
import bmesh
from mathutils import Vector 
import colorsys
num_colors = 4
repeat_color = 2
face_idx = 2
runlength = 4
mat_idx = 2
obj = bpy.context.object
me = obj.data


def make_mats(obj, num_colors):
    hsv=[]
    for i in range(num_colors):
        hue = i/num_colors
        sat = 1
        val = 1
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


def assign_mats_even_dist(obj):
    for i, face in enumerate(obj.data.polygons):
        #print(face.normal)
        if abs(face.normal.x) > 0.6 :
            face.material_index = 0
        elif  abs(face.normal.y) > 0.6 :
            face.material_index = 0
        elif  abs(face.normal.z) > 0.90 :
            face.material_index = 1
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
    print("Done")       
        
def assign_mats_bm(obj):
    bpy.ops.object.mode_set(mode = 'EDIT')
    bm = bmesh.from_edit_mesh(me)
    for face in bm.faces:
        face.material_index = 2
    #bm.to_mesh(me)
    bpy.ops.object.editmode_toggle()        
  

                                          
               

def clear(obj):
    for i, face in enumerate(obj.data.polygons):
        face.material_index = 0

#make_mats(obj, num_colors)

#assign_mats_even_dist(obj)
clear(obj)
#assign_mats_bm(obj)
#assign_mats_angle_faces(obj)
