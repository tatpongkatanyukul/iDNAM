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
import BUtilsV4 as uu
import RidgeIdenV3 as ri
import ShapeApproxV4 as sa
import CrossSecApproxV4 as csa

import importlib
# importlib.reload(ab)
importlib.reload(uu)
importlib.reload(ri)

wpath = "."
logfile = "log.txt"
config_file = ""
pvars = {}               # Dummy; loaded and set by AutoBridge.py
faces = np.array([])     # Dummy: set by WM_OT_Iden_Ridge
keypoints = {}           # Dummy: set by WM_OT_Iden_Ridge

vert_double_threshold = 0.1
dissolve_threshold = 0.01

status = {"aligned": False, 
          "data_ready": False, 
          "ridge": False, "ridge_mat_index": None,
          "shape": False, "shape_rst": None,
          "cross_section": False, "xsect_rst": None}

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

        # print("DTPanelV3: DEBUG")
        # print("type(row) =", type(row))
        # print("row.operator.__doc__ = ")
        # print(row.operator.__doc__)
        # print("DTPanelV3: DEBUG ...")


        
               
def createRefP(name,location,color,collection):
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

        # Rename selected obj to the target name
        obj = bpy.context.selected_objects[0]
        obj.name = uu.CODE["target"]

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
        if False:
            me = obj.data

            acc = Vector((0,0,0))
            count = 0
            for f in me.polygons:    
                acc += f.normal
                count += 1

            acc = acc / count
            rot = acc.rotation_difference( Vector((0,0,1))).to_euler()
            obj.rotation_euler = rot
            bpy.ops.object.transform_apply()
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        # Create reference points, T, Tp, and C
        initT = Vector((-15,1,1))      # T's initial value
        initTp = Vector((15,1,1))       # Tp's initial value
        initC = Vector((-15,15,1  ))    # C's initial value

        try:
            coll = bpy.data.collections["Reference"]
        except:
            coll = bpy.data.collections.new("Reference")
            bpy.context.scene.collection.children.link(coll)

        createRefP(uu.CODE["T"], initT, (0, 0, 1, 1),coll)            
        createRefP(uu.CODE["Tp"], initTp, (0, 0.8, 1, 1),coll)            
        createRefP(uu.CODE["C"], initC,(1, 0, 0, 1),coll) 
        createRefP(uu.CODE["RO"], initC,(1, 0, 0, 1),coll)
        createRefP(uu.CODE["RI"], initC,(1, 0, 0, 1),coll)
        
        bpy.context.space_data.shading.color_type = 'OBJECT'

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

        try: 

            # Align the target and keypoints

            ## * Select the desired objects
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[uu.CODE["target"]].select_set(True)
            bpy.data.objects[uu.CODE["T"]].select_set(True)        
            bpy.data.objects[uu.CODE["Tp"]].select_set(True)        
            bpy.data.objects[uu.CODE["C"]].select_set(True)
            bpy.data.objects[uu.CODE["RO"]].select_set(True)
            bpy.data.objects[uu.CODE["RI"]].select_set(True)
            
            ## * Get world coordinates of key points
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            p1 = bpy.data.objects[uu.CODE["T"]].location
            p2 = bpy.data.objects[uu.CODE["Tp"]].location

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
            
            #    Bring object origins (particularly C) back to their geometries, to have the object's world coord
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')            
            p3 = bpy.data.objects[uu.CODE["C"]].location
            rotx = atan(p3.z/p3.y)

            #    Bring object origins to (0,0,0), ready for rotation around (0,0,0)
            bpy.ops.object.transform_apply()                            

            for obj in bpy.context.selected_objects:                
                obj.rotation_euler[0] = -rotx
            
            ##   Finish the rotation
            bpy.ops.object.transform_apply()
            ##   Reset the object origins to their geometries
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            bpy.ops.object.select_all(action='DESELECT')
    

            status["aligned"] = True
            print("DTPanel: Align/Move Done\n")
        except Exception as e: 
            print("DTPanel: Error Move " + e)
    
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        try:
            bpy.data.objects[uu.CODE["target"]]
            bpy.data.objects[uu.CODE["T"]]
            bpy.data.objects[uu.CODE["Tp"]]
            bpy.data.objects[uu.CODE["C"]]
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
        d = bpy.data.objects[uu.CODE["target"]].dimensions
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
            bpy.data.objects[uu.CODE["target"]]            
            bpy.data.objects[uu.CODE["C"]]
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

        print("DTPanel: Identifying ridge")

        ridge_ids = np.array([])  # Dummy: set by ri.iden_ridge

        ################################################
        # Select the "SCAN" object
        ## Selection block : START  
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object
        for obj in selected_objects:
            obj.select_set(False)

        success = False
        found = False
        for collection in [c for c in bpy.data.collections]:
            for obj in collection.objects:
                if obj.name in [uu.CODE['target']]:
                    bpy.context.view_layer.objects.active = obj
                    selection = obj.select_get()
                    obj.select_set(True)

                    # Do WHAT WE WANT to the selected
                    # Make a bridge model of the "SCAN" object

                    print("DTPanel: * read context")
                    # Read context from Blender
                    # faces = [material, center.x, center.y, center.z, normal.x, normal.y, normal.z]
                    # keypoints = {"T": T, "Tp": Tp, "C": C}
                    faces, keypoints = uu.read_context()

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

                    print('DTPanel: * invoke RidgeIden.iden_ridge')
                    uu.log(f"DTPanel: invoke RidgeIden.iden_ridge.", logfile)
                    ridge_ids, fb = ri.iden_ridge(faces, keypoints, pvars["ridge"])
                    
                    obj.select_set(selection)
                    found = True
                    break
                # end if
            # end for obj
            if found:
                break
        # end for collection                

        # restore saved state of selection
        bpy.context.view_layer.objects.active = active_object
        for obj in selected_objects:
            obj.select_set(True)
        ## Selection block : END
        #############################################

        print('DTPanel: * assign materials by ridge')

        # Clear materials
        uu.clear_materials(clear_target="TARGET")

        # Update material dict
        uu.update_mat_dict()

        # Add material for non-ridge
        uu.assign_face_material([], "non-ridge", pvars["ridge"]["materials"]["non-ridge"])
                                    
        # Add material for ridge
        ridge_mat_id = uu.assign_face_material(ridge_ids, "ridge", pvars["ridge"]["materials"]["ridge"])

        if pvars["ridge"]["show"]:
            bpy.context.space_data.shading.type='MATERIAL'

        status["ridge"] = True
        status["ridge_mat_index"] = ridge_mat_id
        print("DTPanel: Iden Ridge Done;\n    * status =", status, '\n')
        uu.log(f"DTPanel: identifying ridge is done.", logfile)
        return {'FINISHED'}


    # Force to select an object before enabling the button.
    @classmethod
    def poll(cls, context):
        workable = False
        if len(context.selected_objects) == 1:
            if context.selected_objects[0].name == uu.CODE["target"]:
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

        model_name = "ell"
        shape_name = "ridge"

        print("DTPanel: Approximating ridge shape")

        # Read ridge
        print(f'DTPanel: * read ridge of {uu.CODE["target"]} having material index {status["ridge_mat_index"]}')
        uu.log(f'DTPanel: read ridge of {uu.CODE["target"]} having material index {status["ridge_mat_index"]}.', logfile)

        ridge_ids = uu.read_face_ids_material(uu.CODE["target"], status["ridge_mat_index"])

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
        if status["ridge"]:
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

        xsect_name = "xsect"
        print("DTPanel: Approximating ridge cross-section")

        xspar = pvars["cross_sect"]

        print("DTPanel: * read key locations")

        xs_bounds = {}
        # 1. Read key locations
        key_angle1  = uu.get_object_location(xspar["angle_keys"][0])
        key_angle2  = uu.get_object_location(xspar["angle_keys"][1])
        key_radial1 = uu.get_object_location(xspar["radial_bounds"][0])
        key_radial2 = uu.get_object_location(xspar["radial_bounds"][1])

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
            rad1 = sa.rec2pol(np.array(key_radial1)[:2].reshape((-1,2)))[0,0]
            rad2 = sa.rec2pol(np.array(key_radial2)[:2].reshape((-1,2)))[0,0]
            print(f'DTPanel:   * radial {xspar["radial_mode"]} between {xspar["radial_bounds"]} = [{rad1:.2f}, {rad2:.2f}]')
            xs_bounds['rs'] = (rad1, rad2)
        else:
            raise Exception()

        # print('xs_bounds =', xs_bounds)

        # 2. Prepare data
        ## Turn cartesian (x,y) into polar (r,theta)
        
        # ridge_ids = uu.read_face_ids_material(uu.CODE["target"], status["ridge_mat_index"])
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

        xsect_verts, fb = csa.approx_xsect(faces_rtz, status["shape_rst"]["obj"], xs_bounds, xspar["resolution"])

        # Create cross-section geometry
        uu.create_curve(xsect_verts, curve_name=xsect_name, 
                     coll_name=pvars["cross_sect_collection"])
        
        pxsect_file = os.path.join(wpath, pvars["cross_sect_save"])
        with open(pxsect_file, 'wb') as file: 
            pickle.dump((xsect_verts, fb), file)

        print(f'DTPanel: * save cross-section: {pxsect_file}')
        uu.log(f'DTPanel: save cross-section to {pxsect_file}.', logfile)

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


class WM_OT_Realod_Config(bpy.types.Operator):
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



##############################################################################################
        
def register():

    RegQueue = [DT_MainPanel, WM_OT_AddRef, WM_OT_MoveToWorldOrigin, WM_OT_AddRefPlane,
                WM_OT_Iden_Ridge, WM_OT_Approx_Shape, WM_OT_Approx_XSect, WM_OT_Make_Bridge,
                WM_OT_Realod_Config]

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
                WM_OT_Realod_Config]

    for clo in RegQueue[::-1]:
        print('DTPanel: Unregister', clo)
        bpy.utils.unregister_class(clo)    


if __name__ == '__main__':
    register()

