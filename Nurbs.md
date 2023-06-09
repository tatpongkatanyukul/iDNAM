# NURBS

Non-Uniform Rational B-Splines


---

Les Piegl, On NURBS: A Survey

> A NURBS curve is a vector-valued piecewise rational polynomial function of the form

$C(u) = \frac{\sum_i w_i P_i N_{i,p}(u)}{\sum_i w_i N_{i,p}(u)}$

where 
* $w_i$ are the weights,
* $P_i$ are the control points,
* $N_{i,p}(u)$ are the normalized B-spline basis functions of degree $p$ defined as

$$N_{i,0}(u) = \begin{cases}
    1, & \text{if } u_i \leq u < u_{i+1} \\
    0, & \text{otherwise}
\end{cases}$$

$$N_{i,p}(u) = \frac{u-u_i}{u_{i+p} - u_i} N_{i,p-1}(u) + \frac{u_{i+p+1}-u}{u_{i+p+1} - u_{i+1}} N_{i+1,p-1}(u)$$

where $u_i$ are the knots, forming a knot vector $U = [ u_0, u_1, \ldots, u_m ]^T$

The degree $p$, number of knots $m$, and number of control points $n$ are related by the formula $m = n + p + 1$ .

---
