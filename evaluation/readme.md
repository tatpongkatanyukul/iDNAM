# Evaluation

* Evaluation of digital 3D model
* Evaluation of physical NAM
* Evaluation of the treatment

---

## Evaluation of digital 3D model

We may need to separate the evaluation of different types of NAMs

  * Multi-stage NAM
  * Single-stage NAM
    * Single-stage NAM has to fit a patient's mouth from an initial state to a final state.
    * Fitness score
      * $s = \frac{1}{2} (f_0 + f_1)$ where $f_0$ : fitness at the initial state and $f_1$ : fitness at the final state
      * $f_0$ and $f_1$ represent how well the NAM fits to the patient's ridge over **the designated area**.
      * Since $f_1$ measures NAM against a final state of the patient's ridge, it can be computed after the treatment is concluded. 
      * Speculated fitness $\hat{s} = \frac{1}{2} (f_0 + \hat{f}_1)$
        * where speculated final fitness $\hat{f}_1$ is computed with the speculated final state of the patient's ridge.
      * Speculated final state: criteria
        * Gap $D$ between 2 reference points: $A_g$ and $A_l$.
          * $|A_g - A_l| leq D$
        * Projected ridge curves are well matched.
          * curve eq. of greater segment $f_g'(A_g) = b'(A_g)$ and $f_l'(A_l) = b'(A_l)$                  
          * $b$ is a bridge eq.: $b''(a \in [A_g, A_l]) =$ constant.
          * Ridge curve can be fitted from ridge faces.
            * Ridge faces can be identified by $\vec{n}_i \cdot \hat{z} > \tau$ where $\vec{n}_i$ is a normal vector of the face and $\hat{z}$ is a unit vector of z direction.
      * The designated area has to be specified for what conditions, e.g., clearance about 0.15 mm over some area or may be over 5mm-10mm over another area.
     
      The fitness score $f$ depends on the clearance (between NAM surface and the patient ridge, corresponding z-location) $c = Z_N - Z_P$

      * Over some area, this $c$ is expected to be around $0.15$.
      * Over some other area, the criteria may be different, e.g., more flexibility (larger clearance).
      * Example of $f$ formulation
     
        $f = e^{-\sum( (Z_N - Z_P - 0.15)^2 )}$

Note: some other utility tasks
* Automatically find axes.
* Automatically align NAM to patient's ridge
    
---

## Evaluation of the treatment

  * Aveleolar-Ridge Score (ARS)
    * joint meet projection / joint sharpness (matching curve)
    * gap size
  * initial ARS: score of the initial aveleolar ridge of a patient: how good/bad the patient's ridge is.
  * final ARS: score of the final ridge: how good the ridge is after the treatment.

  * Subject of evaluation is the patient's aveleolar ridge
    * near an oral 3D scan  
 
 
