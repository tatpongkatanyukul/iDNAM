import numpy as np

def approx_xsect(faces_rtz, shape_obj, bound_params, 
                 remov_outlier, resolution):
    '''
    xsect_verts, fb = approx_xsect(faces, 
        {"name": shape_name, "obj": dshape}, 
        {"angle_keys": ["T1", "C1"], "radial_bounds": ["RO", "RI"], "reso": 40})    
    '''

    # import pickle
    # with open("C:\\Users\\tatpong\\Desktop\\2024\\Phase1\\Debug_Data.pkl", 'wb') as file: 
    #     pickle.dump((faces_rtz, shape_obj, bound_params, 
    #              remov_outlier, resolution), file)


    print(f"CrossSecApprox.approx_xsect: faces {faces_rtz.shape}, shape {shape_obj}, bounds {bound_params}, resolution {resolution}")

    fb = {}

    phi1, phi2 = bound_params["angles"]

    ell_rs = shape_obj.calc_radius(faces_rtz[:,1])

    rmarks = None
    if bound_params["radial_mode"] == "Z":
    
        z1, z2 = bound_params["zs"] # (inner, outer)

        inners = (faces_rtz[:,0] < ell_rs) & (faces_rtz[:,2] >= z1)

        outers = (faces_rtz[:,0] >= ell_rs) & (faces_rtz[:,2] >= z2)

        rmarks = inners | outers

    elif bound_params["radial_mode"] == "R":

        dr1, dr2 = bound_params['drs']

        rmarks = (faces_rtz[:,0] >= ell_rs + dr1) & \
                 (faces_rtz[:,0] <= ell_rs + dr2)

    else:
        raise Exception(f"Error: radial_mode = {bound_params['radial_mode']}")

    tmarks = (faces_rtz[:,1] >= phi1) & \
             (faces_rtz[:,1] <= phi2)

    segment = faces_rtz[rmarks & tmarks, :]

    # 1.4. Normalize r per elliptical center
    thetas = segment[:,1]
    ell_rs = shape_obj.calc_radius(thetas)
    norm_segment = segment  # Alias
    norm_segment[:,0] = segment[:,0] - ell_rs

    # 1.5. Remove outliers: r that is too large or too small
    if remov_outlier:
        # 1.5.1. Determine Q1, Q3, and iQR
        Qs = [0, 0.25, 0.5, 0.75, 1]
        rQ = {}
        for i, q in enumerate(Qs):
            rQ[i] = np.quantile(norm_segment[:,0], q)
            print('{:.2f}: x = {:.2f}'.format(q, rQ[i]) )

        iQR = rQ[3] - rQ[1]
        #print('iQR =', iQR)

        tau = [rQ[1] - 1.5*iQR, rQ[3] + 1.5*iQR]

        # 1.5.2. Keep only points whose tau[0] < r < tau[1]
        valid_marks = (norm_segment[:,0] > tau[0]) & \
                        (norm_segment[:,0] < tau[1])
        norm_segment = norm_segment[valid_marks, :]
    # end if

    rpmin = np.min(norm_segment[:, 0])
    rpmax = np.max(norm_segment[:, 0])

    tpmin = np.min(norm_segment[:, 1])
    tpmax = np.max(norm_segment[:, 1])

    zpmin = np.min(norm_segment[:, 2])
    zpmax = np.max(norm_segment[:, 2])

    print(f"    * 1. Polar data is ready: r in [{rpmin:.3f}, {rpmax:.3f}],", end=" ")
    print(f"theta in [{tpmin:.3f}, {tpmax:.3f}],", end=" ")
    print(f"z in [{zpmin:.3f}, {zpmax:.3f}]; shape = {norm_segment.shape}")

    # 2. Approximate the cross-section outline    
    normrz = norm_segment[:, [0,2]]

    # 2.1. Discretize the r-z datapoints into bins
    # Work on r-z projection
    
    rs = np.linspace(rpmin, rpmax, resolution)

    bins = []
    # Go through each bin
    zpmax = zpmin
    for i in range(resolution-1):
        rpmin = rs[i]
        rpmax = rs[i+1]
        mark = (normrz[:,0] >= rpmin) & (normrz[:,0] < rpmax)

        # print(i, f"[{rpmin} , {rpmax}]: sum(mark) =", np.sum(mark))

        if np.sum(mark) > 0:
            zpmax = np.max(normrz[mark, 1])
        bins.append([rpmin, zpmax])
    # end for i
    bins.append([rpmax, zpmax])

    bins = np.array(bins)

    # 2.2. Correct the peak and the trailing edge
    #      so that no point lies above its bin.
    id_bin_zmax = np.argmax(bins[:,1])
    bin_zmax = bins[id_bin_zmax,1]

    # Outer side uses the trailing edge.
    backrows = np.c_[bins[(id_bin_zmax+1):, 0], 
                     bins[id_bin_zmax:-1, 1]]

    corrected_bins = np.r_[bins[:(id_bin_zmax+1),:], backrows] # (N,2) of [r,z]

    # [r, z] of shape (N, 2).
    # Make vertices in [r, z, 0]
    N, _ = corrected_bins.shape
    verts = np.c_[corrected_bins, np.zeros((N,1))]   # (N,3) of [r, z, 0] 

    print(f"    * 2. Discretized cross-section is ready: {verts.shape}")
    print("CrossSecApprox.approx_xsect: done.")
    return verts, fb
