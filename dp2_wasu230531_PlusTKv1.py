bl_info = {
    "name": "DT Panel",
    "blender": (3, 50, 0),
    "location": "View3D > Sidebar > Dental Workflow",
    "category": "Object",
}

import bpy
#from bpy.props import PointerProperty
from bpy.props import IntProperty, FloatProperty
from mathutils import Vector
from mathutils import Matrix 
from math import radians, atan
import bmesh
from bmesh.types import BMVert
from mathutils.bvhtree import BVHTree

class DT_MainPanel(bpy.types.Panel):
    
    bl_idname = 'DT_PT_MainPanel'
    bl_label = 'DT_Workflow_Panel'
    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Dental Workflow'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # TK
        row = layout.row()
        row.label(text= "Select nasolabial-scan object")
        row.prop(scene, "snap_to_surface")
        row.operator("wm.addref",text= "Add Ref")
        row = layout.row()
        row.label(text= "Move reference to T and T' point")
        row = layout.row()
        row.operator("wm.movetoworldorigin",text="Move to Origin")
        row = layout.row()
        row.operator("wm.addrefplane",text="Add Ref Plane and I")
        row = layout.row()
        row.label(text= "Move reference I")        
        row = layout.row()
        row.operator("wm.dupwithref",text="Duplicate with Reference")
        row = layout.row()
        row.operator("wm.cutbyplanexy",text="Cut by Plane XY")
        row = layout.row()
        row.operator("wm.cutbyplaneyz",text="Cut by Plane YZ")        
        row = layout.row()
        row.operator("wm.mirrordup",text="Mirror dup and move")
        row = layout.row()
        row.operator("wm.rotatedup",text="Rotate dup at I")
        row = layout.row()
        row.operator("wm.makemaster",text="Make Master")
        row = layout.row()
        row.operator("wm.bisec",text="Bisec Master")
        row = layout.row()
        row.operator("wm.cleanbxy",text="Clean BXY")
        row = layout.row()
        row.operator("wm.makebxye",text="Make BXYE")
        row = layout.row()
        row.operator("wm.cutmaster",text="Cut Master")
        row = layout.row()
        row.operator("wm.makeplate",text="Make Plate")

class WM_OT_AddRef(bpy.types.Operator):
    """Add Reference point"""
    bl_label = "Add Reference point"
    bl_idname = "wm.addref"   
    
    def createRefP(self,objN,location,color,col):
        try: 
            obj = bpy.data.objects[objN]
            #obj.location = Vector((l.x-d.x/2,l.y+d.y/2,0))
            obj.location = location

            # TK
            if bpy.types.Scene.snap_to_surface:
                bpy.context.object.constraints["Shrinkwrap"].target = bpy.data.objects["SCAN"]


        except:
            bpy.ops.mesh.primitive_ico_sphere_add(radius=1, location=location)
            obj = bpy.context.object
            obj.name = objN
            obj.color = color
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)

        
    
    def execute(self, context):
        #NAME = bpy.context.selected_objects[0].name
        
        # rename obj to ref in other model
        objM = bpy.context.selected_objects[0]
        objM.name = "SCAN"
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        
        #not work bound_box not aling use dimension is better
        #om = objM.matrix_world
        #bb = objM.bound_box
        #up_r_conner = om @ Vector((bb[6][0],bb[6][1],bb[6][2]))
        #up_l_conner = om @ Vector((bb[2][0],bb[2][1],bb[2][2]))
        #c_location = Vector(( (bb[6][0]+bb[2][0])/2,(bb[6][1]+bb[2][1])/2,bb[6][2] ))
        up_r_conner = Vector((-15,1,1))
        up_l_conner = Vector((15,1,1))
        c_location = Vector((-15,15,1  ))

        try:
            col = bpy.data.collections["Reference"]
        except:
            col = bpy.data.collections.new("Reference")
            bpy.context.scene.collection.children.link(col)

        self.createRefP("T1",up_r_conner,(0, 0, 1, 1),col)            
        self.createRefP("T1'",up_l_conner,(0, 0, 0.7, 1),col)            
        self.createRefP("C1",c_location,(1, 0, 0, 1),col)            
        
        bpy.context.space_data.shading.color_type = 'OBJECT'

        return {'FINISHED'}
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def invoke(self, context, event):
        try:
            text = bpy.context.selected_objects[0].name            
        except:
            # message here to select object first not use poll 
            return {'CANCELLED'}                             
        return  self.execute(context)
    
    
class WM_OT_MoveToWorldOrigin(bpy.types.Operator):
    """Move to World Origin"""
    bl_label = "Move to World Origin"
    bl_idname = "wm.movetoworldorigin"
    
    def execute(self, context):
        try: 
            bpy.ops.object.select_all( action = 'SELECT' )
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            p1 = bpy.data.objects["T1"].location
            p2 = bpy.data.objects["T1'"].location
            #p3 = bpy.data.objects["C"].location

            #mid point
            m = (p1 + p2) *0.5
            #vector
            v1 = p2 - p1        
            #v2 = p3 - m
            v1.normalize()
            rot = v1.rotation_difference( Vector((1,0,0 ))).to_euler()
            #rot1 = v3.rotation_difference(Vector((0,0,1))).to_euler()
            #print(rot)
            #print(rot1)
            for obj in bpy.data.objects:
                obj.location -= m
            
            # This will change location to 0 for rotate
            bpy.ops.object.transform_apply()                            
            for obj in bpy.data.objects:
                 obj.rotation_euler = rot
            #bpy.ops.object.transform_apply()

            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')            
            p3 = bpy.data.objects["C1"].location
            #p3 =  p3.normalized()
            #rotx = p3.rotation_difference(Vector((-1,1,0))).to_euler()
            #rotx = p3.rotation_difference(Vector((p3.x,p3.y,0))).to_euler()
            rotx = atan(p3.z/p3.y)
            print(rotx)
            bpy.ops.object.transform_apply()         
            for obj in bpy.data.objects:
                #obj.rotation_euler[0] = rotx.x
                obj.rotation_euler[0] = -rotx
            
            #bpy.ops.object.transform_apply()
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            bpy.ops.object.select_all(action='DESELECT')
    
            print("Move Done")
        except Exception as e: 
            print("Error Move " + e)
            #print("Add refernce first")
    
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        try:
            bpy.data.objects["SCAN"]
            bpy.data.objects["T1"]
            bpy.data.objects["T1'"]
            bpy.data.objects["C1"]
            return True
        except:
            return False
    

class WM_OT_AddRefPlane(bpy.types.Operator):
    """Add referent plane"""
    bl_label = "Add Reference Plane and I"
    bl_idname = "wm.addrefplane"
    
    def execute(self, context):
        # This name must be name of objec later 
        d = bpy.data.objects["SCAN"].dimensions
        m_size = max(d[0],d[1])
        col = bpy.data.collections["Reference"]
   
        try:
            obj = bpy.data.objects["Refplane"]
            obj.location = (0,m_size/2,0)
        except:
            bpy.ops.mesh.primitive_plane_add(size=m_size, align='WORLD' )    
            obj = bpy.context.object
            obj.name = "Refplane"
            obj.location = (0,m_size/2,0)
            obj.color = (1, 1, 1, 0.7)
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)        

        m_size = max(d[1],d[2])        
        try:
            obj = bpy.data.objects["RefplaneZ"]
            obj.location = (0,m_size/2,0)
        except:
            bpy.ops.mesh.primitive_plane_add(size=m_size, align='WORLD' )    
            obj = bpy.context.object
            obj.name = "RefplaneZ"
            obj.location = (0,m_size/2,0)
            obj.rotation_euler[1] = radians(90)
            obj.color = (1, 1, 1, 0.7)
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)           
        c_loc = bpy.data.objects["C1"].location
        try: 
            obj = bpy.data.objects["I1"]
            obj.location = (c_loc[0]+10, c_loc[1]+10, c_loc[2]+10)
        except:
            bpy.ops.mesh.primitive_ico_sphere_add(radius=1)
            obj = bpy.context.object
            obj.name = "I1"
            obj.location = (c_loc[0]+10, c_loc[1]+10, c_loc[2]+10)            
            obj.color = (0, 1, 0, 1)       
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
            
        print("Add Ref plane and I done")
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        try:
            bpy.data.objects["SCAN"]            
            bpy.data.objects["C1"]
            return True
        except:
            return False
       

class WM_OT_DupWithRef(bpy.types.Operator):
    """Duplicate with refence"""
    bl_label = "Duplicate with refence"
    bl_idname = "wm.dupwithref"

    def copyRef(self,objN,copyN):
        #delete first if any  NOT WORK object still there
        objs = bpy.data.objects
        #objs.remove(objs[copyN], do_unlink=True)

        obj = bpy.data.objects[objN]
        copy = obj.copy()
        copy.data = copy.data.copy() # linked = False
        copy.name = copyN
        col = bpy.data.collections["Reference"]
        col.objects.link(copy)        
        
    def execute(self, context):
    
        # dup
        obj = bpy.data.objects["SCAN"]
        copy = obj.copy()
        copy.data = copy.data.copy() # linked = False
        copy.name = "Dup"
        copy.color = (0, 0.7, 0, 1)     
        for c in obj.users_collection:
            c.objects.link(copy)

        #dup I to I' ref to move of mirror later
        self.copyRef("I1","I2")
        self.copyRef("T1","T2")
        self.copyRef("T1'","T2'")
        self.copyRef("C1","C2")
        return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        try:
            bpy.data.objects["SCAN"]
            bpy.data.objects["I1"]
            return True
        except:
            return False
    
    
class WM_OT_CutByPlaneXY(bpy.types.Operator):
    """ Cut by plane """
    bl_label = "Cut by plane XY"
    bl_idname = "wm.cutbyplanexy"
    
    def draw(self, context):
        layout = self.layout
        obj = bpy.data.objects["Refplane"]
        col = layout.column()
        col.label(text="Rotation:")
        col.prop(obj, "rotation_euler", index=0, text="X")        
        col.label(text="Move up-down")
        col.prop(obj, "location", index=2, text="Z")        
        

    def execute(self, context):
        plane = bpy.data.objects["Refplane"]
        plane.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        _, rot, _ = plane.matrix_world.decompose()
        v1 = Vector((0.0, 0.0, 1.0))
        v1.rotate(rot.to_euler())
        loc = plane.location
        
        # cut
        bpy.ops.object.select_all(action='DESELECT')
        copy = bpy.data.objects["Dup"]
        copy.select_set(True)
        bpy.context.view_layer.objects.active = copy

        #bpy.ops.object.editmode_toggle()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # plane will be refplane an plane_no will be refplane normal
        # other parameter must investigate
        
        bpy.ops.mesh.bisect(plane_co=loc, plane_no=v1, 
            use_fill=False, clear_inner=True, clear_outer=False, threshold=0.0001, 
            xstart=0, xend=0, ystart=0, yend=0, flip=False)
        bpy.ops.object.editmode_toggle()
        
        # Cutting result with manay mesh 
        # separate them to object
        bpy.ops.mesh.separate(type='LOOSE')
        
        # Choose only one that nearest to I1
        #copyI = bpy.data.objects["I2"]
        objI = bpy.data.objects["I1"]        
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        loc_I = objI.location
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        dup_objs = [obj for obj in bpy.context.scene.objects if obj.name.startswith("Dup")]
        min_length = 10000 # will be refplene size
        min_objx = None
        for objx in dup_objs:
            objx.select_set(True)            
            _, pt_closest, face_normal, _ = objx.closest_point_on_mesh(loc_I)
            o_length = (pt_closest - loc_I).length
            if o_length < min_length:
                min_length = o_length
                min_objx = objx
        
        min_objx.select_set(False)
        bpy.ops.object.delete()
        min_objx.name = "Dup"    
        min_objx.color = (0, 0.7, 0, 1) 
        min_objx.select_set(True)
        #copyI.select_set(True)
        #copyI.parent = min_objx  
        bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'

        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects["Refplane"].select_set(True)
        bpy.context.scene.cursor.location = Vector((0,0,0))
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'   
        return context.window_manager.invoke_props_dialog(self)    

class WM_OT_CutByPlaneYZ(bpy.types.Operator):
    """ Cut by plane """
    bl_label = "Cut by plane YZ"
    bl_idname = "wm.cutbyplaneyz"
    
    def draw(self, context):
        layout = self.layout
        obj = bpy.data.objects["RefplaneZ"]
        col = layout.column()
        col.label(text="Rotation:")
        col.prop(obj, "rotation_euler", index=2, text="Z")        
        # need bool cut left or right here
        # or detect I location to plane ???

           

    def execute(self, context):
        plane = bpy.data.objects["RefplaneZ"]
        plane.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

        _, rot, _ = plane.matrix_world.decompose()
        v1 = Vector((0.0, 0.0, -1.0))
        v1.rotate(rot.to_euler())
        loc = plane.location
        
        # cut
        bpy.ops.object.select_all(action='DESELECT')
        copy = bpy.data.objects["Dup"]
        copy.select_set(True)
        bpy.context.view_layer.objects.active = copy
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # plane will be refplane an plane_no will be refplane normal
        # other parameter must investigate
        
        bpy.ops.mesh.bisect(plane_co=loc, plane_no=v1, 
            use_fill=False, clear_inner=True, clear_outer=False, threshold=0.0001, 
            xstart=0, xend=0, ystart=0, yend=0, flip=False)
        bpy.ops.object.editmode_toggle()
        
        # Cutting result with manay mesh 
        # separate them to object
        bpy.ops.mesh.separate(type='LOOSE')
        #copyI = bpy.data.objects["I2"]
        objI = bpy.data.objects["I1"]

        # Choose only one that nearest to I'
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        loc_I = objI.location
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        dup_objs = [obj for obj in bpy.context.scene.objects if obj.name.startswith("Dup")]
        min_length = 10000 # will be refplene size
        min_objx = None
        for objx in dup_objs:
            objx.select_set(True)            
            _, pt_closest, face_normal, _ = objx.closest_point_on_mesh(loc_I)
            o_length = (pt_closest - loc_I).length
            if o_length < min_length:
                min_length = o_length
                min_objx = objx
        
        min_objx.select_set(False)
        bpy.ops.object.delete()
        min_objx.name = "Dup"    
        min_objx.color = (0, 0.7, 0, 1) 
        min_objx.select_set(True)
        #copyI.select_set(True)        
        #copyI.parent = min_objx  
    
        bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'

        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects["RefplaneZ"].select_set(True)
        bpy.context.scene.cursor.location = Vector((0,0,0))
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'   
        return context.window_manager.invoke_props_dialog(self) 
        
class WM_OT_MirrorDup(bpy.types.Operator):
    """Mirror Dup object"""
    bl_label = "Mirror Dup obj"
    bl_idname = "wm.mirrordup"
    def execute(self, context):
        # mirror here
        bpy.ops.object.select_all(action='DESELECT')
        copy = bpy.data.objects["Dup"]
        copy.select_set(True)
        bpy.data.objects["I2"].select_set(True)
        bpy.data.objects["C2"].select_set(True)
        bpy.data.objects["T2"].select_set(True)
        bpy.data.objects["T2'"].select_set(True)    
        bpy.context.view_layer.objects.active = copy
        bpy.ops.object.parent_set()
        # orient_matrix shold be refplan ??
        bpy.ops.transform.mirror(orient_type='GLOBAL', 
        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
        orient_matrix_type='GLOBAL', 
        constraint_axis=(True, False, False))

        #move dup by locatio I' to I
    
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        I = bpy.data.objects["I1"]
        Id = bpy.data.objects["I2"]
        D = bpy.data.objects["Dup"]
        p1 = I.location
        p2 = Id.location            
        m = p1 - p2
        D.location +=m
        bpy.ops.object.transform_apply() 
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    
        return {'FINISHED'}
    

class DT_RotateDup(bpy.types.Operator):
    bl_label = "Rotate Dup"
    bl_idname = "wm.rotatedup"

    def draw(self, context):
        layout = self.layout
        #col = layout.column()
        obj = bpy.data.objects["Dup"]

        col = layout.column(align=True)
        #col.label(text="Rotation:")
        #col.prop(obj, "rotation_euler", index=0, text="X")
        col.prop(obj, "rotation_euler", index=2, text="Z")        
        #col.label(text="Rotate")
        #row = col.row()
        #row.prop(self, "rotate_z")

    def execute(self, context):        
         print("Run P")          
         return {'FINISHED'}
    
    def invoke(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')        
        D = bpy.data.objects["Dup"]
        I = bpy.data.objects["I2"]
        D.select_set(True)
        I.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.context.scene.cursor.location = I.location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')        
        return context.window_manager.invoke_props_dialog(self)
        
class WM_OT_MakeMaster(bpy.types.Operator):
    """ Make Master plate"""
    bl_label = "Make Master plate"
    bl_idname = "wm.makemaster"


    def add_mesh_to_bmesh(self,bm, mesh, matrix):
        """bm.from_mesh(mesh), but it applies matrix to mesh first"""
        tmp_mesh = None
        try:
            tmp_mesh = mesh.copy()
            tmp_mesh.transform(matrix)
            bm.from_mesh(tmp_mesh)
        finally:
            if tmp_mesh:
                bpy.data.meshes.remove(tmp_mesh)
    
    def execute(self, context):
        #bpy.ops.object.select_all(action='DESELECT')        
        sobj = bpy.data.objects["SCAN"]
        dobj = bpy.data.objects["Dup"]
        bm = bmesh.new()

        #for object in bpy.context.selected_objects:
        self.add_mesh_to_bmesh(bm, sobj.data, sobj.matrix_world)
        self.add_mesh_to_bmesh(bm, dobj.data, dobj.matrix_world)

        mesh = bpy.data.meshes.new('MASTER')
        
        #clean up here
        #bmesh.ops.remove_doubles(bm, verts=[], dist=0)
        # example parameter
        #ret = bmesh.ops.duplicate(
        #          bm,
        #geom=bm.verts[:] + bm.edges[:] + bm.faces[:])
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(mesh)
        mesh.update()
        bm.free()

        obj = bpy.data.objects.new('MASTER', mesh)
        obj.color = (1, 0, 1, 1)     
        bpy.context.collection.objects.link(obj)
        
        print("Make master done")
        return {'FINISHED'}
    
class WM_OT_Bisec(bpy.types.Operator):
    """ Creare bisec obj """
    bl_label = "Create Bisec obj"
    bl_idname = "wm.bisec"

    def bisec(self,ob,plane,name):
        context = bpy.context
        dg = context.evaluated_depsgraph_get()
        scene = context.scene 
        #ob = context.object
        #plane = scene.objects.get("Plane")

        if plane and ob:
            pmw = plane.matrix_world
            face = plane.data.polygons[0]
            plane_co = pmw @ face.center
            plane_no = pmw @ (face.center + face.normal) - plane_co 
            bm = bmesh.new()
            bm.from_object(ob, dg)
            bmesh.ops.transform(bm,
                verts=bm.verts,
                matrix=ob.matrix_world)

            x = bmesh.ops.bisect_plane(bm, geom=bm.faces[:] + bm.edges[:] + bm.verts[:],
                    clear_inner=True,
                    clear_outer=True,
                    plane_co=plane_co,
                    plane_no=plane_no,
            )
            # new object
            me = bpy.data.meshes.new(name)
            #bm.to_mesh(me)
            bm.to_mesh(me)
            ob = bpy.data.objects.new(name, me)
            context.collection.objects.link(ob)

    def makeCurve(self,name):
        obj = bpy.data.objects[name]
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target='CURVE')
        obj.select_set(False)

    def draw(self, context):
        layout = self.layout
        obj = bpy.data.objects["Refplane"]
        col = layout.column()
        col.label(text="Rotation:")
        col.prop(obj, "rotation_euler", index=0, text="X")        
        col.label(text="Move up-down")
        col.prop(obj, "location", index=2, text="Z")        
        
            
    def execute(self, context):
        ob =  bpy.data.objects["MASTER"]
        plane = bpy.data.objects["Refplane"]
        self.bisec(ob,plane,"BXY")
        #bpy.ops.object.select_all(action='DESELECT')
        #self.makeCurve("BXY")
        #bpy.data.objects["BXY"].data.bevel_depth = 0.1
            
        print("Run Bisec")          
        return {'FINISHED'}

    def invoke(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects["Refplane"].select_set(True)
        bpy.context.scene.cursor.location = Vector((0,0,0))
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'   
        return context.window_manager.invoke_props_dialog(self)    

def cleanUpIsland(obj):
    mesh = obj.data
    vall = len(mesh.vertices)
    cutoff = vall * 0.1
    paths={v.index:set() for v in mesh.vertices}
    for e in mesh.edges:
        paths[e.vertices[0]].add(e.vertices[1])
        paths[e.vertices[1]].add(e.vertices[0])
    lparts=[]
    while True:
        try:
            i=next(iter(paths.keys()))
        except StopIteration:
            break
        lpart={i}
        cur={i}
        while True:
            eligible={sc for sc in cur if sc in paths}
            if not eligible:
                break
            cur={ve for sc in eligible for ve in paths[sc]}
            lpart.update(cur)
            for key in eligible: paths.pop(key)
        lparts.append(lpart)
    for lp in lparts:
        print(len(lp))
        if (len(lp) < cutoff):
            vremove = set( [v for v in mesh.vertices if v.index in lp] )
            for v in vremove:
                v.select = True
    
class WM_OT_CleanBXY(bpy.types.Operator):
    """ Clean BXY """
    bl_label = "Clean BXY"
    bl_idname = "wm.cleanbxy"

    def cleanUpNY(self,obj):
        mesh = obj.data
        vremove = set( [v for v in mesh.vertices if v.co[1] < 0 ] )            
        for v in vremove:
            v.select = True

            

    def execute(self, context):
        #bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj = bpy.data.objects["BXY"]
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        self.cleanUpNY(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        #this select from clean 
        bpy.ops.mesh.delete(type='VERT')        
        bpy.ops.object.mode_set(mode='OBJECT')    
         
        cleanUpIsland(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        #this select from clean 
        bpy.ops.mesh.delete(type='VERT')        
        bpy.ops.object.mode_set(mode='OBJECT')    
        print("Run Clean BXY")          
        return {'FINISHED'}

class WM_OT_MAKEBXYE(bpy.types.Operator):
    """ make BXYE """
    bl_label = "Make BXYE"
    bl_idname = "wm.makebxye"
    
    def getX(self,v):
        return v.co[0]

    def cross(self,o, a, b):
        return (a.co[0] - o.co[0]) * (b.co[1] - o.co[1]) - (a.co[1] - o.co[1]) * (b.co[0] - o.co[0])

    def makeEdge(self,obj):
        mesh = obj.data
        bm = bmesh.new()
        verts = [v for v in mesh.vertices]
        verts.sort(key=self.getX)
        #convex hall alg
        # Build lower hull 
        lower = []
        for p in verts:
            while len(lower) >= 2 and self.cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
    
        # Build upper hull
        upper = []
        for p in reversed(verts):
            while len(upper) >= 2 and self.cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)

        # Concatenation of the lower and upper hulls gives the convex hull.
        # Last point of each list is omitted because it is repeated at the beginning of the other list. 
        all =  lower[:-1] + upper[:-1]    
        i = 1    
        e0 =  bm.verts.new(all[0].co)
        st = e0
        while i < len(all):        
            e1 = bm.verts.new(all[i].co)
            bm.edges.new((e0,e1))
            e0 = e1
            i += 1
        bm.edges.new((e0,st))                    
        me = bpy.data.meshes.new("BXYE")
        bm.to_mesh(me)        
        ob = bpy.data.objects.new("BXYE", me)
        context = bpy.context        
        context.collection.objects.link(ob)
        bm.free()

    def execute(self, context):
        obj = bpy.data.objects["BXY"]
        self.makeEdge(obj)
        print("Run Make BXYE")          
        return {'FINISHED'}

class WM_OT_CutMaster(bpy.types.Operator):
    """ Cut master """
    bl_label = "Cut master"
    bl_idname = "wm.cutmaster"

    def cutMaster(self,obj,conv):
    
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        cmesh = conv.data
        mat_rot = Matrix.Rotation(radians(90.0), 3, 'Z')
        for e in cmesh.edges:
            vi0 = e.vertices[0]
            vi1 = e.vertices[1]
            v0 = cmesh.vertices[vi0].co
            v1 = cmesh.vertices[vi1].co
            vd = v1-v0
            enor = vd @ mat_rot
            bmesh.ops.bisect_plane(bm, geom=bm.faces[:] + bm.edges[:] + bm.verts[:],
                    clear_inner=False,
                    clear_outer=True,
                    plane_co=v0,
                    plane_no=enor,
                )
          
        return bm

    def execute(self, context):
        obj = bpy.data.objects["MASTER"]
        conv = bpy.data.objects["BXYE"]
        bm = self.cutMaster(obj,conv)
        # new object
        me = bpy.data.meshes.new("MASTERCUT")
        bm.to_mesh(me)
        ob = bpy.data.objects.new("MASTERCUT", me)
        context = bpy.context 
        context.collection.objects.link(ob)
        bm.free()
        print("Cut master")
        return {'FINISHED'}
    
class WM_OT_MakePlate(bpy.types.Operator):
    """ Make Plate """
    bl_label = "Make Plate"
    bl_idname = "wm.makeplate"

    def execute(self, context):
        obj = bpy.data.objects["MASTERCUT"]
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bvh = BVHTree.FromBMesh(bm)
        
        #should be normal of cutplane
        d = (0, 0, -1) # ray direction
        for face in bm.faces:
            o = face.calc_center_bounds()
            # should be max z 
            o[2] = 50
            loc, norm, idx, dist = bvh.ray_cast(o, d)
            if idx:
                bm.faces[idx].select_set(True)
        #Toggle delete none hit
        for v in bm.verts:
            v.select = not v.select
        gv = [v for v in bm.verts if v.select ] 
        ge = [e for e in bm.edges if e.select ]
        gf = [f for f in bm.faces if f.select ]
        geom = gv[:] + ge[:] + gf[:]
        bmesh.ops.delete(bm, geom=geom, context='VERTS')    
        me = bpy.data.meshes.new("PLATE")
        bm.to_mesh(me)        
        ob = bpy.data.objects.new("PLATE", me)
        context = bpy.context        
        context.collection.objects.link(ob)
        bm.free()

        obj = bpy.data.objects["PLATE"]
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')     
        cleanUpIsland(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        #this select from clean 
        bpy.ops.mesh.delete(type='VERT')        
        bpy.ops.object.mode_set(mode='OBJECT')    
        
        print("Make plate")
        return {'FINISHED'}

        
def register():
    #bpy.types.Scene.prop = PointerProperty(type=bpy.types.Object)
    bpy.utils.register_class(WM_OT_AddRef)    
    bpy.utils.register_class(WM_OT_MoveToWorldOrigin)
    bpy.utils.register_class(WM_OT_AddRefPlane)      
    bpy.utils.register_class(WM_OT_DupWithRef)          
    bpy.utils.register_class(WM_OT_CutByPlaneXY)
    bpy.utils.register_class(WM_OT_CutByPlaneYZ)
    bpy.utils.register_class(WM_OT_MirrorDup)        
    bpy.utils.register_class(DT_MainPanel)
    bpy.utils.register_class(DT_RotateDup)
    bpy.utils.register_class(WM_OT_MakeMaster)
    bpy.utils.register_class(WM_OT_Bisec)
    bpy.utils.register_class(WM_OT_CleanBXY)
    bpy.utils.register_class(WM_OT_MAKEBXYE)
    bpy.utils.register_class(WM_OT_CutMaster)
    bpy.utils.register_class(WM_OT_MakePlate)

    bpy.types.Scene.snap_to_surface = bpy.props.BoolProperty(
        name="Snap to surface",
        description="Snap references to surface",
        default = True)    


def unregister():
    bpy.utils.unregister_class(WM_OT_AddRef)    
    bpy.utils.unregister_class(WM_OT_MoveToWorldOrigin)    
    bpy.utils.unregister_class(WM_OT_AddRefPlane)          
    bpy.utils.unregister_class(WM_OT_DupWithRef)          
    bpy.utils.unregister_class(WM_OT_CutByPlaneXY)
    bpy.utils.unregister_class(WM_OT_CutByPlaneYZ)
    bpy.utils.unregister_class(WM_OT_MirrorDup)
    bpy.utils.unregister_class(DT_MainPanel)
    bpy.utils.unregister_class(DT_RotateDup)
    bpy.utils.unregister_class(WM_OT_MakeMaster)
    bpy.utils.unregister_class(WM_OT_Bisec)
    bpy.utils.unregister_class(WM_OT_CleanBXY)
    bpy.utils.unregister_class(WM_OT_MAKEBXYE)
    bpy.utils.unregister_class(WM_OT_CutMaster)
    bpy.utils.unregister_class(WM_OT_MakePlate)

    del bpy.types.Scene.snap_to_surface


if __name__ == '__main__':
    register()


    