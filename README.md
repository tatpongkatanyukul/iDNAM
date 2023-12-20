# iDNAM

* [OLD Log 2023](https://github.com/tatpongkatanyukul/iDNAM/blob/main/OLDLog2023.md)

# Papers

* 2023: ITTA, Baku Azerbaijan
* 2024: Uzbekistan? https://icisca.newuu.uz/ or computational science?

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
# Log

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
