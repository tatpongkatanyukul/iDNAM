# Features
* 1. From IOS to a bridge model, it requires only key-point identification.
* 2. Allow on-the-fly adjustment of marked ridge area.
* 3. Allow on-the-fly adjustment of cross-section outline.
* Although it is possible to adjust a shape model, I am not feeling comfortable recommending it.
* 4. All setting parameters are accessed through json: ```conf.json```.

# To do
* 1. Snap keypoints, e.g., C, T, T' to the surface for ease of handling.
* 2. Auto smoothening the cross-section.
* 3. Auto de-corner the section corners.
* 4. Easy set-up facility for setting up scipy to Blender-Python.

# Usage
* Requirement
  * Have ```scipy``` installed for Blender-Python
  * Have scipy installed path configured in ```AutoBridgeV2.py```
    ```
    # Path for scipy
    packages_path = r"C:\Users\ASUS\AppData\Roaming\Python\Python310\site-packages"
    ```
  
* 1. In Blender, under ```scripting``` > ```Text``` > ```Open```, choose ```AutoBridgeV2.py```
* 2. Click ```Run script``` (Alt P, in windows)
* 3. 3. In ```3D Viewport```, there will be side tab ```Dental Workflow```.
* 4. Follow steps in the workflow. 
 
# Next
* Evaluation.
* Phase 2: make it a print-ready plate.
