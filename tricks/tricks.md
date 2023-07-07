# Learn tricks

## Create a new mesh object

Not quite right
```
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

```

Correction
```
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
        context = bpy.context        
        context.collection.objects.link(ob)
    bm.free()
```



---
