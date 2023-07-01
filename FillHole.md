# Fill Holes

---
# Get Edge Map from Selection

The function may be badly named, but it works fine.

```
def get_selected_edge_map():
    """
    return edge_map as numpy.array([[eid, v0, v1], [eid, v0, v1], ...])
    """

    mode = bpy.context.active_object.mode
    # we need to switch from Edit mode to Object mode so the selection gets updated
    bpy.ops.object.mode_set(mode='OBJECT')
                
    edge_map = np.array([[e.index, e.vertices[0], e.vertices[1]] for e in bpy.context.active_object.data.edges if e.select])
    # back to whatever mode we were in
    bpy.ops.object.mode_set(mode=mode)
        
    return edge_map
```

---

# Take Boundary Edges From Edge Map

It works fine.

```
def take_boundary_edges(edge_map, target="PLATE"):
    """
    return edge_map whose entries are boundary edges
    """    
    
    if len(edge_map) == 0:
        return []
    
    mode = bpy.context.active_object.mode
    # we need to switch from Edit mode to Object mode so the selection gets updated
    bpy.ops.object.mode_set(mode='OBJECT')
                
    target = bpy.data.objects[target]
    bm = bmesh.new()
    tmp_mesh = target.data.copy()
    tmp_mesh.transform(target.matrix_world)
    bm.from_mesh(tmp_mesh) 

    bm.edges.ensure_lookup_table()
                    
    boundary_edge_map = np.zeros((0,3))           
    for i, eid in enumerate(edge_map[:,0]):
        e = bm.edges[eid]
        # print(eid, e.verts[0].index, e.verts[1].index, e.is_boundary)
        if e.is_boundary:
            boundary_edge_map = np.r_[boundary_edge_map, edge_map[[i],:]]
    
    # back to whatever mode we were in
    bpy.ops.object.mode_set(mode=mode)
    bm.free()

    return boundary_edge_map
```

---

# Select Edges by Edge IDs provided

It works fine.

```
def select_edges(edges, target="PLATE"):
    '''
    edges: [eid, ...]
    '''

    if len(edges) == 0:
        return


    bpy.ops.object.mode_set(mode = 'EDIT') 
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.context.view_layer.objects.active = bpy.data.objects[target]

    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

    for eid in edges:
        print(eid, end='; ')
        
        bpy.data.objects[target].data.edges[int(eid)].select = True    
    
    bpy.ops.object.mode_set(mode = 'EDIT')
```

# Fill Hole Per Selected Edges

This works badly.
It may be the hole filling algorithm itself that I have to work on.

Ideas/To Do's:
* Do surface interpolation. Then fill the edges and vertices of the interpolated area.
* Aj Wasu suggests: ```bmesh.ops.holes_fill(bm, edges, sides)```

```    
def fill_hole(target="PLATE"):

    bpy.context.view_layer.objects.active = bpy.data.objects[target]
    
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.mode_set(mode = 'EDIT')
    
    bpy.ops.mesh.edge_face_add()
```
