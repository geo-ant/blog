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
specifically and I can only touch on adjacent topics. Additionally, I will
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

# Trust Region Algorithms

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
m_k(\boldsymbol{p}) &:=& f_k + \boldsymbol{g}_k^T \boldsymbol{p} + \frac{1}{2} \boldsymbol{p}^T \boldsymbol{B} \boldsymbol{p} \tag{2a} \label{mk-def} \\
\boldsymbol{g}_k &:=& \nabla f(\boldsymbol{x}_k) \in \mathbb{R}^n, \tag{2b} \label{g-def}
\end{eqnarray}$$

where $$\boldsymbol{g}_k$$ is the gradient of $$f$$ and $$\boldsymbol{B} \in \mathbb{R}^{n x n}$$
is a symmetric matrix that's either the [Hessian](https://en.wikipedia.org/wiki/Hessian_matrix)
of $$f$$ or an approximation of it. We'll come back to this again later and make
this more concrete for the least squares case, but let's continue with
the general purpose trust region description just a little more. In each step
$$k$$ of the algorithm we try to find a _candidate step_ $$\boldsymbol{p}_k$$ by minimizing
our current model $$m_k$$ _inside_ the trust region. Formally:

$$\begin{eqnarray}
\boldsymbol{p}_k &=& \arg \min_{\boldsymbol{p}} m_k(\boldsymbol{x}_k + \boldsymbol{p}) \text{ , s.t. } \lVert \boldsymbol{p} \rVert \leq \Delta \tag{3} \label{min-mk-tr} \\
\end{eqnarray}$$

where the _trust region radius_ $$\Delta \in \mathbb{R}$$ and $$\lVert . \rVert$$ is the
[euclidian vector norm](https://en.wikipedia.org/wiki/Norm_(mathematics)#Euclidean_norm)
or L<sup>2</sup> norm. But wait, eagle-eyed readers will have spotted that
$$\lVert \boldsymbol{p} \rVert \leq \Delta$$ doesn't define an elliptical trust region, but
a spherical one. This leads into the topic of _scaling_, which is one of the
trickier aspects to get right in practice, but not because the theory is hard.
I promise I'll get back to that, but let's proceed without scaling for now.

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
- Given
  - initial guess $$x_0$$
  - intial trust region radius $$\Delta_0 > 0$$
  - step acceptance threshold $$\rho_\min \in [0,\frac{1}{4}]$$
- `while` stopping criterion `not` reached
  - Obtain step $$\boldsymbol{p}_k$$ by (approximately) solving $$\eqref{min-mk-tr}$$.
  - Calculate $$\rho_k$$ using $$\eqref{rho-k}$$.
  - `if` $$\rho_k > \frac{3}{4}$$ then 
    - let $$\Delta_{k+1} = \max(\Delta_k,3 \cdot \lVert \boldsymbol{p}_k \rVert)$$
  - `else if` $$\rho < \frac{1}{4}$$
    - let $$\Delta_{k+1} = \Delta_k/2$$
  - `else`
    - let $$\Delta_{k+1} = \Delta_k$$
  - `end if`
  - `if` $$\rho > \rho_\min$$
    - let $$\boldsymbol{x}_{k+1} = \boldsymbol{x}_k + \boldsymbol{p}_k$$
  - `else`
    - let $$\boldsymbol{x}_{k+1} = \boldsymbol{x}_k$$
  - `end if`
- `end while`

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

# Least Squares Minimization

For least squares minimization we are concerned with minizing, you guessed
it, a sum of squares:

$$f(\boldsymbol{x}) = \frac{1}{2}\sum_{i=1}^{m} r_i(\boldsymbol{x})^2 = \lVert \boldsymbol{r}(\boldsymbol{x})\rVert^2 \tag{5} \label{f-lsqr},$$

where $$\boldsymbol{r}(\boldsymbol{x}) = (r_1(\boldsymbol{x}),\dots, r_m(\boldsymbol{x})) \in \mathbb{R}^m$$ is called the _residual vector_
or the vector of residuals. It turns out (cf. N&W p. 245-247), that we can write
the gradient and the Hessian of $$f$$ in terms of the [Jacobian matrix](https://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant)
$$\boldsymbol{J}(\boldsymbol{x})$$ of $$\boldsymbol{r}(\boldsymbol{x})$$. The
Jacobian is defined as:

$$\boldsymbol{J}(\boldsymbol{x})=
\left(\begin{matrix}
\nabla r_1(\boldsymbol{x})^T \\
\vdots \\
\nabla r_m(\boldsymbol{x})^T \\
\end{matrix}\right) \in \mathbb{R}^{m \times n}, \tag{6} \label{jac-r}$$

and now we can write the gradient and Hessian of $$f$$ as

$$\begin{eqnarray}
\nabla f(\boldsymbol{x}) &=& \boldsymbol{J}(\boldsymbol{x})^T \boldsymbol{r} \tag{7a} \label{grad-f} \\
\nabla^2 f(\boldsymbol{x}) &=& \boldsymbol{J}(\boldsymbol{x})^T \boldsymbol{J}(\boldsymbol{x}) + \sum_{i=1}^{m} r_i(\boldsymbol{x})^T \nabla^2 r_i(\boldsymbol{x}) \approx \boldsymbol{J}(\boldsymbol{x})^T \boldsymbol{J}(\boldsymbol{x}) \tag{7b} \label{hessian-f}.
\end{eqnarray}$$

The approximation $$\boldsymbol{B} \approx \boldsymbol{J}^T \boldsymbol{J}$$ is
typically used for the Hessian of $$f$$ and we'll plug the results above into
eq. $$\eqref{mk-def}$$:


$$\begin{eqnarray}
m_k(\boldsymbol{p}) &=& \frac{1}{2} \lVert \boldsymbol{r}(\boldsymbol{x}) \rVert^2 + \boldsymbol{r}(\boldsymbol{x})^T \boldsymbol{J}(\boldsymbol{x})\boldsymbol{p} + \frac{1}{2} (\boldsymbol{J}(\boldsymbol{x})\boldsymbol{p})^T \boldsymbol{J}(\boldsymbol{x})\boldsymbol{p} \tag{8a} \label{mk-lsqr1} \\
 &=& \frac{1}{2} \lVert \boldsymbol{r}(\boldsymbol{x}) + \boldsymbol{J}(\boldsymbol{x})\boldsymbol{p} \rVert^2 \tag{8b} \label{mk-lsqr2}.
\end{eqnarray}$$

Both formulations are useful. Just as an aside, the second line reveals an interesting insight:
since $$m_k(\boldsymbol{p})$$ is meant to approximate
$$f(\boldsymbol{x}+\boldsymbol{p}) = \frac{1}{2}\lVert \boldsymbol{r}(\boldsymbol{x}+\boldsymbol{p})\rVert^2$$,
we can see that what we did so far actually implies a linear approximation of the
residuals $$\boldsymbol{r}(\boldsymbol{x}+\boldsymbol{p}) \approx \boldsymbol{r}(\boldsymbol{x}) + \boldsymbol{J}(\boldsymbol{x})\boldsymbol{p}$$.
Fascinating, but let's get on with it. Now we have taken to big steps on the
way to solving least squares problem with the Dogleg algorithm, but we still need
to know the first thing about the Dogleg algorithm. So let's look into that next.

# Dogleg Basics

The basic idea of the dogleg algorithm is to approximate a solution to $$\eqref{min-mk-tr}$$
by combining two steps: the _Gauss-Newton step_ and the _steepest descent step_.
Please see N&W pp. 73 and Madsen _et al_ sections 3.1 and 3.3 for theoretical
background on those steps; in this article I'm just going to assume them as given.
Note also that this section already specializes Dogleg to least squares problems.

The Gauss-Newton step $$\boldsymbol{p}_{gn}$$ is given as the solution to 

$$\boldsymbol{p}_{gn}(\boldsymbol{x}) = \arg \min_{p} \lVert \boldsymbol{J}(\boldsymbol{x}) \boldsymbol{p} + f(\boldsymbol{x}) \rVert^2, \tag{9} \label{p-gn}$$

which is just the least squares solution to the following system of equations

$$\boldsymbol{J}(\boldsymbol{x}) \boldsymbol{p} \simeq -f(\boldsymbol{x}). \tag{10}$$

Note the minus sign on the right hand side. It's possible to solve this system
using the [normal equations](https://en.wikipedia.org/wiki/Linear_least_squares),
but that becomes numerically unstable quickly. Using matrix decompositions is
the way to go here and we'll return to this later. For now, let's look at the
steepest descent step, which is given as: 

$$ \boldsymbol{p}_{sd}(\boldsymbol{x}) = -\frac{\lVert \boldsymbol{g}(\boldsymbol{x})\rVert^2}{\lVert \boldsymbol{J}(\boldsymbol{x})\boldsymbol{g}(\boldsymbol{x})\rVert^2} \boldsymbol{g}(\boldsymbol{x}), \tag{11} \label{p-sd}$$

where $$g$$ is the gradient of $$f$$ as defined in eq. $$\eqref{g-def}$$. The
Dogleg algorithm searches for the minimum on a path of finite length, which
is parametrized using a $$\tau \in [0,2]$$ like so:

$$\boldsymbol{p}(\tau) = \left\{
\begin{array}{ll} \tau \, \boldsymbol{p}_{sd}, & \tau \in [0,1] \\
\boldsymbol{p}_{sd} + (1-\tau) (\boldsymbol{p}_{gn}-\boldsymbol{p}_{sd}), & \tau \in (1,2] . \\
\end{array}
\right. \tag{12} \label{dogleg-path}$$

This definition of the path looks a bit unwieldy at first sight, but it has a very simple
geometric interpretation: the path first follows the steepest descent step to
its "tip" and from there in a straight line goes to the "tip" of the Gauss-Newton
step. Overall, this creates a path with a corner in it, as illustrated in Figure 1.

<figure>
 <img src="/blog/images/dogleg/dogleg-step.svg" alt="dogleg step illustration" style="width:100%">
 <figcaption>
Figure 1. The dogleg path is constructed from the steepest descent
step and the Gauss-Newton step. This illustration
also helps us understand where the Dogleg algorithm got it's name. Apparently
the inventor of the algorithm <a href="https://en.wikipedia.org/wiki/Michael_J._D._Powell">Michael Powell</a>
was an avid golfer and was reminded of a <a href = "https://en.wikipedia.org/wiki/Golf_course">dogleg hole</a>
in golf. This figure is heavily inspired by N&W figure 4.4, p. 74.
 </figcaption>
</figure>

It can be shown that $$\lVert m_k(\boldsymbol{p}(\tau)) \rVert$$ will decrease
along the dogleg path and that the path will have at most _one_ intersection
with the trust region boundary[^lemma-4-2]. To take the biggest possible step that's
still inside the trust region, we can chose the _dogleg step_ $$\boldsymbol{p}_{dl}$$
as the point on the dogleg path where it intersects the trust region boundary.
Otherwise the dogleg step goes to the end of the path, which is just the
Gauss-Newton step. So the algorithm for choosing the Dogleg step is:


<div class="pseudocode" markdown="1">
**Algorithm 2** (Classic Dogleg Step)
- Calculate $$\boldsymbol{p}_{sd}$$ as in eq. $$\eqref{p-sd}$$
- `if` $$\lVert \boldsymbol{p}_{sd} \rVert \leq \Delta$$
  - return $$\boldsymbol{p}_{dl} = \Delta \; \boldsymbol{p}_{sd} / \lVert \boldsymbol{p}_{sd}\rVert$$
- `end if`
- Calculate $$\boldsymbol{p}_{gn}$$ as in eq. $$\eqref{p-gn}$$
- `if` $$\lVert \boldsymbol{p}_{gn} \rVert \leq \Delta$$
  - return $$\boldsymbol{p}_{dl} = \boldsymbol{p}_{gn}$$
- `else`
  - Find $$\tau_{dl} \in [1,2) $$ such that $$\lVert \boldsymbol{p}(\tau_{dl}) \rVert = \Delta$$ with $$\boldsymbol{p}(\tau)$$ from $$\eqref{dogleg-path}$$
  - return $$\boldsymbol{p}_{dl} = \boldsymbol{p}(\tau_{dl})$$
- `end if`

<span class="caption">
We call this the classic dogleg step, because later in the article
we will make one tiny modification to the calculation of the
Gauss-Newton step, that brings a significant stability improvement
in practice.
</span>
</div>

To obtain the magical $$\tau_{dl}$$ in the third `if` branch, we have to
realize that we are now in the $$\tau \in [1,2)$$ path segment. That means
the condition $$\lVert \boldsymbol{p}(\tau_{dl}) \rVert = \Delta$$ is now
equivalent to the quadratic equation

$$\lVert \boldsymbol{p}_{sd} + (1-\tau_{dl}) (\boldsymbol{p}_{gn}-\boldsymbol{p}_{sd}) \rVert = \Delta^2. \tag {13}$$

It can be shown that the solution to this equation can always be written as follows
(see Appendix A):

$$
\begin{eqnarray}
\tau_{dl} &=& 1 - \xi + \sqrt{\frac{\Delta^2-\lVert \boldsymbol{p}_{sd}\rVert^2}{\lVert \boldsymbol{p}_{gn}-\boldsymbol{p}_{sd}\rVert^2} + \xi^2} \tag{14a} \label{tau-dl} \\
\xi &:=& \frac{\boldsymbol{p}_{sd}^T (\boldsymbol{p}_{gn} - \boldsymbol{p}_{sd})}{\lVert \boldsymbol{p}_{gn}-\boldsymbol{p}_{sd}\rVert^2} \tag{14b}.
\end{eqnarray}
$$

In principle, we now have all the pieces together. We just use the Dogleg step
from Algorithm 2 and plug this into Algorithm 1 as the step that approximately
solves $$\eqref{min-mk-tr}$$. However, there are a couple of pesky little details
that we still have to take care of. 

# Finding the (Regularized) Gauss-Newton Step

For practical reasons, we'll make one modification to the 



# TODO SCALING!!!!
# TODO REGULARIZED GN STEP
(also note that dogleg requires matrix to be pos def, not sure that the lemma 4.2
is still verified, but the regularization works in practice!)

# Appendix A: Finding $$\tau_{dl}$$

TODO TODO TODO

# Appendix B: Singular Value Decomposition for Finding $$\boldsymbol{p}_{gn}$$

[^local-min]: Convergence guarantees of solver methods are their own beast that I won't touch at all in this article. Everyone that has ever worked with optimization algorithms knows that finding global optima is often a pipe dream and even finding a local optimum can be highly sensitive to starting conditions, implementation details, condition numbers, birthdates, star signs, etc etc...
[^ellipsoid-tr]: Other shapes are available. One very common case is a spherical trust region, which is just a special case of the ellipsoid. Another common case would be a box-shaped region in hyperspace.
[^quadratic-model]: You guessed, it: it doesn't _have_ to be quadratic. See e.g. pp 25, 26 in N&W 2<sup>nd</sup> ed. for a demonstration how a linear model leads to a steepest descent algorithm.
[^lemma-4-2]: See N&W pp. 74, in particular Lemma 4.2 for this. For this lemma to hold, we need the Jacobian $$\boldsymbol{J}$$ to have full rank. We'll later see that we can also use Dogleg in practice for all Jacobians, if we use a _regularized_ Gauss-Newton step, rather than the vanilla step defined in $$\eqref{p-gn}$$.
