# iDNAM
iDNAM Project

## Goal

Options
* 1. Given ```stl``` file of a profile of patient's unilateral cleft lip and palate (UCLP, a cleft mouth), get the ```stl``` output for a correction NasoAlveolar molding (NAM, a cleft cast)
* 2. Blender plug-in automates (or semi-automates) generation of a cast profile for NAM.

See pages 45-46 of [iDNAME AI Project 031523](https://drive.google.com/file/d/10M-K6IoRaUhvc9x9v-bFmzyEW4NTkAKx/view?usp=share_link) 

## Evaluation
* Real evaluation needs clinical trials.
* Guideline metrics: gap width, curve matching

## Workflow and Approaches
* 1. Segmentation: greater palate and lesser palate
* 2. Detect ridges (peaks)
  * Options
    * User selected landmarks
    * Auto-detection
* 3. Produce cast profile.
  * Approach 1: Surface interpolation: closing cleft gap by tunnel
    * Conventional interpolation ([colab](https://colab.research.google.com/drive/1W2Ji8KbJf5F-3c8ML_YMiUr130_L7nzw?usp=share_link))
      * cubic spline may not work directly, since it requires interpolation ordered by $x$. 
      * new cylindrical interpolation: spiral
    * curve fitting
      * [parabola](https://colab.research.google.com/drive/1osVF3ibuDZ3rS6RisX4XpqwxKdHy31zq#scrollTo=ebFEQH7LBq3T)
        * It does not seem to work! (Apr 11th)
      * 3D ellipse
  * Approach 2: Optimization: minimize rotation and translation s.t. gap distance, smooth connection, and center reference moved to mid location
    * E.g., $\min_{p, R, T} \lambda R^2 + T^2$ s.t. $d \leq 5mm$, curve matching, tolerance of a reference point to the mid location
    * See page 62 of [iDNAME AI Project 031523](https://drive.google.com/file/d/10M-K6IoRaUhvc9x9v-bFmzyEW4NTkAKx/view?usp=share_link)
      * $p$ is location of a pivot point, $R$ is rotation, $T$ is translation.
      * $d$ is a gap between 2 separated palates.
      * $\lambda$ is a balancing factor.
  * Apporach 3: Mirror image, i.e., mirror the large palate on the small side.
  * Approach 4: Model with parameters tuned with previous data
  * Approach 5: CNN to predict a cast profile directly
    * Pro: challenge on how to meaningfully represent 3D surface data
    * Con: require massive training data and computing power to match.

## Concerns
* 1. Computation cost from operations on massive data of mesh triangles.
* 2. Vagueness of evaluation process.

## Challenges
* 1. Working on 3D surface with massive data of mesh triangles.
  * Check out how Blender handles it.
* 2. Locating dental landmarks
  * User provides landmarks
  * Once reference level plane is defined, peaks can be identified through  z values.
    * Reference level plane can be provided by a user
    * Or, it can be automatically identified using average normal vector: $\bar{n} = \sum_i \vec{n}_i$.
* 3. Modeling 3D surface of cleft mouth and simulating manipulation effects: how profile will be changed due to manipulation, e.g., rotation and translation.
* 4. Alignment issue
  * This may be more related to comparison between intial and final states, rather than the main goal of the project.
    * Challenge: level reference plane is difficult to defined and effect of growth makes it more difficult to compare initial and final states
  * Caveat: X, Y, Z coordinates extracted from software may be arbitrary!
    * Dataset 1: X: left-right, Z: back-front
    * Dataset 2: X: front-back, Z: right-left

---
## Python - Blender

* [API](https://wiki.blender.org/wiki/Reference/Release_Notes/3.4/Python_API)
* Objects ```objs = bpy.data.collections['Collection'].objects```
  * E.g., ```o = bpy.data.collections['Collection'].objects['Nasolabial_scan']``` and ```m = o.to_mesh()```
  * [Mesh](https://docs.blender.org/api/current/bpy.types.Mesh.html)
    * [```vertices```]
      * E.g., ```m.vertices[84451].co``` 
    * [```edges```]
    * [```loops```]
    * [```polygons```]
---
## Logs

* Next
  * Mirror approach
    * python + blender to mirror
    * Have python mirror stl mesh triangles.
    * Put 3D points onto mesh surface.
  * Affine transformation approach 
  * alignment w/ account for growth
    * effective growth centriod? 
  * Spiral interpolation
  * Divided interpolation: left (x=back-front); right (x=back-front); front (connection points on the front, x=left-right)

* May 12
  * [Compute](https://colab.research.google.com/drive/1NMjkwJhOX0p9Xu_oBTSK8bTI_NLSLvLL#scrollTo=dXitJ_slk4Dk)
  * Learn Blender


* May 1
  * Python Blender API: https://docs.blender.org/api/blender_python_api_master/

* Apr 28
  * Add 'constraint' > 'shrinkwrap' on surface > target = 'nasolabial_scan'
  * See python console result, e.g., ```print``` by ```Window``` > ```Toggle System Console```
  * See https://docs.blender.org/api/current/info_quickstart.html to learn about how Blender works.

* Apr 27
  * [Global vs Local](https://blenderartists.org/t/global-vs-local-coordinate/354788)
  * Watch Blender Fundamentals 2.8
    * Next: (4th) Select & Transform 
  * Make Blender as a python module: https://wiki.blender.org/wiki/Building_Blender/Other/BlenderAsPyModule
  * Run script outside Blender UI: https://docs.blender.org/api/current/info_tips_and_tricks.html#use-an-external-editor

* Apr 26
  * Learn Blender
    * Reduce mesh resolution
      * ```edit mode```
	     * > ```select``` > ```all```
	     * > ```mesh``` > ```clean up``` > ```decimate geometry```
	     * > On pop-up panel: set ```ratio```, e.g., 0.1
    * Separate objects
      * [Seperate](https://docs.blender.org/manual/en/latest/modeling/meshes/editing/mesh/separate.html): 'P'


* Apr 11
  * Discuss with Aj Nawapak and Aj Wasu
    * Idea!
      * Mirror: mirror plane with minimization of difference in normal vectors around mirror boundary: 
      
      $$\min_{\hat{m}} \sum_{i \in boundary} (\hat{n}_i - \hat{n}'_i)^2$$ 
      
      where $\hat{m}$ is a normal vector of a mirror plane.
      * This $\hat{m}$ can be initialized with $\vec{m}_0 = \vec{t'} - \vec{t}$ at its midpoint: $\vec{t'} + \vec{m}_0/2$.
        * The discrepancy between $\vec{t'}$ and $\vec{t}$ can be corrected through optimization.
      * This idea can be extended to find a level XY plane: XY plane the can mirror such that the reflection normal vectors are most complement to the original normal vectors.
        * $\hat{n} - \hat{n'} \approx 0$, is it?
  * Next
    * Mirror approach
    * Affine transformation approach

  
* Mar 30, 2023.
> "Can Blender be used as AutoCAD?
No, Blender is not a CAD software. CAD software relies primarily on curve modeling while Blender primarily relies on polygon modeling. CAD Models are a collection of shapes defined with math while models made in Blender are collections of points connected by edges and face."
* Working code
  * [read and write stl file](https://colab.research.google.com/drive/1ecNpa9p7aKYWElI07wIYfy31l1-uW_39?usp=share_link)
  * [pilot keypoints](https://colab.research.google.com/drive/1W2Ji8KbJf5F-3c8ML_YMiUr130_L7nzw?usp=share_link)
    * Try simple interpolation
      * Naive version does not work. The order issue.
    * [Try simple curve fitting](https://colab.research.google.com/drive/1osVF3ibuDZ3rS6RisX4XpqwxKdHy31zq#scrollTo=ebFEQH7LBq3T)
      * Naive version does not seem to be what we want.
    * [Try pca for auto-correct level plane.](https://colab.research.google.com/drive/1osVF3ibuDZ3rS6RisX4XpqwxKdHy31zq#scrollTo=ebFEQH7LBq3T)
      * Naive application of PCA does not seem to be beneficial!


* To do:
    * 1. Keypoints: [Quadratic curve fitting](https://colab.research.google.com/drive/1osVF3ibuDZ3rS6RisX4XpqwxKdHy31zq#scrollTo=ebFEQH7LBq3T) Done! Apr 11. Not quite what we want.
    * 2. STL: Auto-reference plane, e.g., try pca vs average normal vector
      * 2.1. Get reference plane
      * 2.2. Auto-identify keypoints and Alveolar ridge (Talk to Aj Nawapak)
      
  * To learn:
    * 1. Efficient manipulation of triangluar mesh
    * 2. Blender and Blender coding
    
 
* Mar 28, 2023. Meeting.
  * realize coordinate issue
  * aware of alignment issue
    * This matters when we want to compare before and after the NAM treatment.
  * realize cons of interpolation approach
    * oscillation
    * order of points
      * spiral interpolation

* Mar 27, 2023. Solo.
  * [Cubic spline](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html)
  * [Bezier spline](https://en.wikipedia.org/wiki/B%C3%A9zier_curve)
  * [3D interpolation](https://pangeo-pyinterp.readthedocs.io/en/latest/auto_examples/ex_3d.html)

* Mar 23, 2023. Meeting.

  * 1. Surface interpolation may not work, since there might be situation where surface gradient may not be properly matched.
  * 2. Peak finding through large change in directions of adjacent normal vectors may not work, since ridge shape may appear like tepui (flat top).
    * It may be able to find ledge along the ridge though.
  * Next move:
    * Master python/blender
    * [Hands-on python stl](https://github.com/tatpongkatanyukul/iDNAM/blob/main/HandsOn/readme.md) [(Equivalence on colab)](https://colab.research.google.com/drive/1Zv78AlXZGzV7_9aVnF3CCSOHrSZ4tOia)
  * [presentation](https://drive.google.com/file/d/10M-K6IoRaUhvc9x9v-bFmzyEW4NTkAKx/view?usp=share_link)

* Mar 16, 2023.

> the facet normal should be a unit vector pointing outwards from the solid object.[13] In most software this may be set to (0,0,0), and the software will automatically calculate a normal based on the order of the triangle vertices using the "right-hand rule", i.e. the vertices are listed in counter-clock-wise order from outside. Some STL loaders (e.g. the STL plugin for Art of Illusion) check that the normal in the file agrees with the normal they calculate using the right-hand rule and warn the user when it does not. Other software may ignore the facet normal entirely and use only the right-hand rule.
> ... Each triangle is described by twelve 32-bit floating-point numbers: three for the normal and then three for the X/Y/Z coordinate of each vertex – just as with the ASCII version of STL. After these follows a 2-byte ("short") unsigned integer that is the "attribute byte count" – in the standard format, this should be zero because most software does not understand anything else.
> ...
```
UINT8[80]    – Header                 -     80 bytes
UINT32       – Number of triangles    -      4 bytes

foreach triangle                      - 50 bytes:
    REAL32[3] – Normal vector             - 12 bytes
    REAL32[3] – Vertex 1                  - 12 bytes
    REAL32[3] – Vertex 2                  - 12 bytes
    REAL32[3] – Vertex 3                  - 12 bytes
    UINT16    – Attribute byte count      -  2 bytes
end
```
src https://en.wikipedia.org/wiki/STL_(file_format)

* https://python-stl.readthedocs.io/en/latest/index.html
* https://pypi.org/project/numpy-stl/

---

* Try [Colab: stl](https://colab.research.google.com/drive/1Zv78AlXZGzV7_9aVnF3CCSOHrSZ4tOia)

* Check out [Tutorial on how to write a python script to control blender](https://www.youtube.com/watch?v=rHzf3Dku_cE)
