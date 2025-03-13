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

What sparked this article is that fact that the core computations in
this library use the SVD matrix decomposition for calculation. While this makes
the algorithm very robust, it also comes with a speed penalty for problems that
don't actually require this degree of robustness. That's why this article describes
how to use the QR-decomposition for those calculations, which is actually the
approach used in many other implementations. The math in this article is the
the original idea of Linda Kaufmann in (Kau75), cf. (Bae23) for a great recap
and some cool extensions to global fitting.

# VarPro with QR

From the previous articles, we know that we can write a separable model function
$$\boldsymbol{f}$$, which depends on the parameters $$\boldsymbol{c}$$ linearly
and on the parameters $$\boldsymbol{\alpha}$$ nonlinearly as

$$
\boldsymbol{f}(\boldsymbol{c},\boldsymbol{\alpha}) = \boldsymbol{\Phi}(\boldsymbol{\alpha})\boldsymbol{c},
$$

where we call $$\boldsymbol{\Phi}(\boldsymbol{\alpha}) \in \mathbb{R}^{m \times n}$$ the model function matrix.


TODO!!!!!!!!!! WEIGHTED MINIMIZATION
!!! mention that we are leaving out the dependency on \alpha for notational simplicity.
!!! it's always there.

$$\boldsymbol{\Phi}_w\boldsymbol{P} = \boldsymbol{Q} \boldsymbol{R}$$

Note that Kaufmann has a slightly different notation for the QR decomposition,
which must be taken into account when reading the equations in that paper [^kaufmann-qr].

!!!!!!!!

$$
\boldsymbol{R} = \left(
\begin{array}{c|c}
\boldsymbol{R_1} & \boldsymbol{R_2} \\
\hline
\boldsymbol{0} & \boldsymbol{0} \\
\end{array}
\right)
$$


$$
\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} = 
\boldsymbol{Q}
\left(
\begin{array}{c|c}
\boldsymbol{0} & \boldsymbol{0} \\
\hline
\boldsymbol{0} & \boldsymbol{I}_{m-r} \\
\end{array}
\right)
\boldsymbol{Q}^T
$$


$$
\boldsymbol{\Phi}^\dagger = 
\boldsymbol{P}
\left(
\begin{array}{c|c}
\boldsymbol{R_1}^-1 & \boldsymbol{0} \\
\hline
\boldsymbol{0} & \boldsymbol{0} \\
\end{array}
\right)
\boldsymbol{Q}^T
$$


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
[^kaufmann-qr]: Specifically, Kaufmann gives the decomposition as $$Q\Phi P = R$$, whereas (Bae23) and I use the more common $$\Phi P = QR$$. That's not a big deal. It just means, that for Kaufmann $$Q$$ means $$Q^T$$ in this article and vice versa.
