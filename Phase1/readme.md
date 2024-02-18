# Features
1. From IOS to a bridge model, it requires only key-point identification.
2. It allows on-the-fly adjustment of marked ridge area.
   It can be done through material index. Though it may not be easy.
3. It allows on-the-fly adjustment of cross-section outline.
   It can be done in ```Edit``` mode. This is not so difficult.
* Although it is possible to adjust a shape model, I am not feeling comfortable recommending it.
* Of course, the final bridge model can also be modified.
4. All setting parameters are accessible through json: ```conf.json```.

# To do
1. Snap keypoints, e.g., C, T, T' to the surface for ease of handling.
2. Auto smoothening the cross-section.
3. Auto de-corner the section corners.
4. Easy set-up facility for setting up scipy to Blender-Python.

---

# Usage
* Requirement
  * Have ```scipy``` installed for Blender-Python
  * Have scipy installed path configured in ```AutoBridgeV2.py```
    ```
    # Path for scipy
    packages_path = r"C:\Users\ASUS\AppData\Roaming\Python\Python310\site-packages"
    ```
  
1. In Blender, under ```scripting``` > ```Text``` > ```Open```, choose ```AutoBridgeV2.py```
2. Click ```Run script``` (Alt P, in windows)
3. In ```3D Viewport```, there will be side tab ```Dental Workflow```.
4. Follow steps in the workflow. 

# Configuration

The configuration file ```conf.json```, specified in ```AutoBridgeV2.py``` (i.e., ```cfg='conf.json'```)

Fields:
* ```"log"```: ```"log.txt"```. A log filename, without path. The path is automatically set to the working path, where the ```AutoBridgeV2.py``` is.
* ```"save_context"```: ```true```. Whether to save the context, e.g., faces and keypoints, for further investigation.
* ```"faces_file"```: ```"faces.npy"```. Filename of the saved faces (IOS polygons).
* ```"kp_file"```: ```"kp.pkl"```. Filename of the saved keypoints: user-specified keypoints.
* ```"ridge"```: ```{"criteria": "zmax", "tau": 0.0, "show": true, "materials": {"ridge": [1,0,0,1], "non-ridge": [0.5,0.5,0.5,1]}}```. Ridge identification hyperparameters.
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
    * ```"R"```: Approximate a cross-section of IOS whose face center $r_1 \leq r \leq r_2$,
      where $r_1$ and $r_2$ are radials of keypoints.
    * ```"Z"```: Approximate a cross-section of IOS whose face center either having $z \geq z_1$ and $r < r_1$ or having $z \geq z_2$ and $r < r_2$.
  * ```"resolution"```: A number of discretizing bins.
      
* ```"cross_sect_collection"```: ```"Bridge"```
* ```"cross_sect_save"```: ```"xsect.pkl"```

---

## Starting
![Steps](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/Steps.png)




## Step 5
![Set keypoints](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/IOS.png)

## Step 6
![Ridge identification result](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/Ridge.png)

## Step 7
![Shape approximation](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/Shape.png)

## Step 8
![Cross-section](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/CrossSection.png)

## Step 9
![Bridge](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/Bridge.png)


---

# Next
* Evaluation.
* Phase 2: make it a print-ready plate.
