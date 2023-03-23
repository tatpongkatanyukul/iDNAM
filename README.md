# iDNAM
iDNAM Project

## Goal

Options
* 1. Given stl file of a cleft month profile, get the stl output for a correction cleft cast
* 2. Blender plug-in automates (or semi-automates) generation of a cast profile.

## Evaluation
* Real evaluation needs clinical trials.
* Guideline metrics: gap width, curve matching

## Workflow and Approaches
* 1. Segmentation
* 2. Detect ridges (peaks)
  * Options
    * User selected landmarks
    * Auto-detection
* 3. Produce cast profile.
  * Approach 1: Surface interpolation: closing cleft gap by tunnel
  * Approach 2: Optimization: minimize rotation and translation s.t. gap distance, smooth connection, and center reference moved to mid location
    * E.g., $\min_{p, R, T} \lambda R^2 + T^2$ s.t. $d \leq 5mm$, curve matching, tolerance of a reference point to the mid location
      * $p$ is location of a pivot point, $R$ is rotation, $T$ is translation.
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

* Mar 23, 2023.

* 1. Surface interpolation may not work, since there might be situation where surface gradient may not be properly matched.
* 2. Peak finding through large change in directions of adjacent normal vectors may not work, since ridge shape may appear like tepui (flat top).
  * It may be able to find ledge along the ridge though.
* Next move:
  * Master python/blender
  * [Hands-on python stl](https://github.com/tatpongkatanyukul/iDNAM/blob/main/HandsOn/readme.md) [Equivalence on colab](https://colab.research.google.com/drive/1Zv78AlXZGzV7_9aVnF3CCSOHrSZ4tOia)

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
