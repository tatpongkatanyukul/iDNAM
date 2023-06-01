# Learn Blender Python

* Accessing object
  * ```bpy.data.objects["<obj name>"]``` 

* Create a new mesh (mesh is the underlying data of the object, but object has other attributes, e.g., constraint)
  * ```bpy.ops.mesh. ...```

* UI / Panel
  * ```invoke``` > ```execute```
  * ```poll``` is "always" running

---
# Tricks

* Coordinate values
  * "apply transform" before reading data, otherwise it may not be updated.

* ```bmesh``` is a very handy tool to work with mesh info

---

# Interesting code

Code examples
* [Aj Wasu's dp2.py with my addition](https://github.com/tatpongkatanyukul/iDNAM/blob/main/dp2_wasu230531_PlusTKv1.py)\
* [Aj Wasu's color.py for visualizing ridge finding](https://github.com/tatpongkatanyukul/iDNAM/blob/main/color.py)
