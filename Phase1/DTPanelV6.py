bl_info = {
    "name": "DT Panel",
    "blender": (3, 50, 0),
    "location": "View3D > Sidebar > Dental Workflow",
    "category": "Object",
}

import bpy
import bmesh
from bpy.props import IntProperty, FloatProperty
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils import Vector
from mathutils import Matrix 
from math import radians, atan, cos,sin,pi,degrees
from collections import defaultdict


import os
import numpy as np
import pickle
import json

# import AutoBridgeBEv2 as ab
import BUtilsV6 as uu
import RidgeIdenV3 as ri
import ShapeApproxV4 as sa
import CrossSecApproxV7 as csa

import importlib
# importlib.reload(ab)
importlib.reload(uu)
importlib.reload(ri)
importlib.reload(sa)
importlib.reload(csa)

# Set by AutoBridge (Main script)
wpath = "."
logfile = "log.txt"
config_file = ""

CODE = {} # {"T": "T", "Tp": "T'", "C": "C"}
mat_dict = {}

pvars = {}               # Dummy; loaded and set by AutoBridge.py

# Set by actions on Panel
faces = np.array([])     # Dummy: set by WM_OT_Iden_Ridge
keypoints = {}           # Dummy: set by WM_OT_Iden_Ridge

vert_double_threshold = 0.1
dissolve_threshold = 0.01

status = {"aligned": False, 
          "data_ready": False, 
          "ridge": False, "ridge_mat_index": None,
          "shape": False, "shape_rst": None,
          "cross_section": False, "xsect_rst": None,
          "bridge": False}


# not work as pull detect

class DT_MainPanel(bpy.types.Panel):
    
    bl_idname = 'DT_PT_MainPanel'
    bl_label = 'DT Workflow Panel'
    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Dental Workflow'
    
    def draw(self, context):
        layout = self.layout
        # scene = context.scene

        # column = layout.column(align=True)
        # row = column.row()
        # row.label(text = "0.1")
        # row = column.row()
        # row.label(text = "0.2")
        # row = column.row()
        # op = row.operator("wm.test",text= "0.3. Test")

        row = layout.row()
        row.label(text= "1. Select IOS before proceed")
        
        row = layout.row()
        # row.alignment = "LEFT"
        op = row.operator("wm.addref",text= "2. Clean up and create keypoints")
        # print('DTPanelV2: Debug: op.values()=', op.values())

        row = layout.row()
        row.label(text= "3. Move keypoints to locations")
        row = layout.row()
        row.operator("wm.movetoworldorigin",text="4. Align by keypoints")
        row = layout.row()
        row.operator("wm.addrefplane",text="5. Add reference planes")
        row = layout.row()
        row.operator("wm.iden_ridge",text="6. Identify ridge")
        # row = layout.row()
        # row.label(text= "(Ridge can manually be modified by face material.)")
        row = layout.row()
        row.operator("wm.approx_shape",text="7. Approximate shape")
        row = layout.row()
        row.operator("wm.approx_xsect",text="8. Approximate cross-section")
        row = layout.row()
        row.operator("wm.add_bridge",text="9. Add bridge")
        
        row = layout.row()
        # row.alignment = 'LEFT'
        row.operator("wm.reload_cfg",text="# Reload json")

        row = layout.row()
        row.operator("wm.clear_bridge",text="# Clear bridge")

        # print("DTPanelV3: DEBUG")
        # print("type(row) =", type(row))
        # print("row.operator.__doc__ = ")
        # print(row.operator.__doc__)
        # print("DTPanelV3: DEBUG ...")


        
               
def createRefP(name,location,color,collection, onSurface=False):
    '''
    Create a reference point if it does not exist.
    '''

    try: 
        obj = bpy.data.objects[name]
    except:
        # Key point does not exist.
        bpy.ops.mesh.primitive_ico_sphere_add(radius=1, location=location)
        obj = bpy.context.object
        obj.name = name
        obj.color = color
        for c in obj.users_collection:
            c.objects.unlink(obj)
        collection.objects.link(obj)

# end createRefP


class WM_OT_AddRef(bpy.types.Operator):
    """Clean up IOS and add key points"""
    bl_label = "Add Key Points (selected SCAN)"
    bl_idname = "wm.addref"   
                

    def execute(self, context):
        global status
        global CODE

        # Rename selected obj to the target name
        obj = bpy.context.selected_objects[0]
        obj.name = CODE["target"]

        # Move the selected object to (0,0,0)
        ## * Move object origin to the object geometry
        bpy.ops.object.transform_apply()
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        
        ## * Move the object, if it is NOT aligned.
        if not status["aligned"]:
            loc = obj.location
            diff = Vector((0,0,0)) - loc
            bpy.ops.transform.translate(value=diff)

        print("DTPanel: Cleaning up ...")
        # Reduce a number of vertices 
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=vert_double_threshold)
        ## * Delete loose components
        bpy.ops.mesh.delete_loose()
        ## * Make all faces triangles
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris(quad_method='FIXED', ngon_method='BEAUTY')
        ## * Remove non-interior faces
        bpy.ops.mesh.select_interior_faces()
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.delete(type='VERT')
        ## * Remove small edges and faces
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.dissolve_degenerate(threshold=dissolve_threshold)

        bpy.ops.object.mode_set(mode='OBJECT')     

        # Rotate the geometry to have its average normal (0,0,1)
        # if False:
        #     me = obj.data

        #     acc = Vector((0,0,0))
        #     count = 0
        #     for f in me.polygons:    
        #         acc += f.normal
        #         count += 1

        #     acc = acc / count
        #     rot = acc.rotation_difference( Vector((0,0,1))).to_euler()
        #     obj.rotation_euler = rot
        #     bpy.ops.object.transform_apply()
        #     bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        # Create reference points, T, Tp, and C

        initT = Vector((-15,1,1))      # T's initial value
        initTp = Vector((15,1,1))       # Tp's initial value
        initC = Vector((-15,15,1  ))    # C's initial value

        if pvars["reference"]["autoaxis"]:
            # Rotate the geometry to have the widest span along x
            # Pre-estimate x,y,z axes

            unaligned_faces = []
            for face in obj.data.polygons:
                unaligned_faces.append([*face.center, *face.normal])

            unaligned_faces = np.array(unaligned_faces)
            
            print('Maximum projection: PCA?')

            raise Exception("DTPanel: Under-construction feature: json 'reference'>'autoaxis'.")
        # end if


        try:
            coll = bpy.data.collections["Reference"]
        except:
            coll = bpy.data.collections.new("Reference")
            bpy.context.scene.collection.children.link(coll)

        createRefP(CODE["T"], initT, (0, 0, 1, 1),coll)            
        createRefP(CODE["Tp"], initTp, (0, 0.8, 1, 1),coll)            
        createRefP(CODE["C"], initC,(1, 0, 0, 1),coll) 
        createRefP(CODE["RO"], initC,(1, 0, 0, 1),coll)
        createRefP(CODE["RI"], initC,(1, 0, 0, 1),coll)
        
        bpy.context.space_data.shading.color_type = 'OBJECT'

        if pvars["reference"]["mode"] == "constraint":
            # Select the objects
            activ, selected = uu.select_objects([CODE["T"]])

            # Constraints
            bpy.ops.object.constraint_add(type='SHRINKWRAP')

            obj = bpy.context.object
            obj.constraints["Shrinkwrap"].shrinkwrap_type = 'PROJECT'
            obj.constraints["Shrinkwrap"].project_axis = 'NEG_Z'
            obj.constraints["Shrinkwrap"].target = bpy.data.objects["SCAN"]

            for kp in [CODE["Tp"], CODE["C"]]:
                uu.select_objects([kp])
                bpy.ops.object.constraint_add(type='SHRINKWRAP')

                obj = bpy.context.object
                obj.constraints["Shrinkwrap"].shrinkwrap_type = 'PROJECT'
                obj.constraints["Shrinkwrap"].project_axis = 'NEG_Z'
                obj.constraints["Shrinkwrap"].target = bpy.data.objects["SCAN"]
            # end for kp

            # Restore the selection state
            uu.restore_selection(activ, selected)
        # end if

        # Set 3D viewport to solid
        bpy.context.space_data.shading.type='SOLID'

        print("DTPanel: Create Keypoints Done\n")
        return {'FINISHED'}
    
    # Force to select an object before enabling the button.
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    
class WM_OT_MoveToWorldOrigin(bpy.types.Operator):
    """Move to the world origin"""
    bl_label = "Move to World Origin"
    bl_idname = "wm.movetoworldorigin"
    
    def execute(self, context):
        global status
        global CODE

        try: 

            # Align the target and keypoints

            ## * Select the desired objects
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[CODE["target"]].select_set(True)
            bpy.data.objects[CODE["T"]].select_set(True)        
            bpy.data.objects[CODE["Tp"]].select_set(True)        
            bpy.data.objects[CODE["C"]].select_set(True)
            bpy.data.objects[CODE["RO"]].select_set(True)
            bpy.data.objects[CODE["RI"]].select_set(True)
            
            ## * Get world coordinates of key points
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            p1 = bpy.data.objects[CODE["T"]].location
            p2 = bpy.data.objects[CODE["Tp"]].location

            ## * Compute a midpoint
            m = (p1 + p2) *0.5
            ## * Prep a vector pointing from T to Tp
            v1 = p2 - p1        
            v1.normalize()

            ## * Compute rotation to have T-Tp lie along x-axis
            rot = v1.rotation_difference( Vector((1,0,0 ))).to_euler()
            
            ## * Get the midpoint to (0,0,0)
            for obj in bpy.context.selected_objects:                
                obj.location -= m
            
            ##   Finish the translation: have all objects' origins to (0,0,0), ready for rotation around (0,0,0)
            bpy.ops.object.transform_apply()                            

            ## * Perform rotation around (0,0,0)
            for obj in bpy.context.selected_objects:                
                 obj.rotation_euler = rot

            ##   Finish the rotation: have all vertex coordinates w.r.t. (0,0,0)
            bpy.ops.object.transform_apply()                            

            ## * Rotate around x-axis to have T-Tp-C lie flat on z=0 plane

            ##   Align with z-axis
            #    (T' - T) x (C - T) align with +z (0,0,1)
            
            #    Bring object origins (particularly C) back to their geometries, to have the object's world coord
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')  
            p1 = bpy.data.objects[CODE["T"]].location
            p2 = bpy.data.objects[CODE["Tp"]].location
            p3 = bpy.data.objects[CODE["C"]].location

            vTTp = p2 - p1
            vTC = p3 - p1
            vx = vTTp.cross(vTC)

            rot = vx.rotation_difference( Vector((0,0,1))).to_euler()
            bpy.ops.object.transform_apply()

            ## * Perform rotation around (0,0,0)
            for obj in bpy.context.selected_objects:                
                 obj.rotation_euler = rot
            
            ##   Finish the rotation
            bpy.ops.object.transform_apply()



            ##   Reset the object origins to their geometries
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            bpy.ops.object.select_all(action='DESELECT')
    

            status["aligned"] = True
            print("DTPanel: Align/Move Done\n")
        except Exception as e: 
            print("DTPanel: Error Move ", e)
    
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        try:
            bpy.data.objects[CODE["target"]]
            bpy.data.objects[CODE["T"]]
            bpy.data.objects[CODE["Tp"]]
            bpy.data.objects[CODE["C"]]
            return True
        except:
            return False


def createRefPlane(name,m_size,color,coll,rotate=False):
    try: 
        obj = bpy.data.objects[name]
    except:
        bpy.ops.mesh.primitive_plane_add(size=m_size, align='WORLD' )   
        obj = bpy.context.object
        obj.name = name
        obj.location = (0,m_size/2,0)
        if rotate:
            obj.rotation_euler[1] = radians(90)
        obj.color = color
        for c in obj.users_collection:
            c.objects.unlink(obj)
        coll.objects.link(obj)
    return obj
   

class WM_OT_AddRefPlane(bpy.types.Operator):
    """Add referent planes"""
    bl_label = "Add Reference Planes"
    bl_idname = "wm.addrefplane"
    
    def execute(self, context):
        global CODE

        d = bpy.data.objects[CODE["target"]].dimensions
        coll = bpy.data.collections["Reference"]
   
        m_size = max(d[0],d[1])
        createRefPlane("Refplane",m_size,(1, 1, 1, 0.5),coll)

        m_size = max(d[1],d[2])
        try:
            empty = bpy.data.objects["RefZC"]
        except:
            empty = bpy.data.objects.new(name="RefZC", object_data=None)
            coll.objects.link(empty)

        print("DTPanel: Add Ref Plane Done\n")
        return {'FINISHED'}


    @classmethod
    def poll(cls, context):
        try:
            bpy.data.objects[CODE["target"]]            
            bpy.data.objects[CODE["C"]]
            return True
        except:
            return False


class WM_OT_Iden_Ridge(bpy.types.Operator):
    """Identify ridge"""
    bl_label = "Identify ridge"
    bl_idname = "wm.iden_ridge"

    def execute(self, context):
        '''
        Read Blender context. Invoke ri.inden_ridge. Set material to mark ridge faces.
        '''

        global status
        global pvars
        global faces
        global keypoints
        global CODE
        global mat_dict

        print("DTPanel: Identifying ridge")

        ridge_ids = np.array([])  # Dummy: set by ri.iden_ridge

        active_o, selected_o = uu.select_objects([CODE['target']])

        print("DTPanel: * 1. read context")
        # Read context from Blender
        # faces = [material, center.x, center.y, center.z, normal.x, normal.y, normal.z]
        # keypoints = {"T": T, "Tp": Tp, "C": C}
        faces, keypoints = uu.read_context(CODE)

        print('DTPanel:   faces.shape =', faces.shape)
        print('DTPanel:   keypoints =', keypoints)
        status["data_ready"] = True

        # Save context
        if pvars['save_context']:
            try:
                pface_file = os.path.join(wpath, pvars['faces_file'])
                np.save(pface_file, faces)

                pkp_file = os.path.join(wpath, pvars['kp_file'])
                with open(pkp_file, 'wb') as file: 
                    pickle.dump(keypoints, file) 

                uu.log(f"DTPanel: save faces ({faces.shape}) to {pface_file}.", logfile)
                uu.log(f"DTPanel: save keypoints to {pkp_file}.", logfile)
            except Exception as err:
                uu.log(f"DTPanel: Fail to save. {err=}", logfile)

        print('DTPanel: * 2. invoke RidgeIden.iden_ridge')
        uu.log(f"DTPanel: invoke RidgeIden.iden_ridge.", logfile)
        ridge_ids, fb = ri.iden_ridge(faces, keypoints, pvars["ridge"])
                    
        uu.restore_selection(active_o, selected_o)

        print('DTPanel: * 3. assign materials by ridge')

        print('DTPanel: * 3.1 clear materials')
        # Clear and add materials
        # Add and clear, so that there will always be some materials to clear.

        dmats = pvars["materials"]
        uu.add_materials(dmats)
        uu.clear_materials(CODE, clear_target="ALL")
        # Clear target, context, and data. All selected objects will be clear off all materials.

        # Add materials      
        mat_dict = uu.add_materials(dmats)
        
        print('DTPanel:   * mat_dict =', mat_dict)




        print('DTPanel: * 3.2 add designaed materials')

        print('DTPanel:   * add off-focus material')
        # Add default material for all faces
        obj = bpy.data.objects[CODE["target"]]
        for p in obj.data.polygons:
            p.material_index = mat_dict["off-focus"]

        print('DTPanel:   * add ridge material')
        # Add material for ridge
        for id in ridge_ids:
            obj.data.polygons[id].material_index = mat_dict["ridge"]

        if pvars["ridge"]["show"]:
            bpy.context.space_data.shading.type='MATERIAL'

        status["ridge"] = True
        status["ridge_mat_index"] = mat_dict['ridge']
        print("DTPanel: Iden Ridge Done;\n    * status =", status, '\n')
        uu.log(f"DTPanel: identifying ridge is done.", logfile)
        return {'FINISHED'}


    # Force to select an object before enabling the button.
    @classmethod
    def poll(cls, context):
        workable = False
        if len(context.selected_objects) == 1:
            if context.selected_objects[0].name == CODE["target"]:
                workable = True

        return workable


class WM_OT_Approx_Shape(bpy.types.Operator):
    """Approximate a ridge shape"""
    bl_label = "Approximate Shape"
    bl_idname = "wm.approx_shape"

    def execute(self, context):
        global status
        global pvars
        global faces
        global keypoints
        global CODE

        model_name = pvars["shape"]["output_names"][0]
        shape_name = pvars["shape"]["output_names"][1]

        print("DTPanel: Approximating ridge shape")

        # Read ridge
        print(f'DTPanel: * read ridge of {CODE["target"]} having material index {status["ridge_mat_index"]}')
        uu.log(f'DTPanel: read ridge of {CODE["target"]} having material index {status["ridge_mat_index"]}.', logfile)

        ridge_ids = uu.read_face_ids_material(CODE["target"], status["ridge_mat_index"])

        print(f'DTPanel: * ridge:', len(ridge_ids))
        
        # Get shape obj
        print('DTPanel: * invoke ShapeApprox.approx_shape')
        uu.log(f"DTPanel: invoke ShapeApprox.approx_shape.", logfile)

        dshape, fb = sa.approx_shape(faces, keypoints, ridge_ids, pvars["shape"])
        # status["shape_rst"] = {"obj": shape_obj, "fb": fb}

        uu.log(f'DTPanel: * loss {fb["rst"]["final_loss"]:.1f}; fit result{fb}.', logfile)

        # Create shape geometry
        N = pvars["shape"]["resolution"]
        key1, key2 = pvars["shape"]["angles"]
        loc1 = np.array(uu.get_object_location(key1)).reshape((1,-1))
        loc2 = np.array(uu.get_object_location(key2)).reshape((1,-1))

        _, phi1 = sa.rec2pol(loc1[[0],:2])[0]
        _, phi2 = sa.rec2pol(loc2[[0],:2])[0]

        print(f'DTPanel: * create shape geometry: ({phi1}, {phi2})')
        uu.log(f"DTPanel: create shape geometry.", logfile)

        z = 0
        ts_shape = np.linspace(phi1, phi2, N)
        ts_model = np.linspace(0, 2*np.pi, N)

        tss = [ts_shape, ts_model]
        cnames = [shape_name, model_name]

        for j in range(2):

            xs, ys = fb["default_shape_fn"].gen_shape(tss[j])
            if fb["success"]:
                xs, ys = dshape.gen_shape(tss[j])
                
            vertices = [ [xs[i], ys[i], z] for i in range(len(tss[j]))]

            # print(f'DEBUG: ts = {np.min(tss[j])}, {np.max(tss[j])}')

            print('DTPanel: * invoke BUtils.create_curve')
            uu.log(f"DTPanel: invoke BUtils.create_curve.", logfile)

            uu.create_curve(vertices, curve_name=cnames[j], coll_name=pvars["shape_collection"])
        
        # Save shape

        pshape_file = os.path.join(wpath, pvars["shape_save"])
        with open(pshape_file, 'wb') as file: 
            pickle.dump((dshape, fb), file)

        print(f'DTPanel: * save shape: {pshape_file}')
        uu.log(f'DTPanel: save shape to {pshape_file}.', logfile)

        status["shape"] = True
        status["shape_rst"] = {"name": shape_name, "model": model_name, "obj": dshape}
        print("DTPanel: Approx Shape Done;\n    * status =", status, '\n')
        uu.log(f"DTPanel: approx shape is done.", logfile)
        return {'FINISHED'}

    # Force to have finished ridge before enabling
    @classmethod
    def poll(cls, context):
        workable = False

        # We have done the ridge, but not cross_section,
        # because cross_section assigns face materials, invalidating ridge identification.
        if status["ridge"] and not status["cross_section"]:
            workable = True

        return workable

class WM_OT_Approx_XSect(bpy.types.Operator):
    """Approximate a cross-section"""
    bl_label = "Approximate Cross-Section"
    bl_idname = "wm.approx_xsect"

    def execute(self, context):
        global status
        global pvars
        global faces
        global CODE

        xsect_name = pvars["cross_sect"]["output_name"]
        print("DTPanel: Approximating ridge cross-section")

        xspar = pvars["cross_sect"]

        print("DTPanel: * read key locations")

        xs_bounds = {}
        # 1. Read key locations
        key_angle1  = uu.get_object_location(xspar["angle_keys"][0])
        key_angle2  = uu.get_object_location(xspar["angle_keys"][1])
        key_radial1 = uu.get_object_location(xspar["radial_bounds"][0])
        key_radial2 = uu.get_object_location(xspar["radial_bounds"][1])

        # print("DEBUG: key_radial1 =", key_radial1)
        # print("DEBUG: key_radial2 =", key_radial2)
        # return {'FINISHED'}

        ## 1.1. Key locations to angles
        phi1 = sa.rec2pol(np.array(key_angle1)[:2].reshape((1,-1)))[0,1]
        phi2 = sa.rec2pol(np.array(key_angle2)[:2].reshape((1,-1)))[0,1]
        print(f'DTPanel:   * angles between {xspar["angle_keys"]} = [{phi1:.2f}, {phi2:.2f}]')
        xs_bounds["angles"] =  (phi1, phi2)

        ## 1.2. Key locations to radials
        xs_bounds["radial_mode"] = xspar["radial_mode"]

        if xspar["radial_mode"] == "Z":
            z1 = key_radial1[2] # inner
            z2 = key_radial2[2] # outer
            print(f'DTPanel:   * radial {xspar["radial_mode"]} between {xspar["radial_bounds"]} = [{z1:.2f}, {z2:.2f}]')
            xs_bounds["zs"] = (z1, z2)  # (inner, outer)  

        elif xspar["radial_mode"] == "R":
            rad1, t1 = sa.rec2pol(np.array(key_radial1)[:2].reshape((-1,2)))[0]
            rad2, t2 = sa.rec2pol(np.array(key_radial2)[:2].reshape((-1,2)))[0]

            sho = status["shape_rst"]["obj"]
            ell_r1 = sho.calc_radius(t1)
            ell_r2 = sho.calc_radius(t2)

            dr1 = rad1 - ell_r1
            dr2 = rad2 - ell_r2

            print(f'DTPanel:   * radial {xspar["radial_mode"]} between {xspar["radial_bounds"]} = [{dr1:.2f} + r, {dr2:.2f} + r]')
            xs_bounds['drs'] = (dr1, dr2)
        else:
            raise Exception(f"DTPanel: unrecognized 'radial mode' = {xspar['radial_mode']}")

        # print('xs_bounds =', xs_bounds)

        # 2. Prepare data
        ## Turn cartesian (x,y) into polar (r,theta)
        
        # ridge_ids = uu.read_face_ids_material(CODE["target"], status["ridge_mat_index"])
        # ridge_faces = faces[ridge_ids, :]
        # XY = ridge_faces[:, [1,2]]
        # ridge_pol = sa.rec2pol(XY)                          # (r,theta)
        # ridge_rtz = np.c_[ridge_pol, ridge_faces[:, [3]]]   # (r,theta,z)
        # print('ridge_rtz =', ridge_rtz.shape)

        XY = faces[:, [1,2]]
        faces_pol = sa.rec2pol(XY)                    # (r,theta)
        faces_rtz = np.c_[faces_pol, faces[:, [3]]]   # (r,theta,z)
        # print('faces_rtz =', faces_rtz.shape)

        # 3. Compute the cross-section.
        print('DTPanel: * invoke CrossSecApprox.approx_xsect')
        uu.log(f"DTPanel: invoke CrossSecApprox.approx_xsect.", logfile)

        xsect_verts, fb = csa.approx_xsect(faces_rtz, status["shape_rst"]["obj"], xs_bounds, 
                                           resolution=xspar["resolution"])

        # Create cross-section geometry
        uu.create_curve(xsect_verts, curve_name=xsect_name, 
                     coll_name=pvars["cross_sect_collection"])
        
        pxsect_file = os.path.join(wpath, pvars["cross_sect_save"])
        with open(pxsect_file, 'wb') as file: 
            pickle.dump((xsect_verts, fb), file)

        print(f'DTPanel: * save cross-section: {pxsect_file}')
        uu.log(f'DTPanel: save cross-section to {pxsect_file}.', logfile)

        if pvars["cross_sect"]["show"]:

            print('DTPanel: * assign materials by cross-section functionalities')

            # md = uu.update_mat_dict()
            # print("DEBUG: uu.update_mat_dict() =", mat_dict)

            # Add material for fb["eff_ids"] (Non-outliers)
            obj = bpy.data.objects[CODE["target"]]
            for id in fb["eff_ids"]:
                obj.data.polygons[id].material_index = mat_dict["effective"]

            # Add material for non-effective (outliers)
            ids_outliers = set(fb["coverage_ids"]) - set(fb["eff_ids"])
            for id in ids_outliers:
                obj.data.polygons[id].material_index = mat_dict["non-effective"]

            # Set view to MATERIAL mode
            bpy.context.space_data.shading.type='MATERIAL'

            # Material has been re-assigned.
            status["ridge"] = False

        # end if

        status["cross_section"] = True
        status["xsect_rst"] = {"name": xsect_name, "bounds": xs_bounds}
        print("DTPanel: Approx XSect Done;\n    * status =", status, '\n')
        uu.log(f"DTPanel: approx xsect is done.", logfile)
        return {'FINISHED'}


    # Force to have finished shape before enabling
    @classmethod
    def poll(cls, context):
        workable = False
        if status["shape"]:
            workable = True

        return workable


class WM_OT_Make_Bridge(bpy.types.Operator):
    """Make a bridge model"""
    bl_label = "Make Bridge"
    bl_idname = "wm.add_bridge"

    def execute(self, context):
        global status
        global pvars
        global faces
        global keypoints

        print("DTPanel: Making bridge")
        uu.log('DTPanel: create a bridge model', logfile)

        print('DTPanel: * invoke UUtils.make_bridge')
        uu.make_bridge(status["shape_rst"]["name"], 
            status["xsect_rst"]["name"], status["xsect_rst"]["bounds"]["angles"])

        status["bridge"] = True

        print("DTPanel: Make Bridge Done;\n    * status =", status)
        uu.log(f"DTPanel: making bridge is done.", logfile)
        return {'FINISHED'}

    # Force to have finished cross-section before enabling
    @classmethod
    def poll(cls, context):
        workable = False
        if status["cross_section"]:
            workable = True

        return workable


class WM_OT_Reload_Config(bpy.types.Operator):
    """Reload configuration json"""
    bl_label = "Reload json"
    bl_idname = "wm.reload_cfg"

    def execute(self, context):
        global pvars
        global config_file

        print(f"DTPanel: Reload configuration {config_file}")
        with open(config_file) as f:
            # Read pvars from cfg
            pvars = json.load(f)
            assert len(pvars) > 0, f"Configuration file ({pcfg}) error"


        print("DTPanel: Reload Config Done.")
        uu.log(f"DTPanel: Reload Config Done.", logfile)
        return {'FINISHED'}


class WM_OT_Clear_Bridge(bpy.types.Operator):
    """Remove shape, cross-sect, and bridge"""
    bl_label = "Clear bridge"
    bl_idname = "wm.clear_bridge"

    def execute(self, context):
        global pvars
        global config_file
        global status

        print(f"DTPanel: Clear bridge")

        # raise Exception("NOT YET IMPLEMENT")

        # if bpy.context.object.mode == 'EDIT':
        #     bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')
        try:
            bpy.data.objects['bridge'].select_set(True)
        except Exception as err:
            print("DTPanel: err =", err)
        
        try:
            bpy.data.objects['shape'].select_set(True)
        except Exception as err:
            print("DTPanel: err =", err)
        
        try:
            bpy.data.objects['xsect'].select_set(True)
        except Exception as err:
            print("DTPanel: err =", err)

        bpy.ops.object.delete()

        status["ridge"] = False
        status["shape"] = False
        status["cross_section"] = False

        print("DTPanel: Clear Bridge Done.")
        uu.log(f"DTPanel: Clear Bridge Done.", logfile)
        return {'FINISHED'}


##############################################################################################
        
def register():

    RegQueue = [DT_MainPanel, WM_OT_AddRef, WM_OT_MoveToWorldOrigin, WM_OT_AddRefPlane,
                WM_OT_Iden_Ridge, WM_OT_Approx_Shape, WM_OT_Approx_XSect, WM_OT_Make_Bridge,
                WM_OT_Reload_Config, WM_OT_Clear_Bridge]

    print('DTPanel: Registering:', RegQueue)
    for clo in RegQueue:
        bpy.utils.register_class(clo)    

    bpy.types.Scene.plate_offset = FloatProperty(
        name = "Offset",
        description = "offset",
        default = 1.0,
        min = 0.0,
        max = 5.0
        )
    bpy.types.Scene.plate_thickness = FloatProperty(
        name = "thickness",
        description = "thickness",
        default = 2.0,
        min = 0.0,
        max = 5.0
        )

    
def unregister():

    RegQueue = [DT_MainPanel, WM_OT_AddRef, WM_OT_MoveToWorldOrigin, WM_OT_AddRefPlane,
                WM_OT_Iden_Ridge, WM_OT_Approx_Shape, WM_OT_Approx_XSect, WM_OT_Make_Bridge,
                WM_OT_Reload_Config, WM_OT_Clear_Bridge]

    for clo in RegQueue[::-1]:
        print('DTPanel: Unregister', clo)
        bpy.utils.unregister_class(clo)    


if __name__ == '__main__':
    register()

