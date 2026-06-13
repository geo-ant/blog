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

# 1 Foreword and References

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
I'll be pretty sloppy with my citations because most of them would just be N&W
or Madsen _et al_. 

# 2 Trust Region Algorithms

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
&=& f(\boldsymbol{x}+\boldsymbol{p}) + \mathcal{O}(\lVert \boldsymbol{p} \rVert^2) \\
\boldsymbol{g}_k &:=& \nabla f(\boldsymbol{x}_k) \in \mathbb{R}^n, \tag{2b} \label{g-def}
\end{eqnarray}$$

where $$\boldsymbol{g}_k$$ is the gradient of $$f$$ and $$\boldsymbol{B} \in \mathbb{R}^{n x n}$$
is a symmetric matrix that's either the [Hessian](https://en.wikipedia.org/wiki/Hessian_matrix)
of $$f$$ or an approximation of it. We'll come back to this again later and make
this more concrete for the least squares case, but let's continue with
the general purpose trust region description just a little more. In each step
$$k$$ of the algorithm we try to find a _candidate step_ $$\boldsymbol{p}_k \in \mathbb{R}^n$$ by minimizing
our current model $$m_k$$ _inside_ the trust region. Formally:

$$
\boldsymbol{p}_k = \arg \min_{\boldsymbol{p}} m_k(\boldsymbol{x}_k + \boldsymbol{p}) \text{ , s.t. } \lVert \boldsymbol{p} \rVert \leq \Delta \tag{3} \label{pk-def} 
$$

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
$$\rho > \rho_\min$$ allows us to accept or reject the step. N&W
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
- **Given**:
  - initial guess $$x_0$$
  - intial trust region radius $$\Delta_0 > 0$$
  - step acceptance threshold $$\rho_\min \in [0,\frac{1}{4}]$$
- `while` stopping criterion `not` reached
  - Obtain step $$\boldsymbol{p}_k$$ by (approximately) solving $$\eqref{pk-def}$$.
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
Algorithm 4.1 in N&W and Algorithm 3.21 in the Madsen _et al._
paper. I promise that the handwavy parts will be explained in detail later.
The one thing I won't ever explain are the magical 1/4 and 3/4 constants, cf. Nocedal
and Madsen for details (but not that many).
</span>
</div>

Typically, and in this article, The trust region itself is a multidimensional
ellipsoid. 

# 3 Least Squares Minimization

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
\nabla f(\boldsymbol{x}) &=:& \boldsymbol{g}(\boldsymbol{x}) = \boldsymbol{J}(\boldsymbol{x})^T \boldsymbol{r} \tag{7a} \label{grad-f} \\
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

# 4 Dogleg Basics

The basic idea of the dogleg algorithm is to approximate a solution to $$\eqref{pk-def}$$
by combining two steps: the _Gauss-Newton step_ and the _steepest descent step_.
Please see N&W pp. 73 and Madsen _et al_ sections 3.1 and 3.3 for theoretical
background on those steps; in this article I'm just going to assume them as given.
Note also that this section already specializes Dogleg to least squares problems.

The Gauss-Newton step $$\boldsymbol{p}_{gn}$$ is given as the solution to 

$$\begin{eqnarray}
\boldsymbol{J}(\boldsymbol{x})^T \boldsymbol{J}(\boldsymbol{x}) \boldsymbol{p}_{gn} = - \boldsymbol{J}^T(\boldsymbol{x}) \boldsymbol{r}(\boldsymbol{x}) \label{normal-eqs} \tag{9a} \\
\Leftrightarrow \boldsymbol{p}_{gn}(\boldsymbol{x}) = \arg \min_{p} \lVert \boldsymbol{J}(\boldsymbol{x}) \boldsymbol{p} + \boldsymbol{r}(\boldsymbol{x}) \rVert^2, \tag{9b} \label{p-gn}
\end{eqnarray}$$

which is just the least squares solution to the following system of equations

$$\boldsymbol{J}(\boldsymbol{x}) \boldsymbol{p}_{gn} \simeq -\boldsymbol{r}(\boldsymbol{x}). \tag{10}$$

Note the minus sign on the right hand side. It's possible to solve this system
by directly inverting the
[normal equations](https://en.wikipedia.org/wiki/Linear_least_squares) $$\eqref{normal-eqs},
but that becomes numerically unstable quickly. Using matrix decompositions is
the way to go here and we'll return to this later. For now, let's look at the
steepest descent step, which is given as: 

$$ \boldsymbol{p}_{sd}(\boldsymbol{x}) = -\frac{\lVert \boldsymbol{g}(\boldsymbol{x})\rVert^2}{\lVert \boldsymbol{J}(\boldsymbol{x})\boldsymbol{g}(\boldsymbol{x})\rVert^2} \boldsymbol{g}(\boldsymbol{x}), \tag{11} \label{p-sd}$$

where $$g$$ is the gradient of $$f$$ as defined in eq. $$\eqref{grad-f}$$. The
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
- **Given**: Jacobian $$\boldsymbol{J}$$, gradient $$\boldsymbol{g}$$, residuals $$\boldsymbol{r}$$
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
solves $$\eqref{pk-def}$$. However, there are a couple of pesky little details
that we still have to take care of. 

# 5 Parameter Scaling

Parameter scaling is used to address the fact that an objective function can
be very sensitive to changes in certain parameters, while it's less sensitive
to others. In this case, we say that the objective function is _poorly scaled_,
which can manifest as the minimizer being in a narrow valley. In this case,
elliptical trust regions are a much better fit than the spherical trust regions
we've considered so far. The test suite of my Dogleg implementation taught
me that compensating for parameter scaling is one of the most important things
to implement for going from a decent implementation to a great one.

Elliptical trust regions are defined by

$$\begin{eqnarray}
\lVert \boldsymbol{D} \boldsymbol{p} \rVert &\leq& \Delta, \tag{15a} \label{elliptical-tr} \\
\boldsymbol{D} &:=& \text{diag}(d_1,\dots,d_n) \in \mathbb{R}^{n \times n},\; d_j > 0 \tag{15b} \label{d-def}
\end{eqnarray}$$

where $$\boldsymbol{D}$$ is an invertible diagonal matrix. Now the optimization problem
in eq. $$\eqref{pk-def}$$ becomes

$$\boldsymbol{p}_k = \arg \min_{\boldsymbol{p}} m_k(\boldsymbol{p}) \text{ , s.t. } \lVert \boldsymbol{D p} \rVert \leq \Delta \tag{16} \label{pk-elliptical},$$

where the only change to the problem before is the elliptical shape of the trust
region. There are ways to express the solution to this problem using the elliptical
bounds, but a much simpler alternative is to perform a coordinate transform
such that we are now working in a _scaled_ coordinate system for the steps.

$$\boldsymbol{\widetilde{p}} = \boldsymbol{D p}. \tag{17} \label{scaled-p}$$

By substituting this into $$\eqref{pk-elliptical}$$, we obtain a
minimization problem with spherical bounds in the scaled step coordinates:

$$\begin{eqnarray}
\boldsymbol{\widetilde{p}}_k &=& \arg \min_{\boldsymbol{p}} \widetilde{m}_k(\boldsymbol{\widetilde{p}}) \text{ , s.t. } \lVert \boldsymbol{\widetilde{p}} \rVert \leq \Delta \tag{18a} \label{mk-scaled}, \\
\widetilde{m}_k(\boldsymbol{\widetilde{p}}) &:=& \frac{1}{2} \lVert \boldsymbol{r}(\boldsymbol{x}) \rVert^2 + \boldsymbol{\widetilde{g}}(\boldsymbol{x})^T \boldsymbol{\widetilde{p}} + \frac{1}{2} (\boldsymbol{\widetilde{J}}(\boldsymbol{x})\boldsymbol{\widetilde{p}})^T \boldsymbol{\widetilde{J}}(\boldsymbol{x})\boldsymbol{\widetilde{p}} \tag{18b} \label{mk-scaled-1} \\
 &=& \frac{1}{2} \lVert \boldsymbol{r}(\boldsymbol{x}) + \boldsymbol{\widetilde{J}}(\boldsymbol{x})\boldsymbol{\widetilde{p}} \rVert^2 \tag{18c} \label{mk-scaled2} \\
\boldsymbol{\widetilde{J}}(\boldsymbol{x}) &:=& \boldsymbol{J}(\boldsymbol{x}) \boldsymbol{D}^{-1}  \tag{18d} \label{j-scaled} \\
\boldsymbol{\widetilde{g}}(\boldsymbol{x}) &:=& \boldsymbol{D}^{-1} \boldsymbol{g}(\boldsymbol{x}) = \boldsymbol{\widetilde{J}}(\boldsymbol{x})^T \boldsymbol{r}(\boldsymbol{x})   \tag{18e} \label{g-scaled},
\end{eqnarray}$$

where we call $$\boldsymbol{\widetilde{g}}$$ the _scaled_ gradient and
$$\boldsymbol{\widetilde{J}}$$ the _scaled_ Jacobian. The neat thing is that,
at each iteration, we can just calculate the _scaled_ dogled step using the
same math as above as long as we consistently use the scaled Jacobian and
gradient for the calculations. Only to calculate the next evaluation point
$$\boldsymbol{x}_{k+1} = \boldsymbol{x}_k + \boldsymbol{p}_k$$, do we have
to translate the step into unscaled coordinates by using
$$\boldsymbol{p}_k = \boldsymbol{D}^{-1} \widetilde{\boldsymbol{p}}_k$$.


## 5.1 Practical Parameter Scaling

Now, let's look at how to actually implement practically useful parameter
scaling. Madsen _et al._ don't mention scaling at all, while N&W simply state:
"Information to construct the scaling matrix $$\boldsymbol{D}$$ can be derived
from the second derivatives [...]. We can allow $$\boldsymbol{D}$$ to change
from iteration to iteration" (N&W section 4.5). For more practically useful
information, we have to turn to gold-standard implementations, like Ceres
Solver or Minpack. The Minpack User Guide
[section 2.5](https://www.osti.gov/biblio/6997568) gives some good theoretical
and practical insight. However, the best performing scaling I've
found is implemented in the Ceres Solver[^test-suite].

### 5.1.1 Static and Dynamic Scaling

Curiously, Ceres combines two types of scaling. To be able to talk about these
two types, we are going to introduce some (non-standard) vocabulary:
_Static Scaling_ $$\boldsymbol{D}_s$$ and _Dynamic Scaling_ $$\boldsymbol{D}_d$$.
Ceres calls those _Jacobi scaling_, and _diagonal scaling_, respectively.
I find the names misleading because both matrices are diagonal matrices, both
matrices act on the Jacobian (among other things), and they are calculated based
on the Jacobian (though slightly differently).

The matrix $$\boldsymbol{D}_s$$is calculated _once_ in the first iteration and
stays the same for the whole runtime of the algorithm. It's intent
is to _"improve the conditioning of the Jacobian"_[^ceres-static-scaling]:

$$\begin{eqnarray}
  \boldsymbol{D}_s &=& \text{diag}(d_{s,1},\,\dots\,,d_{s,n}) \in \mathbb{R}^n \tag{19a} \label{Ds} \\ 
  d_{s,i} &=& |\boldsymbol{j}_i|+1 \tag{19b}, \\
\end{eqnarray}$$

where $$\boldsymbol{j}_i$$ is the $$i$$-th _column_ of the Jacobian. For this
matrix, since it's only calculated once in the first iteration, this is the
Jacobian at initialization. Using this scaling indeed makes the
algorithm perform better in my test suite, but I'll be honest: this was a bit
of a surprise to me, once I understood what was going on.

The dynamic scaling matrix $$\boldsymbol{D}_d^{(k)}$$ is updated everytime the Jacobian
changes, i.e. _everytime a step is taken_. The dynamic scaling implemented by Ceres
is very similar to the scaling described in the Minpack User guide. It's primary
intent is to give us an adaptive elliptical trust region. I've included the $$(k)$$
superstep to make the explicit dependence on the step obvious. It's calculated
as [^ceres-dynamic-scaling]:

$$\begin{eqnarray}
  \boldsymbol{D}_d^{(k)} &=& \text{diag}(d_{d,1}^{(k)},\,\dots\,,d_{d,n}^{(k)}) \in \mathbb{R}^n \tag{20a} \label{Dd} \\ 
  d_{d,i}^{(k)} &=& \max(\min(d_{max}, |\boldsymbol{j}_i^{(k)}|),d_{min}), \tag{20b} \\
\end{eqnarray}$$

where $$\boldsymbol{j}_j^{(k)}$$ agian denotes the $$i$$-th column of the Jacobian,
this time evaluated at the current step with index $$k$$. The diagonal elements
are just the column-norms of the Jacobian clamped to a the range $$[d_{min}, d_{max}]$$,
where the default values for the endpoints of the range in Ceres are:

$$\begin{eqnarray}
d_{min} &=& 10^{-3} \\
d_{max} &=& 10^{-16} \\
\end{eqnarray}$$


We can combine those scaling matrices into one _step dependent_ diagonal scaling
matrix $$\boldsymbol{D}_k$$, where $$k$$ is the index of the current step.

$$\boldsymbol{D}_k = \boldsymbol{D}_s \boldsymbol{D}_d^{(k)} \tag{21} \label{Dk}$$

### 5.1.2 Implementing Parameter Scaling

Don't worry if this has all been a bit confusing so far, we're going to tie it
together now. At each iteration, we calculate the scaling matrix $$\boldsymbol{D}_k$$
as given in $$\eqref{Dk}$$. We can then use this matrix to calculate
the scaled Jacobian $$\widetilde{\boldsymbol{J}}$$ from the Jacobian $$\boldsymbol{J}$$,
using $$\eqref{j-scaled}$$ and from that the scaled gradient using $$\eqref{g-scaled}$$.

We're calculating the dogleg step in scaled space by using the same algorithm
as described above. The two ingredients to the dogleg step are the $$\widetilde{\boldsymbol{p}}_{gn}$$
and $$\widetilde{\boldsymbol{p}}_{sd}$$, which are the Gauss-Newton and the
steepest descent step, respectively, both in scaled space. From that, we
calculate the final dogleg step in scaled space $$\widetilde{\boldsymbol{p}_{dl}}$$
using Algorithm 2. We can still use Algorithm 1 to perform the trust region step,
but we have to be sure to _unscale_ the dogleg step using
$$\boldsymbol{p}_{dl} = \boldsymbol{D}^{-1} \widetilde{\boldsymbol{p}}_{dl}$$
before using it to get the next step
$$\boldsymbol{x}_{k+1} = \boldsymbol{x}_k + \boldsymbol{p}_k$$.

To obtain $$\widetilde{\boldsymbol{p}}_{sd}$$, we just use modify $$\eqref{p-sd}$$
with the scaled gradient and Jacobian: 

$$ \widetilde{\boldsymbol{p}}_{sd}(\boldsymbol{x}) = -\frac{\lVert \widetilde{\boldsymbol{g}}(\boldsymbol{x})\rVert^2}{\lVert \widetilde{\boldsymbol{J}}(\boldsymbol{x})\widetilde{\boldsymbol{g}}(\boldsymbol{x})\rVert^2} \widetilde{\boldsymbol{g}}(\boldsymbol{x}), \tag{22} \label{p-sd-scaled}$$

In the next section, I'll explain how calculate the Gauss-Newton step, since
I wanted to introduce regularization to it as well. Note, that we'll never
actually need to form the scaled Jacobian to calculate $$\eqref{p-sd-scaled}$$,
because we can just rewrite the matrix vector product in the denominator as
$$\widetilde{\boldsymbol{J}}\widetilde{\boldsymbol{g}} = \boldsymbol{J}(\boldsymbol{D}^{-1} \widetilde{\boldsymbol{g}})$$,
which saves a couple of FLOPS, but probably won't matter that much in the
grand scheme of things.

# 6 Finding the Regularized Gauss-Newton Step

Instead of using $$\eqref{normal-eqs}$$ to calculate the Gauss-Newton step using
suitable matrix decompositions, we'll modify the equations to calculate the
[regularized Gauss-Newton step](https://en.wikipedia.org/wiki/Gauss%E2%80%93Newton_algorithm#Improved_versions)
for increased stability. None of the sources I know for the Dogleg Algorithm
mentions this, but Ceres does it to measurably improve the stability of the
algorithm[^ceres-regularization]. The regularization is performed in
_scaled space_ such that the regularized normal equations are:

$$
(\widetilde{\boldsymbol{J}}^T \widetilde{\boldsymbol{J}} + \mu \boldsymbol{I}) \widetilde{\boldsymbol{p}}_{gn} = - \widetilde{\boldsymbol{J}}^T \boldsymbol{r} \label{normal-eqs-scaled-regularized} \tag{23}, \\
$$

where I've omitted the explicit dependency on $$\boldsymbol{x}$$ for notational
convenience. Here $$\mu \in \mathbb{R}$$ is a scalar with $$\mu > 0$$ and
$$\boldsymbol{I} \in \mathbb{R}^{n \times n}$$ is the identity matrix.
Together they improve the conditioning of the approximate
Hessian $$\widetilde{\boldsymbol{J}}^T\widetilde{\boldsymbol{J}}$$
in scaled space. By substituting
$$\widetilde{\boldsymbol{J}} = \boldsymbol{J}\boldsymbol{D}^{-1}$$,
$$\boldsymbol{p}_{gn} = \boldsymbol{D}^{-1}\widetilde{\boldsymbol{p}}_{gn}$$ and
then rewriting a little, we can see that equation $$\eqref{normal-eqs-scaled-regularized}$$
is equivalent to solving the following unscaled system:

$$
(\boldsymbol{J}^T \boldsymbol{J} + \mu \boldsymbol{D}^2) \boldsymbol{p}_{gn} = - \boldsymbol{J}^T \boldsymbol{r} \label{normal-eqs-unscaled-regularized} \tag{24}, \\
$$

which is also equivalent to the following (augmented) least squares problem:

$$
\boldsymbol{p}_{gn} =
\arg\min_{\boldsymbol{p}}
\left\lVert
\left(\begin{matrix}
\boldsymbol{J} \\
\sqrt{\mu}\boldsymbol{D}
\end{matrix}\right)
\boldsymbol{p} -
\left(\begin{matrix}
\boldsymbol{-r} \\
\boldsymbol{0}
\end{matrix}\right)
\right\rVert^2
\label{ceres-augmented-system-regularized}
\tag{25}
$$

which is just another way of saying to solve the following system in a
least-squares sense:

$$
\left(\begin{matrix}
\boldsymbol{J} \\
\sqrt{\mu}\boldsymbol{D}
\end{matrix}\right)
\boldsymbol{p}_{gn} \simeq
-\left(\begin{matrix}
\boldsymbol{r} \\
\boldsymbol{0}
\end{matrix}\right)
\tag{26}
\label{augmented-least-squares-sense}.
$$

Ceres uses [QR decomposition](https://en.wikipedia.org/wiki/QR_decomposition) to solve this
augmented system in a least squares sense[^ceres-regularized-gn], but also allows
other solvers to be selected. It's also
possible to use [singular value decomposition](https://en.wikipedia.org/wiki/Singular_value_decomposition)(SVD)
to solve the system. That one even allows us to reuse the SVD of $$\boldsymbol{J}$$
for different $$\mu$$, but is typically not worth its high computational cost
compared to other solvers, which is why it's not available in Ceres.

All formulations $$\eqref{normal-eqs-scaled-regularized}$$ - $$\eqref{augmented-least-squares-sense}$$
are equivalent, but there's one small caveat: if we use any of the formulations
$$\eqref{normal-eqs-unscaled-regularized}$$ - $$\eqref{augmented-least-squares-sense}$$,
then we solve for the _unscaled_ Gauss-Newton step, and we have to transform
it into _scaled space_ using $$\widetilde{\boldsymbol{p}}_{gn} = \boldsymbol{D} \boldsymbol{p}_{gn}$$
for use in Algorithm 2 together with $$\widetilde{\boldsymbol{p}}_{sd}$$
to calculate the _scaled_ Dogleg step $$\widetilde{\boldsymbol{p}}_{dl}$$. Only
after the complete scaled Dogleg step has been calculated, can we unscale it to
obtain the next iterate $$\boldsymbol{x}_{k+1}$$. If that all seems a bit roundabout,
it's of course fine to use $$\eqref{normal-eqs-scaled-regularized}$$, but the
advantage of using the other formulations is that we (like in the previous section)
can use those without having to ever form the scaled Jacobian explicitly.

## 6.1 Updating the Regularization Parameter $$\mu$$

To see how to chose the regularization paramter, we'll dig into the Ceres
source code again. There are two imporant values $$\mu_{min} = 10^{-8}$$
and $$\mu_{max} = 1$$, which are hard-coded[^cere-mu-min-max]. The parameter
$$\mu$$ starts out with $$\mu_{min}$$ and is always restricted to the range
$$[\mu_{min}, \mu_{max}]$$ [^ceres-mu-range]. When a linear solver _fails_ to solve
the system $$\eqref{augmented-least-squares-sense}$$ in a least squares sense,
the value of $$\mu$$ gets increased by a factor $$10$$ and the solution is
retried [^ceres-mu-inc]. If the solver cannot solve before hitting the limit $$\mu_{max}$$,
the optimization is terminated with failure. The value of $$\mu$$ persists
between iterations, but it is decreased by a factor of $$5$$ every time a
step is accepted[^ceres-mu-dec].

This scheme adds a little bit of complexity, but as I said before it _is_
worth it. Luckily, if we're using a solver that _can't fail_,
then $$\mu$$ always stays at $$\mu_{min}$$. Examples of linear solvers that can't
fail are e.g. SVD[^svd-regularized] or column-pivoted QR, the latter of which _is_ an option in
Ceres.

# 7 Stopping Criteria

Before putting this all together, there's more thing I completely glossed
over in Algorithm 1 and that is "while stopping criterion `not` reached". So
let's talk about stopping criteria, specifically convergence criteria that
tell us whether we think a solution is good enough or whether we're possibly
stuck. N&W doesn't define stopping criteria, but Madsen _et al._, the Minpack
User Guide section 2.3, and (obviously) the Ceres source code. I'll list the criteria
in different sections and we'll see there's a decent amount of overlap as well.

## 7.1 Minpack Stopping Criteria

I'll label the stopping criteria from Minpack with **MPK-1**, **MPK-2**,... to
distinguish them from the criteria of other sources. Firstly, Minpack describes three
convergence criteria to try and estimate how far our current iterate is
away from an optimal solution.

* **MPK-1**: The _Xtol Criterion_ estimates how close we are to a true solution and is
  stated as

  $$\Delta \leq x_{tol} \cdot \lVert \boldsymbol{Dx} \rVert, \tag{27} \label{minpack-xtol}$$

  where $$x_{tol} \in \mathbb{R}$$ and $$x_{tol} > 0$$. Formally, this criterion
  _tries_ to guarantee a bound on the distance of the current parameter estimate
  $$\boldsymbol{x}_k$$ from the true, unknown optimum $$\boldsymbol{x}^\star$$
  such that $$\lVert \boldsymbol{D}(\boldsymbol{x}_k-\boldsymbol{x}^\star) \rVert \leq x_{tol} \lVert \boldsymbol{Dx}^\star \rVert$$.

* **MPK-2**: The _Ftol Criterion_ tries to bound 
  $$\lVert f(\boldsymbol{x})\rVert \leq (1+f_{tol}) \cdot \lVert f(\boldsymbol{x}^\star) \rVert$$.
  Again $$f_{tol} \in \mathbb{R}$$ and $$f_{tol} > 0$$ is a user-supplied tolerance.
  Since the true optimum is unknown, the test is defined in terms of the
  normalized _actual reduction_ and the normalized _predicted reduction_ defined
  as

  $$\begin{eqnarray}
  \text{ACTRED} &:=& \frac{f(\boldsymbol{x}_{k})- f(\boldsymbol{x}_{k+1})}{f(\boldsymbol{x}_{k})} \\[0.5em]
  \text{PREDRED} &:=& \frac{ m_k(\boldsymbol{0})- m_k(\boldsymbol{p}_{k})}{ f(\boldsymbol{x}_{k})}. \\
  \end{eqnarray}$$

  The criterion is considered fulfilled if the following three conditions are met:

  $$\begin{eqnarray}
  \text{PREDRED} &\leq& f_{tol} \tag{28a} \\\
  |\text{ACTRED}| &\leq& f_{tol} \tag{28b} \\
  \text{ACTRED}  &\leq& 2\cdot\text{PREDRED} \tag{28c}
  \end{eqnarray}$$

  Since this criterion sets attempts to set a relative bound on the residuals
  compared to their optimum, this won't be hit if $$f(\boldsymbol{x}^\star)=0$$,
  unless our residuals also vanish. It's therefore useful to supplement this
  criterion with an absolute check $$f(\boldsymbol{x}_k) < \epsilon_f$$, where
  $$\epsilon_f$$ is a small tolerance, possibly in the order of machine precision.

* **MPK-3**: The _Gtol Criterion_ tries to estimate if we're at a minimum by checking
  whether the gradient at the current iterate vanishes. Instead of just
  comparing the maximum absolute value of the gradient against a threshold,
  this criterion checks:

  $$ \max_i\left\{ \frac{| \boldsymbol{j}_i^T \; \boldsymbol{r}(\boldsymbol{x}_k)|}{\lVert \boldsymbol{j}_j\rVert \cdot \lVert \boldsymbol{r}(\boldsymbol{x}_k)\rVert}\right\} \leq g_{tol}, \tag{29} \label{minpack-gtol}, $$

  where $$\boldsymbol{j}_i$$ is the $$i$$-th column of the Jacobian evaluated
  at the current parameters $$\boldsymbol{x}_k$$. Formulating the gradient
  criterion like this makes the criterion more robust to scaling in $$f$$, but it
  might not always confer a practical advantage. Again $$g_{tol} > 0$$ is a user
  supplied real number.

By default, the Minpack implementation sets $$g_{tol} = 0$$ and the user guide
gives some guidance on the values of $$x_{tol}$$ and $$f_{tol}$$:

> In general, $$x_{tol}$$ and $$f_{tol}$$ should be smaller than $$10^{-5}$$;
> recommended values for these tolerances are on the order of the square root
> of the machine precision.

The Minpack implementation actually checks each of the three criteria above _twice_.
First, it performs the checks with the user supplied tolerances. If any of the convergence
criteria is hit, then the optimizer terminates successfully. Second, it performs
the checks _again_ but uses machine epsilon instead of the user supplied tolerances.
If any of those checks hit, then the optimization terminates with failure because
it's reasonable to assume that no further progress can be made.

The Minpack implementation actually checks one more hard stopping criterion,
and that's this one[^minpack-feval]:

* **MPK-4**: The _Max Eval_ criterion makes the algorithm terminate when the number of
  times the function $$f$$ was evaluated exceeds a certain limit $$N_{feval}$$.
  At other places in the libraries similar parameters have default values
  of $$N_{feval} = 100\cdot(n+1)$$ or $$200\cdot (n+1)$$, where $$n$$ is the
  number of elements in $$\boldsymbol{x}$$, i.e. the number of variables.

The number of function evaluations is highly correlated to the number of
iterations, but it increases every time that a step is _evaluated_ rather than
every time a step is actually _accepted_. Since function evaluations may be costly,
this is a more stringent bound on the limit of computations to perform than
the number of iterations, where each iteration possibly tests many steps.

## 7.2 Madsen _et al_. Stopping Criteria

To label the stopping criteria in the Madsen, Nielsen, and Tingleff paper I'll
use the prefix **MNT**. The following four stopping criteria are defined:

* **MNT-1**: The _Max Gradient Element_ criterion terminates the optimization
  with success under the condition

  $$\lVert \boldsymbol{g} \rVert_{\infty} \leq \epsilon_g,$$

  where $$\boldsymbol{g}$$ is the gradient at the current iterate $$\boldsymbol{x}_k$$
  and $$\epsilon_g > 0$$ is a real number.

* **MNT-2**: The _Step Norm Criterion_ terminates the optimization with success

  when

  $$\lVert \boldsymbol{p}_{dl} \rVert \leq \epsilon_p \cdot (\lVert \boldsymbol{x_k})
  \rVert + \epsilon_p),$$

  where $$\boldsymbol{p}_{dl}$$ is the current _unscaled_ Dogleg step and
  $$\epsilon_p > 0$$ is a real number.

* **MNT-3**: The _Max Residual Criterion_ terminates with success if

  $$\lVert \boldsymbol{r} \rVert_{\infty} \leq \epsilon_r,$$

  where $$\boldsymbol{r}$$ is the residual vector, evaluated at the current
  iterate $$\boldsymbol{x}_k$$ and $$\epsilon_r > 0$$ a real number.

* **MNT-4** The _Max Iteration Count Criterion_ terminates with failure if
  the iteration count surpasses a defined limit $$N_{iter}$$:

  $$k > N_{iter}$$

We can already see that there's a lot of conceptual overlap in the stopping
criteria between Minpack and Madsen _et al._. But there's also a decent
amount of subtle (and not so subtle) differences. Although the Minpack criteria look
more sophisticated, my experience is that they don't always perform better in practice.

## 7.3 Ceres' Stopping Criteria

Ceres introduces some new stopping criteria, but also takes a _almost_ all
from Madsen _et al_. like so:

* **MNT-1** with default _gradient tolerance_ of $$\epsilon_g = 10^{-10}$$
* **MNT-3** with default _parameter tolerance_ of $$\epsilon_p = 10^{-8}$$ 
* **MNT-4** with a default iteration limit of $$N_{iter} = 50$$

Additionally, Ceres defines a number of custom stopping criteria, which I'll
prefix with **CRS**

* **CRS-1**: The _Function Tolerance Criterion_[^ceres-function-tol] is used
  instead of **MNT-2** and terminates successfully if

  $$|\text{ACTRED}| \leq \epsilon_a,$$

  where $$\text{ACTRED}$$ is defined as in **MPK-2** and $$\epsilon_a = 10^{-6}$$
  by default.

* **CRS-2**: The _Min Trust Region Radius_[^ceres-min-delta] criterion terminates with success
  if the trust region radius $$\Delta$$ is below a certain threshold:

  $$\Delta \leq \Delta_{min},$$

  where by default $$\Delta_{min} = 10^{-32}$$.

* **CRS-3**: The _Max Solver Time_[^ceres-max-time] criterion terminates with
  failure if the total time that the solver took exceeds a limit that
  defaults to tens of years.

All the criterions above (including the ones used from Madsen _et al_.) make
the Ceres solver indicate `CONVERGENCE` on success and `NO_CONVERGENCE` on
failure. However, Ceres also has a distinct hard `FAILURE` mode, which is
different from `NO_CONVERGENCE`. The following criteria terminate the algorithm
in a hard failure mode:

* **CRS-4**: Hard failure is triggered if function or Jacobian evaluation fails
  or if the linear solver cannot find a regularized Gauss-Newton step despite
  having hit the maximum regularization parameter $$\mu$$.

* **CRS-5**: Hard failure is triggered if too many consecutive steps were
  rejected[^ceres-consecutive-steps]. By default, the limit is 5 consecutive
  invalid steps.

# Appendix A: Finding $$\tau_{dl}$$

TODO TODO TODO

# Appendix B: Singular Value Decomposition for Finding $$\boldsymbol{p}_{gn}$$

[^local-min]: Convergence guarantees of solver methods are their own beast that I won't touch at all in this article. Everyone that has ever worked with optimization algorithms knows that finding global optima is often a pipe dream and even finding a local optimum can be highly sensitive to starting conditions, implementation details, condition numbers, birthdates, star signs, etc etc...
[^ellipsoid-tr]: Other shapes are available. One very common case is a spherical trust region, which is just a special case of the ellipsoid. Another common case would be a box-shaped region in hyperspace.
[^quadratic-model]: You guessed, it: it doesn't _have_ to be quadratic. See e.g. pp 25, 26 in N&W 2<sup>nd</sup> ed. for a demonstration how a linear model leads to a steepest descent algorithm.
[^lemma-4-2]: See N&W pp. 74, in particular Lemma 4.2 for this. For this lemma to hold, we need the Jacobian $$\boldsymbol{J}$$ to have full rank. We'll later see that we can also use Dogleg in practice for all Jacobians, if we use a _regularized_ Gauss-Newton step, rather than the vanilla step defined in $$\eqref{p-gn}$$.
[^test-suite]: Were "best" is evaluated against the suite of test problems that I use. This is the famous MGH test suite described by More, Garbow, and Hilstrom in ["Testing Unconstrained Optimization Software"](https://doithat step additionally..org/10.1145/355934.355936).
[^ceres-static-scaling]: See [`trust_region_minimizer.cc:265`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/trust_region_minimizer.cc#L265) and following lines in the Ceres Solver source code. From the comments in the Ceres source code we can piece together that the scaling is meant to act roughly as $$\text{diag}(\boldsymbol{H})^{-1}$$, where $$\boldsymbol{H} \approx \boldsymbol{J}^T \boldsymbol{J}$$ is the Hessian of $$f$$. The addition of $$1$$ is there to counteract division by small numbers. It's important to note that Ceres actually defines the scaling matrix as the inverse of the matrix that I gave, but they apply the matrix itself (not its inverse) to the Jacobian from the right hand side. To make their matrix consistent with my notation (where always the inverse of a scaling matrix is applied to the Jacobian from the right), I have to invert the definition. That means the scaling is exactly the same both in this document and in Ceres, I've just chosen notational consistency.
[^ceres-dynamic-scaling]: See [`dogleg_strategy.cc:117`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/dogleg_strategy.cc#L117) and following, as well as [`trust_region_strategy.h:71`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/trust_region_strategy.h#L71). But note the `sqrt` operation in the actual diagonal matrix, which means the actual enforced clamping range is given by the `sqrt` of the values.
[^ceres-regularization]: See [`dogleg_strategy.cc:517`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/dogleg_strategy.cc#L517). Again, I can confirm that this measure makes the algorithm perform better on my test suite.
[^ceres-regularized-gn]: The last two formulations actually show are actually how Ceres solves the system. First the matrix $$\sqrt{mu} \boldsymbol{D}$$ is formed in [`dogleg_strategy.cc:561`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/dogleg_strategy.cc#L561) and passed to the solver options of the least squares solver. Then e.g. in the [`dense_qr_solver.cc:48`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/dense_qr_solver.cc#L48) we can see that the diagonal is used as described to construct the augmented system before solving this with QR decomposition.
[^cere-mu-min-max]: See [`dogleg_strategy.cc:60`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/dogleg_strategy.cc#L60).
[^ceres-mu-range]: See [`doglec_strategy.cc:544`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/dogleg_strategy.cc#L544) and [`doglec_strategy.cc:632`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/dogleg_strategy.cc#L632).
[^ceres-mu-inc]: See [`dogleg_strategy.cc:63`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/dogleg_strategy.cc#L63) and [`dogleg_strategy:533`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/dogleg_strategy.cc#L533).
[^ceres-mu-dec]: See [`doglec_strategy.cc:632`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/dogleg_strategy.cc#L632).
[^svd-regularized]: If you're interested in how to solve the regularized normal equations (in scaled space) with SVD, you can have a look at my code [here](https://github.com/geo-ant/dogleg/blob/ceb440443ad294a78bf3e3edc848bd6ac7f4bca7/dogleg-matx/src/nalgebra_impl.rs#L268).
[^minpack-feval]: The Minpack implementation I'm referring to is actually of the _Levenberg-Marquardt_ algorithm but those criteria are also applicable to Dogleg, see [`minpack.f90:1488`](https://github.com/fortran-lang/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/src/minpack.f90#L1488).
[^ceres-function-tol]: See [`trust_region_minimizer.cc:751`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/trust_region_minimizer.cc#L751).
[^ceres-min-delta]: See [`trust_region_minimizer.cc:707`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/trust_region_minimizer.cc#L707).
[^ceres-max-time]: See [`trust_region_minimizer.cc:646`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/trust_region_minimizer.cc#L646).
[^ceres-consecutive-steps]: See [`trust_region_minimizer.cc:467`](https://github.com/ceres-solver/ceres-solver/blob/0ba987acaf9e8674070f116ed624edf017d2b630/internal/ceres/trust_region_minimizer.cc#L467).
