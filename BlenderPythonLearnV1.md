# Learn Blender Python

* Accessing object
  * ```bpy.data.objects["<obj name>"]``` 

* Create a new mesh (mesh is the underlying data of the object, but object has other attributes, e.g., constraint)
  * ```bpy.ops.mesh. ...```

* UI / Panel
  * ```invoke``` > ```execute```
  * ```poll``` is "always" running

---
# Tricks

* Coordinate values
  * "apply transform" before reading data, otherwise it may not be updated.

* ```bmesh``` is a very handy tool to work with mesh info

---

# Interesting code

Code examples
* [Aj Wasu's dp2.py with my addition](https://github.com/tatpongkatanyukul/iDNAM/blob/main/dp2_wasu230531_PlusTKv1.py)
* [Aj Wasu's color.py for visualizing ridge finding](https://github.com/tatpongkatanyukul/iDNAM/blob/main/color.py)


## Highlights

```class WM_OT_CutByPlaneXY(bpy.types.Operator)``` in [```dp2_wasu230531_PlusTKv1.py```](https://github.com/tatpongkatanyukul/iDNAM/blob/main/dp2_wasu230531_PlusTKv1.py)

```
        # cut
        bpy.ops.object.select_all(action='DESELECT')
        copy = bpy.data.objects["Dup"]
        copy.select_set(True)                                  ## Select object
        bpy.context.view_layer.objects.active = copy           ## Select object

        #bpy.ops.object.editmode_toggle()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')               ## Select all meshes in the object
```

* Mesh is an underlying data inside object. It's kinda Object/Edit mode in Blender interaction

---

```class WM_OT_CutByPlaneXY(bpy.types.Operator)```

```
    def draw(self, context):
        layout = self.layout
        obj = bpy.data.objects["Refplane"]
        col = layout.column()
        col.label(text="Rotation:")
        col.prop(obj, "rotation_euler", index=0, text="X")        
        col.label(text="Move up-down")
        col.prop(obj, "location", index=2, text="Z")        

```
* ```rotation_euler``` and ```location``` are properties of the object ```obj```

---

```class WM_OT_MirrorDup```

```
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        I = bpy.data.objects["I1"]
        Id = bpy.data.objects["I2"]
        D = bpy.data.objects["Dup"]
        p1 = I.location
        p2 = Id.location            
        m = p1 - p2
        D.location +=m
        bpy.ops.object.transform_apply()                                     ## Update coordinates
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
```
* Actually, ```D.location +=m``` alone can move the objects, but to have their coordinate information updated we need to do ```bpy.ops.object.transform_apply()```

---

```class WM_OT_MakeMaster```

Tricks of using [```bmesh```](https://docs.blender.org/api/current/bmesh.html), allowing more efficient way to manipulate mesh

```
        sobj = bpy.data.objects["SCAN"]
        dobj = bpy.data.objects["Dup"]
        bm = bmesh.new()

        #for object in bpy.context.selected_objects:
        self.add_mesh_to_bmesh(bm, sobj.data, sobj.matrix_world)           ## location, rotation, scale
        self.add_mesh_to_bmesh(bm, dobj.data, dobj.matrix_world)

        mesh = bpy.data.meshes.new('MASTER')
        
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(mesh)
        mesh.update()
        bm.free()

        obj = bpy.data.objects.new('MASTER', mesh)
        obj.color = (1, 0, 1, 1)     
        bpy.context.collection.objects.link(obj)
```

* Create a bmesh object ```bm = bmesh.new()```
* Copy object mesh into bmesh (```bm``` variable) ```self.add_mesh_to_bmesh(bm, sobj.data, sobj.matrix_world)```
* Manipute mesh info with bmesh functionalities, e.g., ```bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0)```
* Copy mesh info from bmesh back to the data mesh ```bm.to_mesh(mesh)```
* Link mesh data to the object ```obj = bpy.data.objects.new('MASTER', mesh)```
* Link the object to the collection (otherwise, it might not be visible) ```bpy.context.collection.objects.link(obj)```

---

```class WM_OT_MakePlate```

```
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
```

* Copy mesh data to bmesh ```bm.from_mesh(obj.data)```
* Navigate vertices, edges, and faces info in bmesh ```gv = [v for v in bm.verts if v.select ]```, ```bm.edges```, ```bm.faces```

---



