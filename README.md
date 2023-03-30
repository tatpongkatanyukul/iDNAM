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
      * parabola
      * 3D ellipse
  * Approach 2: Optimization: minimize rotation and translation s.t. gap distance, smooth connection, and center reference moved to mid location
    * E.g., $\min_{p, R, T} \lambda R^2 + T^2$ s.t. $d \leq 5mm$, curve matching, tolerance of a reference point to the mid location
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

## Logs

* Next
  * Try pca for auto-correct level plane.
  * alignment w/ account for growth
    * effective growth centriod? 
  * Spiral interpolation
  * Divided interpolation: left (x=back-front); right (x=back-front); front (connection points on the front, x=left-right)

* Mar 30, 2023.
> "Can Blender be used as AutoCAD?
No, Blender is not a CAD software. CAD software relies primarily on curve modeling while Blender primarily relies on polygon modeling. CAD Models are a collection of shapes defined with math while models made in Blender are collections of points connected by edges and face."
 
 
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
