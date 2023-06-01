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
