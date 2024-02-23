# Features
1. From IOS to a bridge model, it requires only key-point identification.
2. It allows on-the-fly adjustment of marked ridge area.
   It can be done through material index. Though it may not be easy.
3. It allows on-the-fly adjustment of cross-section outline.
   It can be done in ```Edit``` mode. This is not so difficult.
* Although it is possible to adjust a shape model, I am not feeling comfortable recommending it.
* Of course, the final bridge model can also be modified.
4. All setting parameters are accessible through json: ```conf.json```.
5. Names of all key points are adjustible in a single point, ```AutoBridgeV3.py```
6. It provides visualization for ridge identification, shape approximation, and cross-section approximation.

# To do
1. Snap keypoints, e.g., ```C```, ```T```, ```T'```, to the surface for ease of handling.
   This requires proper cooridnation. E.g., when z-axis is totally off, snap (projection along z) causes a weird behavior.
2. Auto smoothening the cross-section.
3. Auto de-corner the section corners.
4. ~~Easy set-up facility for setting up scipy to Blender-Python.~~ Done! See ```AutoSetupV2.py``` along with ```setup.json```.

# Technical values beyond ITTA2024 paper

1. Shape approximation allows an off-center ($y_c \neq 0$) ellipse
2. Cross-section approximation has better handling on trailing edges in multiple-peak cases.

# Opportunities

1. Auto-orientation: PCA 
2. More flexible shape: Fourier approximation

---

# Usage
* Requirement
  * Have ```scipy``` installed for Blender-Python (manually or automatically if run ```AutoSetupV2.py```)
  * Have scipy installed path configured in ```setup.json``` (manually or automatically if run ```AutoSetupV2.py```)
  
1. In Blender, under ```scripting``` > ```Text``` > ```Open```, choose ```AutoBridgeV2.py```
2. Click ```Run script``` (Alt P, in windows)
3. In ```3D Viewport```, there will be side tab ```Dental Workflow```.
4. Follow steps in the workflow. 

# Configuration

The configuration file ```conf.json```, specified in ```AutoBridgeV3.py``` (i.e., ```cfg='conf.json'```)

Fields:
* ```"log"```: ```"log.txt"```. A log filename, without path. The path is automatically set to the working path, where the ```AutoBridgeV3.py``` is.
* ```"save_context"```: ```true```. Whether to save the context, e.g., faces and keypoints, for further investigation.
* ```"faces_file"```: ```"faces.npy"```. Filename of the saved faces (IOS polygons).
* ```"kp_file"```: ```"kp.pkl"```. Filename of the saved keypoints: user-specified keypoints.
* ```"reference"```: ```{"autoaxis": false, "mode": "no constraint"}```
  * ```autoaxis``` NOT YET IMPLEMENTED! Automatic orientation: x-,y-,z-axes.
  * ```"mode"```
    * ```"constraint"``` NOT YET COMPLETED! snap to the target surface. Unless axes are well set, this does not help. Also, it requires setting of z values, otherwise it will only cause confusion.
    * ```"no constraint"``` (or anything, but ```"constraint"```) No snapping to the target surface.
* ```"ridge"```: ```{"criteria": "zmax", "tau": 0.0, "show": true}```. Ridge identification hyperparameters.
  * ```criteria``` options
    * ```"zmax"```: ridge is any face whose center $z \geq \tau z_\max$,
      where $z_\max$ is the maximal $z$ and $\tau$ is specified by ```"tau"```.
    * ```"z >= 0"``` (or anything, but ```"zmax"```): ridge is any face whose center $z \geq 0$. This is equiv. to ```zmax``` with ```tau``` 0.
  * ```"show"``` whether to switch 3D viewport to ```material preview mode``` the ridge and non-ridge areas are marked by colors specified in ```"materials"```.
* ```"shape"```: ```{"fit": "SP", "init": "circle", "resolution": 100, "angles": ["T1'", "C1"]}```. Shape approximation hyperparameters.
  * ```"fit"``` Method to fit the shape, i.e., ellipse to the ridge data.
    * ```SP``` employs ```curve_fit``` ellipse $\frac{x^2}{\alpha^2} + \frac{(y - y_c)^2}{\beta^2} = 1$.
    * ```SP.Y0``` employs ```curve_fit``` ellipse $\frac{x^2}{\alpha^2} + \frac{y^2}{\beta^2} = 1$.
    * ```SP.BNDS``` employs ```curve_fit``` ellipse with all $\alpha$, $\beta$, and $y_c$ are bounded to $-2 \bar{r}, 2 \bar{r}$.
    * ```GD``` NOT YET IMPLEMENTED! Gradient descend. This does not require ```scipy```, but is slow and requires all GD practices. Not recommended if ```scipy``` is available.
  * ```"init"``` Method to initialize the model parameters.
    * ```"circle"``` uses circle parameters to initialize, i.e., $\alpha = \bar{r}$, $\beta = \bar{r}$, and $y_c = 0$.
    * ```"manual"``` set parameters directly, requires ```man_params```, e.g., ```"man_params": (20, 20, 0)```.
  * ```"resolution"``` Resolution of the shape geometry generated.
  * ```"angles"``` Keypoints to specify the segment of the shape model to approximte "ridge" shape.
* ```"shape_collection"```: ```"Bridge"```. Name of the shape collection, created if not exists.
* ```"shape_save"```: ```"shape.pkl"```. Filename of the saved shape results.
* ```"cross_sect"```: ```{"angle_keys": ["T1'", "C1"], "radial_bounds": ["RI", "RO"], "radial_mode": "Z", "resolution": 40}```. Cross-section approximation hyperparameters.
  * ```angle_keys```: key points specifying segment. These are independent from shape angles to give freedom to the cross-section approximation, e.g., it can be chosen to fit to a larger segment than what shape is prepared, to account for possible plate movement.
  * ```"radial_bounds"```:  key points specifying radial bounds, or how wide the cross-section is accounting for.
  * ```"radial_mode"```: Method to take radial bounds into selection.
    * ```"R"```: Approximate a cross-section of IOS whose face center $r_c + \Delta r_1 \leq r \leq r_c + \Delta r_2$,
      where $\Delta r_1 = r_1 - r_c$, $\Delta r_2 = r_2 - r_c$, $r_1$ and $r_2$ are radials of keypoints; and $r_c$ is the radial of the center of the ellipse at the corresponding angle.
      E.g., the final bridge will have a constant width controlled by 2 keypoints, in this example, ```RI``` and ```RO```.
    * ```"Z"```: Approximate a cross-section of IOS whose face center either having $z \geq z_1$ and $r < r_1$ or having $z \geq z_2$ and $r < r_2$.
      E.g., in this example, the final bridge will have inner depth as deep as ```RI``` and outer depth as deep as ```RO```.
  * ```"resolution"```: A number of discretizing bins.
      
* ```"cross_sect_collection"```: ```"Bridge"```
* ```"cross_sect_save"```: ```"xsect.pkl"```

---

## Starting
![Steps](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/Steps.png)

## Step 5
![Set keypoints](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/IOS.png)

## Step 6: Ridge identification

After ridge identification, all faces identified to be ridge are assigned "ridge" material (color as specified in ```conf.json```, here shown in blue)

![Ridge identification result](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/IdenRidge.png)

## Step 7: Shape approximation

Shape is approximated based on ridge data (from step 6) and shape prior, e.g., ellipse and perhaps having center on (0,0,0) using ```shape``` ```fit``` = ```SP``` or (0,y,0) using ```SP.Y0``` in ```conf.json```. The final shape and approximate bridge are created as Blender geometries. The generated shape is highlighted in orange in this example.

![Shape approximation](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/ApproxShape.png)

## Step 8: Cross-section approximation

Cross-section is approximated based on ridge data (from step 6), shape approximation (from step 7), and cross-section mode and bounds, specified in ```conf.json``` (under ```cross_sect```). After the approximation, the cross-section geometry is created and the faces involved in the process are assigned "effective" (used for approximation) or "non-effective" (discarded based on outlier criteria). Here the ```effective``` are shown in red.

![Cross-section](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/ApproxCrossSection.png)

## Step 9

The bridge geometry is created based on shape (from step 7) and cross-section (from step 8).

![Make Bridge](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/MakeBridge.png)

![Bridge](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/Bridge.png)


---

# Next
* Evaluation.
* Auto-orientation.
* Fourier shape.
* Phase 2: make it a print-ready plate.
