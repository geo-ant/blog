---
layout: post
tags: math numerics least-squares
#categories: []
date: 2026-06-30
last_updated:
#excerpt: ''
#image:
#description:
#permalink:
title: "Powell's Dogleg for Least Squares Minimization from Scratch"
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

I've recently released the Rust [`dogleg`](https://docs.rs/dogleg/latest/dogleg/)
crate and I thought I'd document everything you need to implement your own
dogleg solver from scratch. You probably don't want to do that. But if you
did, then here's everything you need to know about it.

# Foreword and References

I'll try to do my best to actually go into details around the algorithm and
implementation details, rather than leaving it at the high-level stuff.
However, since this will be a long article, I'll need to focus on Dogleg
specifically and can only touch on broader adjacent topics. Additionally, I will
focus on the topic of _unconstrained least squares minimization_. Dogleg itself is a general
purpose minimization minimization algorithm and not restricted to least squares.
However, when applied to this important subproblem, we can exploit the structure
of the problem in such a way that we can gain some dramatic increases in robustness.

Obviously _none_ of this is original and the best references I know on the
topic are [Nocedal&Wright](https://link.springer.com/book/10.1007/978-0-387-40065-5)
"Numerical Optimization" 2<sup>nd</sup> ed. (in short N&W),
[Madsen _et al._](https://www2.imm.dtu.dk/pubdb/edoc/imm3215.pdf)
"Methods for Non-Linear Least Squares Problems", the Ceres Solver [documentation](http://ceres-solver.org/nnls_solving.html#dogleg)
and [source code](https://github.com/ceres-solver/ceres-solver), and (to a lesser
extent, but surprisingly) the [Minpack User Guide](https://www.osti.gov/biblio/6997568)
and the [Modern Minpack source code](https://github.com/fortran-lang/minpack).
I'll be pretty sloppy with my citations because most of them would just be Nocedal&Wright
or Madsen _et al_. 

# The Basics of Trust Region Algorithms

Let's start from the basics: we'd like to minimize a scalar-valued
_objective function_ $$f:\mathbb{R}^n \rightarrow \mathbb{R}$$ with respect
to its _parameters_ $$\boldsymbol{x} \in \mathbb{R}^n$$:

$$\min_{\boldsymbol{x}} f(\boldsymbol{x}). \tag{1}\label{min-f}$$

Since we are dealing with least-squares minimization, we'll later set
the objective function to the 2-norm of a vector of residuals, but for now that's
not important.

The important thing is that trust region methods are iterative methods that
produce a sequence $$\boldsymbol{x}_k$$ that (hopefully) converges to an (at least)
local[^local-min] minimum $$x^*$$. They do this by approximating the function $$f$$
in each step $$k$$ inside _model function_ $$m_k : \mathbb{R}^n \rightarrow \mathbb{R}$$,
which (hopefully) does a reasonable job of approximating the function inside
a so-called _trust region_. The trust region is a multidimensional ellipsoid[^ellipsoid-tr],
which is shrunk or expanded by how well the model predicted the actual behavior
of the function. The model function is typically[^quadratic-model] chosen as the
quadratic function taken from the 2<sup>nd</sup> order Taylor expansion
of $$f(\boldsymbol{x}_k+ \boldsymbol{p})$$ around $$\boldsymbol{x}_k$$:

$$\begin{eqnarray}
m_k(\boldsymbol{p}) &:=& f_k + \boldsymbol{g}_k^T \boldsymbol{p} + \frac{1}{2} \boldsymbol{p}^T \boldsymbol{B} \boldsymbol{p} \tag{2} \label{mk-def} \\
\boldsymbol{g}_k &:=& \nabla f(\boldsymbol{x}_k) \in \mathbb{R}^n,
\end{eqnarray}$$

where $$\boldsymbol{g}_k$$ is the gradient of $$f$$ and $$\boldsymbol{B} \in \mathbb{R}^{n x n}$$
is a symmetric matrix that's either the [Hessian](https://en.wikipedia.org/wiki/Hessian_matrix)
of $$f$$ or an approximation of it. We'll come back to this again later and make
this more concrete for the least squares case, but let's continue with
the general purpose trust region description just a little more. In each step
$$k$$ of the algorithm we try to find a _candidate step_ $$\boldsymbol{p}_k$$ by minimizing
our current model $$m_k$$ _inside_ the trust region. Formally:

$$\begin{eqnarray}
\boldsymbol{p}_k &=& \arg \min_{\boldsymbol{p}} m_k(\boldsymbol{x}_k + \boldsymbol{p}) \text{ , s.t. } \lVert \boldsymbol{D}_k \boldsymbol{p} \rVert \leq \Delta \tag{3} \label{min-mk-tr} \\
\boldsymbol{D}_k &=& \text{diag}(d_1,...,d_n) \in \mathbb{R}^{n \times n},
\end{eqnarray}$$

where the _trust region radius_ $$\Delta \in \mathbb{R}$$ and the _diagonal matrix_
$$\boldsymbol{D}_k$$ define the elliptical shape of the trust region. If $$\boldsymbol{D}_k$$
is chosen as the identity matrix, we'd have a spherical trust region. We'll later
see that the matrix $$\boldsymbol{D}_k$$ acts as a scaling matrix with stabilizing
influence that can vary from step to step.

I've called $$\boldsymbol{p}_k$$ a candidate step, because it's not automatically
accepted. In the following, we'll introduce a value $$\rho_k \in \mathbb{R}$$
to serve both as an acceptance criterion for the step and as a decision
criterion when to enlarge or shrink the trust region. Its defined as the
ratio of the _actual reduction_ over the _predicted reduction_:

$$\rho_k = \frac{f(\boldsymbol{x}_k) - f(\boldsymbol{x}_k+\boldsymbol{p}_k)}{m_k(\boldsymbol{0})-m_k(\boldsymbol{p}_k)} \tag {4} \label{rho-k}.$$

Note that the denominator (the predicted reduction) will always be nonnegative
(cf. N&W pp 68, 69). Thus, a $$\rho_k > 0$$ thus tells us that the objective function
would be reduced by taking the step, whereas the $$\rho_k \leq 0$$ indicates that 
it wouldn't be. So using a small value $$\rho_\min \geq 0$$ as a threshold
$$\rho > \rho_\min$$ allows us to accept or reject the step. Nocedal&Wright
give the bound $$\rho_\min \in [0, \frac{1}{4})$$, Madsen _et al_ use
$$\rho_\min = 0$$, Minpack [uses](https://github.com/fortran-lang/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/src/minpack.f90#L1794) $$\rho = 10^{-4}$$,
and Ceres [leaves it configurable](https://github.com/ceres-solver/ceres-solver/blob/806af056feb22a1236baca247b4f4b6e1ea911e5/internal/ceres/trust_region_minimizer.cc#L801)
but [defaults to](https://github.com/ceres-solver/ceres-solver/blob/806af056feb22a1236baca247b4f4b6e1ea911e5/include/ceres/solver.h#L285)
$$\rho_\min = 10^{-3}$$. Very confusing, but at the end not the most important
thing in the world.

The other thing that $$\rho_k$$ can do for us is help us understand whether
the model did a decent job at approximating our actual objective function.
If it did a good job, we increase the trust region radius for the next step;
if it did a bad job, we shrink the radius. If the model was neither particularly good
nor particularly bad at approximating our objective function, we'll just leave the
trust region radius as is. All of this is summarized in the following algorithm.

<div class="pseudocode" markdown="1">
**Algorithm 1** (Trust Region)
- **Given**
  - initial guess $$x_0$$
  - intial trust region radius $$\Delta_0 > 0$$
  - step acceptance threshold $$\rho_\min \in [0,\frac{1}{4}]$$
  - initial elliptical scaling $$\boldsymbol{D}_0$$
- **while** stopping criterion **not** reached
  - Obtain step $$\boldsymbol{p}_k$$ by (approximately) solving $$\eqref{min-mk-tr}$$.
  - Calculate $$\rho_k$$ using $$\eqref{rho-k}$$.
  - **if** $$\rho_k > \frac{3}{4}$$ then 
    - let $$\Delta_{k+1} = \max(\Delta_k,3 \cdot \lVert \boldsymbol{p}_k \rVert)$$
  - **else if** $$\rho < \frac{1}{4}$$
    - let $$\Delta_{k+1} = \Delta_k/2$$
  - **else**
    - let $$\Delta_{k+1} = \Delta_k$$
  - **if** $$\rho > \rho_\min$$
    - let $$\boldsymbol{x}_{k+1} = \boldsymbol{x}_k + \boldsymbol{p}_k$$
    - calculate new elliptical scaling $$\boldsymbol{D}_{k+1}$$
  - **else**
    - let $$\boldsymbol{x}_{k+1} = \boldsymbol{x}_k$$

<span class="caption">
The high level outline of a typical trust region algorithm, including Dogleg, cf
Algorithm 4.1 in Nocedal&Wright and Algorithm 3.21 in the Madsen _et al._
paper. I promise that the handwavy parts will be explained in detail later.
The one thing I won't ever explain are the magical 1/4 and 3/4 constants, cf. Nocedal
and Madsen for details (but not that many).
</span>
</div>

Typically, and in this article, The trust region itself is a multidimensional
ellipsoid. 

# The Basics of Least Squares



[^local-min]: Convergence guarantees of solver methods are their own beast that I won't touch at all in this article. Everyone that has ever worked with optimization algorithms knows that finding global optima is often a pipe dream and even finding a local optimum can be highly sensitive to starting conditions, implementation details, condition numbers, birthdates, star signs, etc etc...
[^ellipsoid-tr]: Other shapes are available. One very common case is a spherical trust region, which is just a special case of the ellipsoid. Another common case would be a box-shaped region in hyperspace.
[^quadratic-model]: You guessed, it: it doesn't _have_ to be quadratic. See e.g. pp 25, 26 in N&W 2<sup>nd</sup> ed. for a demonstration how a linear model leads to a steepest descent algorithm.
