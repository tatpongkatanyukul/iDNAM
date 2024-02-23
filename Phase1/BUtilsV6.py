import time
import bpy
import bmesh

import sys
import numpy as np

# CODE = {"T": "T", "Tp": "T'", "C": "C"} 
# mat_dict = {}

def clear_log(fname):
    with open(fname, 'w') as f:
        f.write("")


def log(text, fname):

    with open(fname, 'a') as f:
        f.write( '\n' + str(time.ctime()) + ' >>> ' + text)

def get_object_location(obj_name):
    obj = bpy.context.object
    ## * Select the desired objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[obj_name].select_set(True)

    # Update coordinates to global coordinates
    bpy.ops.object.transform_apply()

    # Get world coordinates of the object center
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    loc = bpy.data.objects[obj_name].location

    return loc


def read_context(CODE):
    '''
    Read all necessary info from Blender

    return [material, center.x, center.y, center.z, normal.x, normal.y, normal.z]
    '''
    obj = bpy.context.object
    ## * Select the desired objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[CODE["target"]].select_set(True)
    bpy.data.objects[CODE["T"]].select_set(True)        
    bpy.data.objects[CODE["Tp"]].select_set(True)        
    bpy.data.objects[CODE["C"]].select_set(True)        

    # Update face coordinates to global coordinates
    bpy.ops.object.transform_apply()


    # Read target info (inc. face coordinates)
    bpy.data.objects[CODE["T"]].select_set(False)        
    bpy.data.objects[CODE["Tp"]].select_set(False)        
    bpy.data.objects[CODE["C"]].select_set(False)        

    faces = []
    for i, face in enumerate(obj.data.polygons):
        faces.append([face.material_index, *face.center, *face.normal])
    faces = np.array(faces)             

    #context = {'name': obj.name, 'faces': faces}
    #print("type(context['faces']) =", type(context['faces']))
    #print('sys.getsizeof(context) =', sys.getsizeof(context))

    # Get world coordinates of key points
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    KeyT  = bpy.data.objects[CODE["T"]].location
    KeyTp = bpy.data.objects[CODE["Tp"]].location
    KeyC  = bpy.data.objects[CODE["C"]].location

    keypoints = {"T": np.array(KeyT), "Tp": np.array(KeyTp), "C": np.array(KeyC)}

    return faces, keypoints

def update_mat_dict():
    #print('BUtils: Debug: len(bpy.data.materials) =', len(bpy.data.materials))
    # global mat_dict
    mat_dict = {mat.name: i for i, mat in enumerate(bpy.data.materials)}

    return mat_dict

def clear_materials(CODE, clear_target="ALL", echo=True):
    clear_flag = {"target": False, "context": False, "data.materials": False}

    if clear_target == "ALL":
        clear_flag = {"target": True, "context": True, "data.materials": True}
    elif clear_target == "TARGET":
        clear_flag["target"]  = True
        clear_flag["data.materials"]  = True
    elif clear_target == "CONTEXT":
        clear_flag["context"]  = True
        clear_flag["data.materials"]  = True
    elif clear_target == "DATA":
        clear_flag["data.materials"]  = True
    else:
        print(f"BUtils.clear_materials: {clear_target} is an invalid target.")

    print('BUtils.clear_materials: target =', clear_target)

    if clear_flag["target"]:
        try:
            while len(bpy.data.objects[CODE["target"]].material_slots) > 0:
                bpy.ops.object.material_slot_remove() 

            print(f"    Clear {CODE['target']}.material_slots: {len(bpy.data.objects[CODE['target']].material_slots)} materials left")   
        except Exception as err:
            print(f"    Clear {CODE['target']}.material_slots: error = {err}.")

    if clear_flag["context"]:
        try:
            while len(bpy.context.object.data.materials) > 0:
                bpy.context.object.data.materials.pop()
            
            print(f"    Clear context.object.data.materials: {len(bpy.context.object.data.materials)} materials left")   
        except Exception as err:
            print(f"    Clear context.object.data.materials: error = {err}.")


    if clear_flag["data.materials"]:
        try:
            for i, m in enumerate(bpy.data.materials):
                print(f'        * remove bpy.data.materials.remove({m.name})')
                bpy.data.materials.remove(m)        

            print(f"    Clear data.materials: {len(bpy.data.materials)} materials left")   
        except Exception as err:
            print(f"    Clear data.materials: error = {err}.")


    # bpy.context.space_data.shading.type='SOLID'  # This gives an error. I guess: perhaps I called it when there is no material.

    print('BUtils.clear_materials: done.')
# end clear_materials

def add_materials(dmaterials, i=0):

    mat_dict = {}

    # Add material one by one
    for mat_name in dmaterials:
        mat_color = dmaterials[mat_name]

        # Create material if not exists
        if mat_name not in bpy.data.materials:
            mat = bpy.data.materials.new(mat_name)
            mat.diffuse_color = mat_color

            bpy.context.object.data.materials.append(mat)
            mat_dict[mat_name] = i

            i += 1
        
        # end Create material
    # end for

    return mat_dict



# def assign_face_material(face_ids, mat_name, mat_color=(1,1,1,1)):

#     global mat_dict

#     print('BUtils.assign_face_material: face_ids =', face_ids)
#     print('    material: {} color {}'.format(mat_name, mat_color))

#     # Create material if not exists
#     if mat_name not in bpy.data.materials:
#         mat = bpy.data.materials.new(mat_name)
#         mat.diffuse_color = mat_color

#         bpy.context.object.data.materials.append(mat)

#         # Update mat_dict
#         update_mat_dict()
#         print('    * Add material: {} ({}) color {}'.format(mat_name, mat_dict[mat_name], mat_color))
#     else:
#         msg = f"    * Material: {mat_name} (mat id {mat_dict[mat_name]}) already exists, "
#         msg += "color ({:.2f},{:.2f},{:.2f},{:.2f}).".format(*bpy.data.materials[mat_dict[mat_name]].diffuse_color)
#         print(msg)
        
#     # end Create material

#     # Assign material to faces per face_ids
#     obj = bpy.data.objects[CODE["target"]]
#     # obj.data.polygons[face_ids].material_index = mat_dict[mat_name]
#     # This is not working for np.array: dtype=int32
#     for id in face_ids:
#         obj.data.polygons[id].material_index = mat_dict[mat_name]
#     # end for
    

#     # print(f'Debug: mat id {mat_dict[mat_name]} face_ids=', face_ids)

#     print('BUtils.assign_face_material: done.')
#     return mat_dict[mat_name]


def read_face_ids_material(obj_name, mat_id):
    '''
    Read ids of faces whose material indices are matched.
    return [id] (python list)
    '''

    obj = bpy.data.objects[obj_name]
    found_ids = []
    for i, face in enumerate(obj.data.polygons):
        if face.material_index == mat_id:
            found_ids.append(i)
    # end for i

    print(f'BUtils.read_face_ids_material({obj_name}, {mat_id}) founds {len(found_ids)} ids. Done.')
    return found_ids

def create_curve(vertices, curve_name="ridge", coll_name=None):
    '''
    Create curve by the given vertice coordinates in order.
    ```vertices```, e.g., [[x, y, z], [x, y, z], ... ] 

    '''

    if len(vertices) < 2:
        print('BUtils: create_curve needs more than one vertex.')
        return

    
    coll = None
    try:
        coll = bpy.data.collections[coll_name]
    except:
        coll = bpy.data.collections.new(coll_name)
        bpy.context.scene.collection.children.link(coll)


    bm = bmesh.new()
    # Create vertices
    v0 = vertices[0]
    vb = bm.verts.new((v0[0], v0[1], v0[2]))    
    for co in vertices[1:]:
        ve = bm.verts.new((co[0], co[1], co[2]))    
        # Create an edge
        bm.edges.new((vb, ve))        
        vb = ve            
    
    try:
        me = bpy.data.meshes[curve_name]
    except:
        me = bpy.data.meshes.new(curve_name)
        
    bm.to_mesh(me)
    try:
        ob = bpy.data.objects[curve_name]
    except:
        ob = bpy.data.objects.new(curve_name, me)
        #context = bpy.context        
        #context.collection.objects.link(ob)
        coll.objects.link(ob)

        # ctxobj = bpy.context.object
        # for c in ctxobj.users_collection:
        #     c.objects.unlink(ctxobj)
        # coll.objects.link(ctxobj)

    bm.free()
# end create_curve    


def make_bridge(shp, xsec, angles):

    # 1. Change `crosssect` and `ridge` to curve.
    # save and reset state of selection
    
    active_o, selected_o = select_objects([shp])
    bpy.ops.object.convert(target="CURVE")

    select_objects([xsec])
    bpy.ops.object.convert(target="CURVE")

    # 4.2. Bevel
    obj = bpy.data.objects[shp]
    obj.data.bevel_mode = 'OBJECT'
    obj.data.bevel_object = bpy.data.objects[xsec]

    # 4.3. Convert shp to mesh
    
    active_o, selected_o = select_objects([shp])
    bpy.ops.object.convert(target='MESH')
                
    restore_selection(active_o, selected_o)

    return


def select_objects(obj_list):
    '''
    After used, restore selection state with ```restore_selection```
    '''

    ################################################
    ## Selection block : START  
    selected_objects = bpy.context.selected_objects
    active_object = bpy.context.active_object
    for obj in selected_objects:
        obj.select_set(False)

    success = False
    to_find = len(obj_list)
    for collection in [c for c in bpy.data.collections]:
        for obj in collection.objects:
            if obj.name in obj_list:
                bpy.context.view_layer.objects.active = obj
                #selection = obj.select_get()
                obj.select_set(True)

                #obj.select_set(selection)
                to_find -= 1
                if to_find == 0:
                    break                
            # end if
        # end for obj
        if to_find == 0:
            break
    # end for collection                

    return active_object, selected_objects

def restore_selection(active_object, selected_objects):

    # restore saved state of selection
    bpy.context.view_layer.objects.active = active_object

    for obj in bpy.context.selected_objects:
        obj.select_set(False)

    for obj in selected_objects:
        obj.select_set(True)
    ## Selection block : END
    #############################################


################################################################################
if __name__ == '__main__':
    log("test 2", 'log.txt')