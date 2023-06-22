"""
Filling holes
"""

import bpy
import bmesh


class FillCriteria:
    '''
    Exclude maximal-distance group
    '''

    def __init__(self, AllGs):
        self.maxdist = 0
        for g in AllGs:
            if g[-1] > self.maxdist:
                self.maxdist = g[-1]
        # end for            
        
    def test(self, g):
        return g[-1] < self.maxdist



def fillByEdgeClusters(target_name="Target", final='Finished'):
    
    ####################################
    # 1. Read mesh info of the target
    ####################################
    target = bpy.data.objects[target_name]
    
    ############################################################
    # 2. Convert mesh info to bmesh for efficient processing
    ############################################################    
    bm = bmesh.new()
    tmp_mesh = target.data.copy()
    tmp_mesh.transform(target.matrix_world)
    bm.from_mesh(tmp_mesh)    
    
#    print('bmesh =', bm)    
#    #print('dir(bm)=', dir(bm))
#    print('bm.verts=', bm.verts)
#    print('bm.edges=', bm.edges)
#    print('bm.faces=', bm.faces)


    # https://wiki.blender.org/wiki/Source/Modeling/BMesh/Design
    # > "Loops define the boundary loop of a face. Each loop logically corresponds to an edge, though the loop is local to a single face so there will usually be more than one loop per edge (except at boundary edges of the surface)."
#    print('bm.loops=', bm.loops)
    
#    print('dir(bm.edges)=', dir(bm.edges))
    
#    for i, e in enumerate(bm.edges):
##        print(e)
#        print('* index =', e.index)
#        
#        for f in e.link_faces:
#            print('* ', f)
#    
#            
#        if i > 2:
#            break

#    i = 3

    ############################################################
    # 3. Refresh edge information
    ############################################################

    bm.edges.ensure_lookup_table()

#    #print('getitem=', bm.edges.__getitem__(i))
#    print('bm.edges[i]=', bm.edges[i])
#    print('bm.edges[i].index=', bm.edges[i].index)
#    
#    print('bm.edges[i].verts=', bm.edges[i].verts)
#    v0 = bm.edges[i].verts[0].index
#    v1 = bm.edges[i].verts[1].index
#    print('* v0=', v0)
#    print('* v1=', v1)
#    print('* len(bm.edges[i].link_faces)=', len(bm.edges[i].link_faces))
#        
    # bm.edges.get : Return an edge which uses the verts passed.
    # src: https://docs.blender.org/api/current/bmesh.types.html#bmesh.types.BMEdgeSeq


    ############################################################
    # 4. Create a list of candidate boundary edges
    ############################################################
    show_candidate_edges = False
    
    if show_candidate_edges:
    
        bpy.ops.object.mode_set(mode = 'OBJECT')
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_mode(type="EDGE")
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.mode_set(mode = 'OBJECT')    # Start selecting vertices
    # end show
    
    Candidates = []
    for e in bm.edges:
        if len(e.link_faces) == 1:
            Candidates.append(e.index)

            if show_candidate_edges:
                print('e.index =', e.index)
                target.data.edges[e.index].select = True           
            # end show

    if show_candidate_edges:
        bpy.ops.object.mode_set(mode = 'EDIT')      # End selecting the vertices        
        return  # End the function to ensure its effect is visible.    
    # end show
    
#    print('Candidates=', Candidates)
    
    ############################################################    
    # 5. Group candidates into the boundary groups
    ############################################################
    show_candidate_vertices = False
    if show_candidate_vertices:
    
        bpy.ops.object.mode_set(mode = 'OBJECT')
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.mode_set(mode = 'OBJECT')    # Start selecting vertices
    # end show
    
    Groups = []
    # [([edges ids], [vert ids], total length), (), ...]
    for ie in Candidates:
        v0 = bm.edges[ie].verts[0].index 
        v1 = bm.edges[ie].verts[1].index 

        if show_candidate_vertices:
            print('Candidate', ie, ': v0=', v0, '; v1=', v1)
            target.data.vertices[v0].select = True           
            target.data.vertices[v1].select = True           
        # end show    
        
        # Check if v0 or v1 belongs to any group, assign ie to the group                
        # Otherwise, create a new group
        
        for i, g in enumerate(Groups):
            edges, verts, _ = g
            if v0 in verts:
                Groups[i][0].append(ie)
                Groups[i][1].append(v1)  # v0 is already in.
                break
                
            if v1 in verts:
                Groups[i][0].append(ie)
                Groups[i][1].append(v0)  # v1 is already in.
                break
        else:
            # No vertices belong to any group, this forms a new one.
            Groups.append( [[ie], [v0, v1], 0] )
        # end for g /else
    # end for ie

    if show_candidate_vertices:
        bpy.ops.object.mode_set(mode = 'EDIT')      # End selecting the vertices        
        return  # End the function to ensure its effect is visible.    
    # end show
    
    for i, g in enumerate(Groups):
        edges, verts, _ = g
        L = 0
        for ie in edges:
            L += bm.edges[ie].calc_length()
        Groups[i][2] = L
        
#    print('Groups=', Groups)
#    print('len(Groups)=', len(Groups))
#    for g in Groups:
#        print('* # edges =', len(g[0]), '; lenght=', g[2])


    ############################################################        
    # 6. Fill the hole
    ############################################################    
    
    fill_criteria = FillCriteria(Groups)
    
    # 6.1 Select vertices in the group and fill the hole
    
    # Clear unwanted vertices        
    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj = bpy.context.active_object
    bpy.ops.object.mode_set(mode = 'EDIT') 
    bpy.ops.mesh.select_mode(type="VERT")

#    print('bpy.context.active_object=', bpy.context.active_object)
    bpy.context.view_layer.objects.active = target
#    print('bpy.context.active_object=', bpy.context.active_object)

    # Start selecting the vertices
    
    ### Test selecting vertices
    # bpy.ops.mesh.select_all(action = 'DESELECT')
    # bpy.ops.object.mode_set(mode = 'OBJECT')
    # obj.data.vertices[5].select = True
    # target.data.vertices[8].select = True
    # bpy.ops.object.mode_set(mode = 'EDIT')

    for i, g in enumerate(Groups):
#        print('* Group %d'%i, g)
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

#        print('  * v=', end=' ')
        for v in g[1]:
#            print(v, end='; ')
            target.data.vertices[v].select = True            
#        print()        
        bpy.ops.object.mode_set(mode = 'EDIT')

                
        # 6.2 Fill the hole of the selected vertices
        if fill_criteria.test(g):
            print("Fill group %d"%i, ':', g[-1])        
            bpy.ops.mesh.edge_face_add()
            
    

    # ?. Finalize
    # Create new mesh info
    #me = bpy.data.meshes.new(final)
    #bm.to_mesh(me)
    #ob = bpy.data.objects.new(final, me)
    #context = bpy.context 
    #context.collection.objects.link(ob)
    bm.free()    


# end fillByEdgeCluster    


    
if __name__ == '__main__':
    print("\n\nMain")
    fillByEdgeClusters("Target")

