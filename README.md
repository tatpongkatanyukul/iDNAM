# iDNAM

* [OLD Log 2023](https://github.com/tatpongkatanyukul/iDNAM/blob/main/OLDLog2023.md)

# Papers

* 2024: ITTA, Baku Azerbaijan

---
# My strategy
* Since Aj Wasu covers the main and essential part, I am quite free to explore anything I wish.
* The hard part of this project is that I have to write python code in Blender editor, which is not quite friendly. The import file is too much of a trouble.
  * It may be more productive to exprot the essential data and work in my comfortable environment like Colab.

---
# Plan
Two main tasks
* 1. Finding edges
  * Option 1.1. **Self-organizing map**
  * Option 1.2. Features ($z$, $\vec{n}$, $\Delta \vec{n}$) and ANN
  * Option 1.3. Surface CNN

* 2. Bridging gap
  * Option 2.1. **NURBS: maximization of ridge continuity: grad and momentum (or Jacobian)**
  * Option 2.2. Patient's palates: minimization of rotation and translation   
 
* 3. Assessing results
  * I am thinking out having results from multiple approaches and have experts (K. June, Aj Cartoon) blindly grade the results.
  * Check out Bleu score for reference
 
---
# On hold

* [Morphogen 2D](https://colab.research.google.com/drive/1mT8QNi-vt6rmBi1QrWxQwdN2B582q4tZ#scrollTo=C0mdgvfGO0cL) (On hold 2023 Oct 24)
  * It (```polymorph``` and ```polymorph_coeff```) is not right!
    * reflective criterion is not met.
    * continuous secretion criterion is not met either.

* [Shape regression](https://colab.research.google.com/drive/1shFRNxwB2SVL8DPYXnpWWhgsHPg0WOnZ#scrollTo=yhaNKMWV8lrd)

---
# To write

* Moving ellipse: shape model
* Fixing the double peak: cross-section model

---
# To do

* Auto-alignment
  * PCA 

* Shape
  * Fourier-approx shape
  * Cross-section area as indicator of fitness vs parabola
  * Morphogen: use other method than separation of variable to solve pde w/ B.C. = ellipse

* Thicken the bridge
* Fill the floor
* dent it for fenum

---
# Log

* 2024 July 6
  * June left the project! 

* 2024 July 9
  * Talk to Aj Anuparb
  * [STL files](https://drive.google.com/drive/u/0/folders/1RGY4oe1fq1-ljXw90aQ52reQOMHk6Bwv)

* 2024 Feb 22
  * Finish [Phase 1](https://github.com/tatpongkatanyukul/iDNAM/tree/main/Phase1)

* 2024 Feb 21
  * [PCA to pre-orient axis](https://colab.research.google.com/drive/10eDKV-de9gIJF0asBL6s9_T-2AJ6aq-n)
  * [Investigate a ridge-over-bridge case](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Log/readme.md)
  * Idea to fix multiple-peak case: instead of $\max \{ bin(i) \}$, if we do $\max \{ bin{i-1}, bin(i) \}$ then we don't have to worry about trailing edge or correcting heights after peak anymore. The lead edge will be the same.

* 2024 Feb 20
  * Refine [Phase 1](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/readme.md)
  * Work on the [set up script](https://github.com/tatpongkatanyukul/iDNAM/blob/main/Phase1/AutoSetupV1.py)
  * Issues left
    * A little nuisance on moving reference points
      * Cause: data axis is off
      * Chicken-and-egg problem: once T, T', and C are located, Aj Wasu has coded the "Move to World Location".
      * But moving the objects in a disoriented axes is like a drunkard trying to walk on a straight line.
      * [PCA](https://stackoverflow.com/questions/32569188/scipy-svd-vs-numpy-svd) can come to rescue.

* 2024 Feb 10
  * [Phase 1](https://drive.google.com/drive/folders/13EcyENB7C4cwWotuD_PyRjYlV1-YZG6h?usp=drive_link) 

* Oct 24
  * [Elliptic curve](https://colab.research.google.com/drive/1aP1Wb8wCztPs2EYsz0TKfGTFdNxUhtvR#scrollTo=uzLR4OOt1jFU)
    Next:
    * Add it to Blender
    * Find the ridge
    * Fit ellipse to the ridge
    * Make NAM surface using Gaussian mixture model 


* Oct 20
  * [Evaluation](https://github.com/tatpongkatanyukul/iDNAM/blob/main/evaluation/readme.md)

* Oct 13

I am able to import module in python/blender

```
import sys
sys.path.append("E:\\2023\\Research\\iDNAM\\230706")

from myutils import test
print('test=', test(5))
```

* Sep 20
  * ?read NURBS 
