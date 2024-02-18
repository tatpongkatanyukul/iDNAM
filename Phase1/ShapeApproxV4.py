import numpy as np

# import sys
# packages_path = r"C:\Users\ASUS\AppData\Roaming\Python\Python310\site-packages"
# sys.path.insert(0, packages_path )

# import scipy as sp
# print("sp =", sp.__version__)


#######################
## Ellipse Utilities
#######################

def rec2pol(RPoints):
    '''
    RPoints     [x,y] as np.array (N,2)

    return (r, theta) as np.array (N,2)
    '''
    x = RPoints[:,0]
    y = RPoints[:,1]

    r = np.sqrt(x**2 + y**2)
    th = np.arctan2(y, x)

    return np.c_[r, th]


def pol2rec(PPoints):
    '''
    PPoints [r,theta] as np.array (N,2)

    return  (x, y)    as np.array (N,2)
    '''

    r = PPoints[:,0]
    theta = PPoints[:,1]
    x = r*np.cos(theta)
    y = r*np.sin(theta)

    return np.c_[x, y]


def grad_descend(jacf, x_train, y_train, p0, params, lossf=None):

    raise Exception("Function ```grad_descend``` has not yet been implemented.")

    p = p0
    losses = []

    # Dummy

    return p, losses


def ell_jac(p, x_train, y_train):

    raise Exception("Function ```ell_jac``` has not yet been implemented.")

    return 0


def ell_loss(params, theta, radius):

    rp = ell_radius(theta, *params)
    
    return np.mean( (rp - radius)**2 )


def circle_loss(r, theta, radius):

    rp = r * np.ones(theta.shape)

    return np.mean( (rp - radius)**2 )


def ell_radius(th, alpha, beta, yc=0):
    al2 = alpha**2
    be2 = beta**2
    cos_t = np.cos(th)
    sin_t = np.sin(th)
    
    a = cos_t**2/al2 + sin_t**2/be2
    b = - 2 * yc * sin_t/be2
    c = yc**2/be2 - 1
    
    denom = 2*a    
    term = np.sqrt(b**2 - 4*a*c)
    r1 = (-b + term)/denom
    return r1


def safe_ell_radius(th, gamma, beta, yc):
    '''
    gamma = 1/alpha
    beta = 1/beta    
    '''

    raise Exception("Function ```safe_ell_radius``` has not yet been tested.")

    gam2 = gamma**2
    rho2 = rho**2
    cos_t = np.cos(th)
    sin_t = np.sin(th)
    
    a = gam2 * cos_t**2 + rho2 * sin_t**2
    b = -2 * yc * rho2 * sin_t
    c = rho2 * yc**2 - 1
    
    denom = 2*a    
    term = np.sqrt(b**2 - 4*a*c)
    r1 = (-b + term)/denom
    return r1


def gen_shape(th, params):
    r = ell_radius(th, *params)
    XY = pol2rec(np.c_[r, th])
    return XY[:,0], XY[:,1]


class Ell2D_shape:
    def __init__(self, params):
        self.params = params

    def gen_shape(self, thetas):
        return gen_shape(thetas, self.params)

    def calc_radius(self, thetas):
        return ell_radius(thetas, *self.params)


class circ_xy:
    def __init__(self, r):
        self.r = r

    def gen_shape(self, ts):
        return self.r*np.cos(ts), self.r*np.sin(ts)


###############################
## approx_shape
###############################

def approx_shape(faces, keypoints, ridge_ids, hparams):
    '''
    shape_obj = sa.approx_shape(faces, keypoints, ridge_ids, hparams)

    hparams: {"fit": "SP.BNDS", "init": "circle", "show": true, "show_reso": 100}
    "fit" options:
        "SP": curve_fit (without bounds); params: "alpha", "beta", "yc"
        "SP.Y0": curve_fit safe ellipse (without bounds); params: "gamma", "rho" ("yc" is fixed to 0)
        "SP.BNDS" (recommended): curve_fit with bounds: bounds = [-mean(r), mean(r)]; params: "alpha", "beta", "yc"
        "GD": gradient descend requires (e.g.,) "gd_params": {"lr": 0.03, "nepochs: 2000}; init = circle.
    "init" options:
        "circle" (default): alpha, beta, yc = mean(r), mean(r), 0
        "manual": requires (e.g.,) "man_params": [1,1,0]
    '''
    print(f"ShapeApprox.approx_shape: fit ellipse ({hparams['fit']})")

    dshape = None
    fb = {"success": False, "rst": {}}

    # 1. Get the ridge data
    ridge_faces = faces[ridge_ids, :]
    XY = ridge_faces[:, [1,2]]

    # 2. Fil ellipse to data
    PolarRT = rec2pol(XY)
    rs, thetas = PolarRT[:,0], PolarRT[:,1]
    meanr = np.mean(rs)
    fb["default_shape_fn"] = circ_xy(meanr)

    aby = (meanr, meanr, 0) # default init = circle
    if hparams["init"] == "manual":
        aby = hparams["man_params"]

    N_params = 3
    w = aby
    if hparams["fit"] == "GD":
        w, losses = grad_descend(ell_jac, thetas, rs, p0=aby, params=hparams["gd_params"]) 
        fb["rst"] = {"w": w, "losses": losses}

    else:

        try:
            import scipy as sp

            if hparams["fit"] == "SP":
                w, pcov = sp.optimize.curve_fit(ell_radius, thetas, rs, p0=aby)
                fb["rst"] = {"w": w, "pcov": pcov}
            elif hparams["fit"] == "SP.Y0":
                N_params = 2
                w, pcov = sp.optimize.curve_fit(ell_radius, thetas, rs, p0=aby[:2])
                fb["rst"] = {"w": w, "pcov": pcov}
            elif hparams["fit"] == "SP.BNDS":
                bnds = (-2*meanr, 2*meanr)
                w, pcov = sp.optimize.curve_fit(ell_radius, thetas, rs, p0=aby, bounds=bnds)
                fb["rst"] = {"w": w, "pcov": pcov}
            else:
                raise Exception(f"Configure 'fit' option {hparams['fit']} is not recognized.")

                


        except Exception as error:
            print("ShapeApprox.approx_shape: error =", error)
            
            raise Exception("If scipy is not installed, consider installing or set json configure to have 'fit': 'GD'.")

    # Compute loss
    loss = ell_loss(w, thetas, rs)
    fb["rst"]["final_loss"] = loss

    # Compute loss of circle model
    loss_circ = circle_loss(meanr, thetas, rs)

    if loss <= loss_circ:
        if N_params == 3:
            print(f"ShapeApprox.approx_shape: final loss = {loss:.3f} (<= {loss_circ:.3f}); alpha={w[0]:.3f}, beta={w[1]:.3f}, yc={w[2]:.3f}.")
        elif N_params == 2:
            print(f"ShapeApprox.approx_shape: final loss = {loss:.3f} (<= {loss_circ:.3f}); alpha={w[0]:.3f}, beta={w[1]:.3f}.")
        fb["success"] = True

        dshape = Ell2D_shape(w)

    else:
        print(f"ShapeApprox.approx_shape: fail to fit. Final loss = {loss:.3f}; default loss = {loss_circ:.3f}.")
        fb["rst"]["circle"] = {"r": meanr, "loss": loss_circ}
    
    print("ShapeApprox.approx_shape: done.")
    return dshape, fb

###############################
## Tests
###############################



######################################################################


if __name__ == "__main__":

    import pickle
    with open(r"./kp.pkl", "rb") as kp_file:
        kpoints = pickle.load(kp_file)

    print("kpoints=", kpoints)

    faces = np.load("./faces.npy")
    print('faces:', faces.shape)

    ridge_ids = np.where( faces[:,3] >=  0)[0]
    print('ridge_ids:', len(ridge_ids))

    print('* Test')

    hparams = {"fit": "SP.BNDS", "init": "circle", "resolution": 100}
    # hparams = {"fit": "SP", "init": "circle", "resolution": 100}
    # hparams = {"fit": "SP.Y0", "init": "circle", "resolution": 100}

    # hparams = {"fit": "SP.BNDS", "init": "manual", 
    #            "man_params": [1,2,0], "resolution": 100}

    # hparams = {"fit": "SP", "init": "manual", 
    #            "man_params": [10,20,0], "resolution": 100}

    ell, fb = approx_shape(faces, kpoints, ridge_ids, hparams)

    print('ell=', ell)
    print('fb=', fb)

    from matplotlib import pyplot as plt

    z = 0
    ts = np.linspace(0, 2*np.pi, 200)

    df_xs, df_ys = fb["default_shape_fn"].gen_shape(ts)
    xs, ys = ell.gen_shape(ts)

    plt.plot(faces[ridge_ids, 1], faces[ridge_ids, 2], 'y.')
    plt.plot(df_xs, df_ys, 'b--', label='circle')
    plt.plot(xs, ys, 'r:', label='ellipse')
    plt.axis('equal')
    plt.legend()
    plt.show()






