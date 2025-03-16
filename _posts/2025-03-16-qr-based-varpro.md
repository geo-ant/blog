---
layout: post
tags: least-squares algorithm varpro
#categories: []
date: 2025-03-16
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Solving Variable Projection with QR Decomposition'
#
#
# Make sure this image is correct !!!
og_image: vapro-with-qr.png
#
#
# make sure comments are enabled
comments_id: 82
math: true
---

This article continues the series on Variable Projection and
explains how rewrite the problem using QR decomposition, rather than the more
computationally expensive singular value decomposition (SVD).

# Context

VarPro is an algorithm to perform nonlinear least squares fitting for a
certain class of model functions to observations[^fitting]. I've
written about the [fundamentals of varpro](/blog/2020/variable-projection-part-1-fundamentals/)
and its [extension to global fitting](/blog/2024/variable-projection-part-2-multiple-right-hand-sides/)
--as well as [related topics](/blog/tags/#varpro)-- on this blog. I also maintain
the free and open-source [`varpro`](https://crates.io/crates/varpro) library in the Rust
language. This article is part of a long-running series on Variable Projection (VarPro)
on this blog, so I will rush through a lot of the fundamentals. I assume prior
knowledge of the first two linked articles, and I'll be using the same notation.

# Goal

The core computations in my library use the SVD matrix decomposition. While this makes
the algorithm very robust, it also comes with a speed penalty for problems that
don't actually require this degree of robustness. There is a well-known way to speed up
the calculations by using the QR decomposition and some mathematical sleights
of hand. In fact, that approach is used in many other implementations
and it's the original idea of Linda Kaufmann, published in (Kau75). This article explains
that approach. See also (Bae23) for a great recap as well as some cool extensions
to global fitting[^bae-qr].

# VarPro with QR

From the previous articles, we know that we can write a separable model function
$$\boldsymbol{f}$$, which depends on the parameters $$\boldsymbol{c}$$ linearly
and on the parameters $$\boldsymbol{\alpha}$$ nonlinearly, as

$$
\boldsymbol{f}(\boldsymbol{c},\boldsymbol{\alpha}) = \boldsymbol{\Phi}(\boldsymbol{\alpha})\boldsymbol{c}, \label{f} \tag{1}
$$

where we call $$\boldsymbol{\Phi}(\boldsymbol{\alpha}) \in \mathbb{R}^{m \times n}$$,
with $$m>n$$, the model function matrix. Typically, we are interested in some
form of *weighting* for the least squares problem, so that we end up with
the weighted function matrix $$\boldsymbol{\Phi}_w = \boldsymbol{W} \boldsymbol{\Phi} \in \mathbb{R}^{m \times n}$$
and the weighted matrix of observations $$\boldsymbol{Y}_w = \boldsymbol{W Y}$$.
After some neat math, which is described in detail in the previous articles, we arrive 
at this functional to minimize:

$$R_{WLS}(\boldsymbol{\alpha}) = \Vert \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \boldsymbol{Y}_w \Vert_F^2, \label{functional} \tag{2}$$

which only depends on $$\boldsymbol{\alpha}$$. $$R_{WLS}(\boldsymbol{\alpha})$$ is the sum of squared residuals we
want to minimize and $$\lVert . \rVert_F^2$$ is the
[Frobenius Norm](https://mathworld.wolfram.com/FrobeniusNorm.html).
$$R_{WLS}(\boldsymbol{\alpha})$$ is also called the *projection functional* and the matrix
$$\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \in \mathbb{R}^{m \times m}$$ is the
*projection onto the orthogonal complement of the range of* $$\boldsymbol{\Phi}_w(\boldsymbol{\alpha})$$.
For this article, I have used the formulation of VarPro that can account for
multiple [right hand sides](/blog/2024/variable-projection-part-2-multiple-right-hand-sides/),
but the whole article is also applicable to VarPro with a
[single right hand side](/blog/2024/variable-projection-part-2-multiple-right-hand-sides/).
In that case, the matrix $$Y_w$$ becomes the observation *vector* $$\boldsymbol{y}_w$$
and the matrix norm $$\lVert . \rVert_F^2$$ becomes the
[euclidean norm](https://en.wikipedia.org/wiki/Euclidean_space#Euclidean_norm)
$$\lVert . \rVert_2^2$$.

In the previous articles, we have used the singular value decomposition of
$$\boldsymbol{\Phi}_w(\boldsymbol{\alpha})$$ to rewrite the functional.
Now, we want to use the QR-decomposition with column-pivoting of the matrix $$\boldsymbol{\Phi}_w$$.
I'll leave out the dependency on $$\boldsymbol{\alpha}$$
for notational simplicity from now on, but all matrices in the following equation
have a dependency on the vector of nonlinear parameters $$\boldsymbol{\alpha}$$.
The column-pivoted QR decomposition of $$\boldsymbol{\Phi}_w$$ exists so that[^kaufmann-qr]:

$$
\boldsymbol{\Phi}_w\boldsymbol{\Pi} = \boldsymbol{Q} \boldsymbol{R} \label{qr} \tag{3},
$$

where $$\boldsymbol{\Pi}\in \mathbb{R}^{n\times n}$$ is a permutation matrix
that reorders the columns of $$\boldsymbol{\Phi_w}$$ for numerical stability,
$$\boldsymbol{Q} \in \mathbb{R}^{m \times m}$$ is an *orthogonal* matrix and
$$\boldsymbol{R}$$ is a matrix of this form:

$$
\boldsymbol{R} = \left[
\begin{array}{c|c}
\boldsymbol{R_1} & \boldsymbol{R_2} \\
\hline
\boldsymbol{0} & \boldsymbol{0} \\
\end{array}
\right] \in \mathbb{R}^{m \times n}, \label{r} \tag{4}
$$

where $$\boldsymbol{R_1} \in \mathbb{R}^{r \times r}$$ is a nonsingular upper triangular
matrix with $$r = \text{rank} \boldsymbol{\Phi}_w$$. The matrix $$\boldsymbol{R}_2 \in \mathbb{R}^{r \times (n-r)}$$
contains values that we won't need for the rest of this article[^r2-fullrank]. It is useful
to divide $$\boldsymbol{Q}$$ into two sub-matrices as well like so:

$$
\boldsymbol{Q} = 
\left[
\begin{array}{c|c}
\boldsymbol{Q}_1 & \boldsymbol{Q}_2
\end{array}
\right], \label{q} \tag {5}
$$

where $$\boldsymbol{Q}_1 \in \mathbb{R}^{m \times r}$$ is the submatrix of the
first $$r$$ columns, and $$\boldsymbol{Q}_2 \in \mathbb{R}^{m \times (m-r)}$$
contains the rest. Kaufmann gives expressions for the pseudoinverse
$$\boldsymbol{\Phi}_w^\dagger \in \mathbb{R}^{n \times m}$$ of the function
matrix, and for the projection matrix using the QR decomposition (Kau75):

$$
\begin{eqnarray}
  \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} &=& 
  \boldsymbol{Q}
  \underbrace{
  \left[
  \begin{array}{c|c}
  \boldsymbol{0} & \boldsymbol{0} \\
  \hline
  \boldsymbol{0} & \boldsymbol{I}_{(m-r)\times(m-r)} \\
  \end{array}
  \right]
  }_{m \times m}
  \boldsymbol{Q}^T
  =\boldsymbol{Q}
  \left[
  \begin{array}{c}
  \boldsymbol{0}_{r\times m} \\
  \hline
  \boldsymbol{Q}_2^T \\
  \end{array}
  \right]
  \label{p-qiq}
  \tag {6}\\[10pt]
  \boldsymbol{\Phi_w}^\dagger &=& 
  \boldsymbol{\Pi}
  \underbrace{
  \left[
  \begin{array}{c|c}
  \boldsymbol{R_1}^{-1} & \boldsymbol{0} \\
  \hline
  \boldsymbol{0} & \boldsymbol{0} \\
  \end{array}
  \right]
  }_{n \times m}
  \boldsymbol{Q}^T
  = \boldsymbol{\Pi}
  \left[\begin{array}{c}
  \boldsymbol{R_1}^{-1} \boldsymbol{Q_1}^T \\
  \hline
  \boldsymbol{0}_{(n-r)\times m} \\
  \end{array}
  \right]
  . \label{phi-dagger} \tag {7}
\end{eqnarray}
$$

Note, that if $$\boldsymbol{\Phi}_w$$ has full rank, i.e. $$r = n$$, then
the middle block matrix becomes $$\left[\boldsymbol{R}_1^{-1} \vert \boldsymbol{0}\right]$$
and thus $$\boldsymbol{\Phi}_w^\dagger = \boldsymbol{\Pi} \boldsymbol{R}_1^{-1}\boldsymbol{Q}_1^T$$.
Plugging $$\eqref{p-qiq}$$ into $$\eqref{functional}$$ lets us write


$$R_{WLS}(\boldsymbol{\alpha}) = \left\Vert \boldsymbol{Q}
  \left[
  \begin{array}{c}
  \boldsymbol{0} \\
  \hline
  \boldsymbol{Q}_2^T \\
  \end{array}
  \right]
  \boldsymbol{Y}_w \right\Vert_F^2=
  \left\Vert 
  \left[
  \begin{array}{c}
  \boldsymbol{0} \\
  \hline
  \boldsymbol{Q}_2^T \\
  \end{array}
  \right]
  \boldsymbol{Y}_w \right\Vert_F^2 
  =\left\Vert 
  \boldsymbol{Q}_2^T 
  \boldsymbol{Y}_w \right\Vert_F^2.
  \label{functional-q} \tag{8}
$$

For the first step, we have used the fact that we can just drop $$\boldsymbol{Q}$$
due to the invariance of the norm under orthogonal transformations[^norm-ortho].
The functional we want to minimize is thus

$$
R_{WLS}(\boldsymbol{\alpha}) =\left\Vert 
\boldsymbol{Q}_2^T(\boldsymbol{\alpha})
\boldsymbol{Y}_w \right\Vert_F^2.
\label{functional-q2} \tag{9}
$$

To use off-the-shelf minimization algorithms, like Levenverg-Marquardt, we
have to calculate the Jacobian matrix. I have given expressions for that
in the linked articles for single and multiple right hand sides. Instead of
the partial derivatives for $$\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}$$,
we now need an expression for the partial derivatives of $$\boldsymbol{Q}_2^T(\boldsymbol{\alpha})$$.
Luckily, Kaufmann gives an approximation for this expression:

$$
\frac{\partial \boldsymbol{Q}_2^T}{\alpha_k} \approx -\boldsymbol{Q}_2^T\frac{\partial \boldsymbol{\Phi_w}}{\alpha_k} \boldsymbol{\Phi_w}^\dagger, \tag{10}
$$

with $$\boldsymbol{\Phi}^\dagger$$ as in $$\eqref{phi-dagger}$$. There is a
typo in the Kaufmann paper for the final form of this equation, which
leaves out the preceding minus ($$-$$). The previous formulae in (Kau75), and the derivation
in (Bae23) show that this is an oversight.

# Conclusion

This is all we need to make VarPro work with the column-pivoted QR decomposition
instead of SVD. Using the QR decomposition with column-pivoting will work even
if the matrix $$\boldsymbol{\Phi}_w(\boldsymbol{\alpha})$$ becomes singular
or near-singular while iterating for a solution. If it's safe to assume that this
won't be the case _for all iterations_, then we can use the QR decomposition
without column pivoting. This should be even faster to compute, and it's 
what (Bae23) and (Mul08) do. This leads to virtually the same formulae as presented
above with the difference that there is no permutation matrix
($$\boldsymbol{\Pi}=\boldsymbol{I}$$) and $$r = \text{rank}(\boldsymbol{\Phi}_w) = n$$,
which implies $$\boldsymbol{Q}_2 \in \mathbb{R}^{m \times (m-n)}$$.

# References and Further Reading

**(Bae23)** Bärligea, A. *et al.* (2023) "A Generalized Variable Projection
Algorithm for Least Squares Problems in Atmospheric Remote Sensing,"
*Mathematics* **2023, 11, 2839** [DOI link](https://doi.org/10.3390/math11132839)

**(Mul08)** Mullen, K. M. (2008). "Separable nonlinear models: theory,
implementation and applications in physics and chemistry."
[PhD-Thesis - Research and graduation internal, Vrije Universiteit Amsterdam](https://research.vu.nl/ws/portalfiles/portal/75843866/complete%20dissertation.pdf).

**(Kau75)** Kaufman, L. A variable projection method for solving
separable nonlinear least squares problems.
BIT 15, 49–57 (1975). [DOI link](https://doi.org/10.1007/BF01932995)

**(Gol73)** Golub, G.; Pereyra, V. "The Differentiation of Pseudo-Inverses
and Nonlinear Least Squares Problems Whose Variables Separate".
SIAM J. Numer. Anal. **1973, 10, 413–432**. [DOI link](https://doi.org/10.1137/0710036)

# Endnotes

[^fitting]: VarPro isn't strictly for function fitting only, since it's a way of rewriting _separable_ nonlinear least squares minimization problems. It's just widely employed for model fitting, which is also what I am using it for.
[^kaufmann-qr]: Note that Kaufmann uses slightly different --but equivalent-- convention for the QR decomposition than this article and (Bae23). This must be taken into account when comparing the equations across publications. Specifically, Kaufmann gives the decomposition as $$Q\Phi P = R$$, whereas (Bae23) and I use the more common $$\Phi P = QR$$ convention. That's not a big deal. It just means, that for Kaufmann $$Q$$ means $$Q^T$$ in this article and vice versa.
[^bae-qr]: While Kaufmann uses QR decomposition with column-pivoting, Bärligea uses QR decomposition without pivoting. There are some slight changes in the formulae to watch out for. Further, the QR decomposition with column-pivoting will be more stable when the function matrix is singular or nearly singular, albeit at a somewhat higher computational cost.
[^norm-ortho]: Hooray for ~~margin~~ endnote proofs: the squared Frobenius norm of a matrix $$\boldsymbol{A}$$ can be written as $$\Vert \boldsymbol{A}\Vert_F^2=\text{trace}(\boldsymbol{A}^T A)$$. With that, it's trivial to show that $$\Vert \boldsymbol{QA}\Vert_F^2=\Vert \boldsymbol{A}\Vert_F^2$$, if $$\boldsymbol{Q}$$ is orthogonal, since $$\boldsymbol{Q Q}^T = \boldsymbol{Q}^T \boldsymbol{Q} = I$$. In the single right hand side case, we would have the euclidean norm of a vector instead of the Frobenius norm. The euclidean norm of a vector is also invariant under orthogonal transformation, i.e. $$\Vert \boldsymbol{Q x}\Vert_2^2 = \Vert \boldsymbol{x}\Vert_2^2$$ for all orthogonal matrices $$\boldsymbol{Q}$$ and all vectors $$\boldsymbol{x}$$.  
[^r2-fullrank]: If $$\boldsymbol{\Phi}_w$$ has full rank, i.e. $$r = n$$, then the matrix $$\boldsymbol{R}_2$$ has zero columns.
