---
layout: post
tags: least-squares algorithm varpro
#categories: []
date: 2025-03-15
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Solving Variable Projection with QR Decomposition'
#
#
# Make sure this image is correct !!!
og_image: 
#
#
# make sure comments are enabled
comments_id: 
math: true
---

TODO INTRO

# Context

VarPro is an algorithm for nonlinear least squares fitting certain classes of model functions
to observations[^fitting]. I've written about the fundamentals of varpro
[here](/blog/2020/variable-projection-part-1-fundamentals/) and its extension
to global fitting [here](/blog/2024/variable-projection-part-2-multiple-right-hand-sides/)
--as well as [other places](/blog/tags/#varpro)-- on this blog. I also maintain
the free and open-source [`varpro`](https://crates.io/crates/varpro) library in the Rust
language. This article is part of a long running series on Variable Projection (VarPro)
on this blog, so I will rush through a lot of the fundamentals. I'll
assume prior knowledge of the previous articles, and I'll be using
the same notation.

# Goal

The core computations in my library use the SVD matrix decomposition. While this makes
the algorithm very robust, it also comes with a speed penalty for problems that
don't actually require this degree of robustness. There is a known way to speed up
the calculations by using the QR decomposition and some mathematical sleights
of hand. In fact, this the approach is used in many other implementations
and it's the original idea of Linda Kaufmann in (Kau75). This article explains
that approach. See also (Bae23) for a great recap as well as some cool extensions
to global fitting[^bae-qr].

# VarPro with QR

From the previous articles, we know that we can write a separable model function
$$\boldsymbol{f}$$, which depends on the parameters $$\boldsymbol{c}$$ linearly
and on the parameters $$\boldsymbol{\alpha}$$ nonlinearly as

$$
\boldsymbol{f}(\boldsymbol{c},\boldsymbol{\alpha}) = \boldsymbol{\Phi}(\boldsymbol{\alpha})\boldsymbol{c},
$$

where we call $$\boldsymbol{\Phi}(\boldsymbol{\alpha}) \in \mathbb{R}^{m \times n}$$,
with $$m>n$$, the model function matrix. Typically, we are interested in some
form of *weighting* for the least squares problem, so that we end up with
the weighted function matrix $$\boldsymbol{\Phi}_w = \boldsymbol{W} \boldsymbol{\Phi} \in \mathbb{R}^{m \times n}$$
and the weighted matrix of observations $$\boldsymbol{Y}_w = \boldsymbol{W Y}$$.
After some math --described in detail in the previous articles-- we end
up with this functional to minimize, which only depends on $$\boldsymbol{\alpha}$$:

$$\mathcal{F}(\boldsymbol{\alpha}) = \Vert \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \boldsymbol{Y}_w \Vert_2^2,$$

TODO!!!!!!!!!! WEIGHTED MINIMIZATION
!!! mention that we are leaving out the dependency on \alpha for notational simplicity.
!!! it's always there.

We can use the QR-decomposition (with column pivoting) of the matrix $$\boldsymbol{\Phi}_w$$
as follows[^kaufmann-qr]. I'll leave out the dependency on $$\boldsymbol{\alpha}$$
for notational simplicity from now on, but all matrices in the following equation
have a dependency on the nonlinear parameters $$\boldsymbol{\alpha}$$:

$$
\boldsymbol{\Phi}_w\boldsymbol{\Pi} = \boldsymbol{Q} \boldsymbol{R},
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
\right] \in \mathbb{R}^{m \times n},
$$

where $$\boldsymbol{R_1} \in \mathbb{R}^{r \times r}$$ is a nonsingular upper
matrix with $$r = \text{rank} \boldsymbol{\Phi}_w$$. The matrix $$\boldsymbol{R}_2$$
contains values that we won't need for the rest of this article. It is useful
to divide $$\boldsymbol{Q}$$ into two sub-matrices as well like so:

$$
\boldsymbol{Q} = 
\left[
\begin{array}{c|c}
\boldsymbol{Q}_1 & \boldsymbol{Q}_2
\end{array}
\right],
$$

where $$\boldsymbol{Q}_1 \in \mathbb{R}^{m \times r}$$ is the submatrix of the
first $$r$$ columns, and $$\boldsymbol{Q}_2 \in \mathbb{R}^{m \times (m-r)}$$
contains the rest.
 

!!!!!!!!



$$
\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} = 
\boldsymbol{Q}
\left[
\begin{array}{c|c}
\boldsymbol{0} & \boldsymbol{0} \\
\hline
\boldsymbol{0} & \boldsymbol{I}_{m-r} \\
\end{array}
\right]
\boldsymbol{Q}^T
$$


$$
\boldsymbol{\Phi_w}^\dagger = 
\boldsymbol{P}
\left[
\begin{array}{c|c}
\boldsymbol{R_1}^-1 & \boldsymbol{0} \\
\hline
\boldsymbol{0} & \boldsymbol{0} \\
\end{array}
\right]
\boldsymbol{Q}^T
$$


$$
\frac{\partial \boldsymbol{Q}_2^T}{\boldsymbol{\alpha}_k} \approx -\boldsymbol{Q}_2^T\frac{\partial \boldsymbol{\Phi_w}}{\boldsymbol{\alpha}_k} \boldsymbol{\Phi_w}^\dagger
$$

There is a typo in the Kaufmann paper for the final form of this equation, which
leaves out the minus ($$-$$). The previous formulae and the derivation in (Bae23) make
it clear that this is an oversight.

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
[^kaufmann-qr]: Note that Kaufmann uses slightly different --but equivalent-- convention for the QR decomposition than this article and (Bae23). This must be taken into account when reading comparing the equations across publications.Specifically, Kaufmann gives the decomposition as $$Q\Phi P = R$$, whereas (Bae23) and I use the more common $$\Phi P = QR$$ convention. That's not a big deal. It just means, that for Kaufmann $$Q$$ means $$Q^T$$ in this article and vice versa.
[^bae-qr]: While Kaufmann uses QR decomposition with column-pivoting, Bärligea uses QR decomposition without pivoting. There are some slight changes in the formulas to watch out for. Further, the QR decomposition with column-pivoting will be more stable when the function matrix is singular or nearly singular, albeit at a somewhat higher computational cost.
