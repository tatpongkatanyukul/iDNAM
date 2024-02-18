"""
Ridge Identification Functions

Derived from
* 
"""

import numpy as np

def iden_ridge(faces, keypoints, hparams):
    '''
    ridge_ids = ri.iden_ridge(faces, keypoints, pvars)
    * faces:        np.array: face.material_index, *face.center, *face.normal
    * keypoints:    {"T": np.array(KeyT), "Tp": np.array(KeyTp), "C": np.array(KeyC)}
    * hparams:        {"criteria": "zmax", "tau": -1, "show": true, "materials": {"ridge": [1,0,0,1], "non-ridge": [0.5,0.5,0.5,1]}}
      * criteria: "zmax"
      * criteria: "z > 0"
    '''

    print("RidgeIden.iden_ridge: hparams =", hparams)

    ridge_ids = np.array([0]) # Dummy
    fb = {}

    # Identify the ridge based on criteria
    if hparams["criteria"] == "zmax":
        zmax = np.max(faces[:,3])
        ridge_ids = np.where( faces[:,3] >=  zmax*hparams["tau"])[0]  
    else:
        # Default: z >= 0
        ridge_ids = np.where( faces[:,3] >=  0)[0]
    
    print("RidgeIden.iden_ridge: ridge face count =", len(ridge_ids))
    
    print("RidgeIden.iden_ridge: done.")
    return ridge_ids, fb


if __name__ == '__main__':
    print('RidgeIdenV1.__main__')