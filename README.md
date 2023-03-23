# iDNAM
iDNAM Project

## Goal

Options
* 1. จาก stl file ของ cleft month profile ทำ stl output สำหรับ cleft cast
* 2. Blender plug-in automates (or semi-automates) cast profile.

## Evaluation
* Real evaluation needs clinical trials.
* Guideline metrics: gap width, curve matching

## Workflow and Approaches
* 1. Segmentation
* 2. Detect ridges (peaks)
* 3. Produce cast profile.




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

* Try [Colab: stl](https://colab.research.google.com/drive/#create=1&folderId=1IINhV8ZIgnSsc8iKzD9FN_38psgIQj_Z)
