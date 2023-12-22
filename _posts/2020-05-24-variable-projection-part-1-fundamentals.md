---
layout: post
tags: least-squares image-processing algorithm math varpro
#categories: []
date: 2020-05-24
last_updated: 2023-12-22
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'The Variable Projection Method - Nonlinear Least Squares Fitting with VarPro (Update 12/2023)'
#
#
# Make sure this image is correct !!!
og_image: vapro-introduction.png
#
#
# make suren comments are enabled
comments_id: 11
math: true
---

The Variable Projection method is a lesser known algorithm in the domain of 
nonlinear least squares fitting. It is interesting because it makes 
clever use of linear algebra to potentially speed up fitting certain classes
of functions to data. I'll introduce the method
such a way that it will enable you to implement your own varpro library in your
favorite programming language. Only a basic understanding of linear algebra and calculus is required.

**UPDATE 12/2023:** This article has undergone a pretty major rework. I have
restructured it to be a more self contained introduction into how to implement
variable projection using off-the-shelf nonlinear least squares solvers. I have
also relegated a few more non-standard ideas to the appendix.

# Before We Dive In

Variable Projection was introduced by Gene Golub and Victor Pereyra[^golub_pereyra2002]
in 1973 in their seminal (Golub 1973) paper. 
I based much of the content of this article on the publication of Dianne O'Leary 
and Bert Rust (O'Leary 2007). They do an excellent job of breaking the method 
down in terms of familiar linear algebra. Furthermore, they give helpful practical 
tips on the implementation. However, there are typos in some crucial 
formulae in their publication, which I have hopefully corrected. I will, for 
the most part, use the notation of O'Leary and Rust so that it is easy to go 
back and forth[^errors_notation]. Let's dive in.

# The Idea of VarPro

[Nonlinear Least Squares Fitting](https://en.wikipedia.org/wiki/Non-linear_least_squares) 
is the process of fitting a model function to data by minimizing the sum of the squared 
residuals. It's called *nonlinear* least squares as opposed to *linear* least 
squares because the function in question can be nonlinear in the fitting parameters. 
If the function was purely linear in the fitting parameters, we could take advantage 
of the fact that linear least squares problems can be [very efficiently solved](https://en.wikipedia.org/wiki/Linear_least_squares). 

VarPro shines when fitting a model function that is comprised of both linear
and nonlinear parameters or rather, to be more precise, if the model is _separable_.
Separable models are linear combinations of nonlinear functions.
The fundamental idea of VarPro is to separate the linear parameters from the 
nonlinear parameters during the fitting process. In doing so we can take advantage 
of efficient solutions for the linear parameters and reduce the fitting problem 
to a purely nonlinear least squares minimization. We still have to solve this 
reduced problem using a nonlinear minimization algorithm of our choice (e.g. 
[Levenberg-Marquardt](https://en.wikipedia.org/wiki/Levenberg%E2%80%93Marquardt_algorithm)).

That means VarPro is *not* a full-featured nonlinear least squares minimization algorithm in 
and of itself, but a clever way of rewriting the problem before tackling it numerically.
We will see how to compose Variable Projection with off-the-shelf nonlinear
least squares solvers. Let's now translate the principle above into formulae.

# The Model Function

VarPro is concerned with fitting model functions $$f$$ that can be written 
as a *linear combination* of $$n$$ functions that are *nonlinear*[^nonlinear_base] 
in their parameters:

$$f(\boldsymbol{\alpha},\boldsymbol{c},t) = \sum_{j=1}^{n} c_j\phi_j(\boldsymbol{\alpha},t).$$

Note that O'Leary and Rust call this function $$\eta$$ rather than $$f$$.
I will refer to the $$\phi_j$$ as the *model base functions*[^model_base_functions]. 
Now let's group the linear parameters in the vector $$\boldsymbol{c}=(c_1,\dots,c_n)^T\in\mathbb{R}^n$$ 
and the nonlinear parameters in the vector $$\boldsymbol{\alpha}=(\alpha_1,\dots,\alpha_q)^T\in\mathcal{S}_\alpha \subseteq \mathbb{R}^q$$.
So we have $$n$$ linear parameters and $$q$$ nonlinear parameters. The independent 
variable of the model function is $$t$$. It could, for example, represent physical 
quantities such as time or space. It is important to note that when I use the 
terms *linear* or *nonlinear* it refers to the behaviour of the function $$f$$ 
with respect to the parameter vectors $$\boldsymbol{\alpha}$$ and $$\boldsymbol{c}$$, 
but not the independent variable $$t$$. It is completely irrelevant if the model 
is linear or nonlinear in $$t$$.

# Weighted Least Squares

We want to fit our model to a vector $$\boldsymbol{y}$$ of observations

$$\boldsymbol{y}=(y_1,\dots,y_m)^T \in \mathbb{R}^m,$$

where $$y_i$$ is the observation at a coordinate $$t_i$$, $$i=1,\dots,m$$. The 
total number of observations is $$m$$. Let's write the function values for $$f$$ 
at those coordinates as a vector, too:
$$\boldsymbol{f}(\boldsymbol{\alpha},\boldsymbol{c}) = (f(\boldsymbol{\alpha},\boldsymbol{c},t_1),\dots,f(\boldsymbol{\alpha},\boldsymbol{c},t_m))^T \in \mathbb{R}^m.$$
Our objective is to minimize the weighted sum of the squared residuals:

$$R_{WLS}(\boldsymbol{\alpha},\boldsymbol{c}) = \lVert{\boldsymbol{W}(\boldsymbol{y}-\boldsymbol{f}(\boldsymbol{\alpha},\boldsymbol{c}))}\rVert_2^2, \label{RWLS}\tag{1}$$

with the weight matrix $$\boldsymbol{W}$$. Our minimization problem is formally 
written as

$$\min_{\boldsymbol{c}\in \mathbb{R}^n, \boldsymbol{\alpha}\in\mathcal{S}_\alpha} R_{WLS}(\boldsymbol{\alpha},\boldsymbol{c}) \label{FullMinimization}\tag{2}.$$

Note that the nonlinear parameters can be constrained on a subset $$\mathcal{S}_\alpha$$ of $$\mathbb{R}^q$$
while the linear parameters are unconstrained[^unconstrained].

# Separating Linear from Nonlinear Parameters

The fundemental idea of VarPro is to eliminate all linear parameters 
$$\boldsymbol{c}$$ from the minimization problem, by solving the linear 
subproblem separately. Assume that for a fixed $$\boldsymbol{\alpha}$$ we have 
a coefficient vector $$\boldsymbol{\hat{c}}(\boldsymbol{\alpha})$$ which is

$$ \boldsymbol{\hat{c}}(\boldsymbol\alpha) = \arg \min_{\boldsymbol{c} \in \mathbb{R}^n} \lVert{\boldsymbol{W}(\boldsymbol{y}-\boldsymbol{f}(\boldsymbol{\alpha},\boldsymbol{c}))}\rVert_2^2 \label{LSMinimization} \tag{3},$$

for any fixed $$\boldsymbol{\alpha}$$, which just means that $$\boldsymbol{c}(\boldsymbol{\alpha})$$
solves the linear subproblem. Then, given certain assumptions[^rank-conditions], the full problem 
$$\eqref{FullMinimization}$$ is equivalent to the following reduced problem:

$$ \min_{\boldsymbol{\alpha} \in \mathcal{S}_\alpha} \lVert{\boldsymbol{W}(\boldsymbol{y}-\boldsymbol{f}(\boldsymbol{\alpha},\boldsymbol{\hat{c}}(\boldsymbol{\alpha})))}\rVert_2^2 \label{ReducedMinimization} \tag{4},$$

where, as stated above, $$\boldsymbol{\hat{c}}(\boldsymbol{\alpha})$$ solves 
minimization problem $$\eqref{LSMinimization}$$. We have reduced a minimization 
problem with respect to $$\boldsymbol{\alpha}$$ _and_ $$\boldsymbol{c}$$ to a minimization 
problem with respect to $$\boldsymbol{\alpha}$$ _only_. However, the reduced minimization 
problem requires the solution of a subproblem, which is finding $$\boldsymbol{\hat{c}}(\boldsymbol\alpha)$$. 
At first it looks like nothing is gained. Until we realize that problem $$\eqref{LSMinimization}$$ 
is a *linear* least squares problem, which can be efficiently solved using linear algebra.

The additional giant benefit of VarPro is that it gives us expressions for the derivatives 
of the function $$R_{WLS}(\boldsymbol{\alpha},\boldsymbol{\hat{c}}(\boldsymbol{\alpha}))$$, 
too[^derivatives]. $$R_{WLS}(\boldsymbol{\alpha},\boldsymbol{\hat{c}}(\boldsymbol{\alpha}))$$ 
is the target we want to minimize for the nonlinear problem $$\eqref{ReducedMinimization}$$, 
which we have to solve using our favorite numerical algorithm. But we are getting ahead
of ourselves.

# Enter the Matrix

To rewrite problem $$\eqref{LSMinimization}$$ using linear algebra we introduce 
the *model function matrix* $$\boldsymbol{\Phi}(\boldsymbol{\alpha})$$:

$$\boldsymbol{\Phi}(\boldsymbol{\alpha}) 
= \left(\begin{matrix}
\phi_1(\boldsymbol{\alpha},t_1) & \dots & \phi_n(\boldsymbol{\alpha},t_1) \\
\vdots & \ddots & \vdots \\
\phi_1(\boldsymbol{\alpha},t_m) & \dots & \phi_n(\boldsymbol{\alpha},t_m) \\
\end{matrix}\right)
= \left(\begin{matrix}
\vert & & \vert \\
\boldsymbol\phi_1(\boldsymbol{\alpha}), & \dots & ,\boldsymbol\phi_n(\boldsymbol{\alpha}) \\
\vert & & \vert  \\
\end{matrix}\right)\in \mathbb{R}^{m \times n},$$

so for the matrix elements we have $$\Phi_{ik} = \phi_k(\boldsymbol{\alpha},t_i)$$. 
For fitting problems I assume we have more observations than model base functions, 
i.e. $$m>n$$. That means that the matrix has more rows than colums, which in 
turn implies that $$\text{rank}\boldsymbol{\Phi}(\boldsymbol{\alpha})\leq n$$. 
The matrix might or might not have full rank[^rank_of_Phi]<sup>,</sup>[^full_rank_Phi]. 
This fact will be important later, when giving an expression for its pseudoinverse.

We can now write

$$\boldsymbol{f}(\boldsymbol{\alpha},\boldsymbol{c})=\boldsymbol{\Phi}(\boldsymbol{\alpha})\boldsymbol{c},$$

so the linear subproblem $$\eqref{LSMinimization}$$ becomes

$$ \boldsymbol{\hat{c}}(\boldsymbol\alpha) = \arg \min_{\boldsymbol{c} \in \mathbb{R}^n} \lVert{\boldsymbol{y_w}-\boldsymbol{\Phi_w}(\boldsymbol{\alpha})\,\boldsymbol{c}}\rVert_2^2 \label{LSMinimizationLinAlg} \tag{5},$$

where I have defined the *weighted observations* $$\boldsymbol{y_w}$$ and the 
*weighted model function matrix* $$\boldsymbol{\Phi_w}(\boldsymbol{\alpha})$$ as

$$\boldsymbol{y_w} = \boldsymbol{W}\boldsymbol{y} \,\text{ and }\, \boldsymbol{\Phi_w}(\boldsymbol{\alpha}) = \boldsymbol{W} \boldsymbol{\Phi}(\boldsymbol{\alpha}).$$

A solution to problem $$\eqref{LSMinimizationLinAlg}$$ is[^mistake_paper]<sup>,</sup>[^L2Solution]

$$\boldsymbol{\hat{c}} = \boldsymbol{\Phi_w}^\dagger(\boldsymbol{\alpha}) \boldsymbol{y_w}, \label{c_hat_solution} \tag{6}$$

using the [Moore Penrose pseudoinverse](https://en.wikipedia.org/wiki/Moore%E2%80%93Penrose_inverse)
$$\boldsymbol{\Phi_w}^\dagger(\boldsymbol{\alpha})$$ of $$\boldsymbol{\Phi_w}(\boldsymbol{\alpha})$$.
This allows us to rewrite the nonlinear problem by plugging in $$\boldsymbol{\hat{c}}$$ from above

$$ \min_{\boldsymbol{\alpha} \in \mathcal{S}_\alpha} \lVert \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}\boldsymbol{y_w} \rVert_2^2 \label{NonlinProblemMatrix} \tag{7},$$

using the matrix

$$\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}:= \boldsymbol{1}-\boldsymbol{\Phi_w}(\boldsymbol{\alpha})\boldsymbol{\Phi_w}^\dagger(\boldsymbol{\alpha}) \in \mathbb{R}^{m \times m} \label{ProjectionMatrix}\tag{8}$$

which is called the *projection onto the orthogonal complement of the range of* 
$$\boldsymbol{\Phi}_w$$. It's abbreviated to $$\boldsymbol{P}$$ in 
(O'Leary 2007), but I'll keep using the more complex symbol which is commonly used in 
other publications as well. Using this matrix  we have written the squared 
sum of residuals as

$$\begin{eqnarray}
R_{WLS}(\boldsymbol{\alpha},\boldsymbol{c}) &=& \lVert \boldsymbol{r}_w\rVert^2_2 \label{Rwls}\tag{9}\\
\boldsymbol{r}_w (\boldsymbol{\alpha})&:=&  \boldsymbol{y_w}-\boldsymbol{\Phi_w}(\boldsymbol{\alpha})\boldsymbol{\hat{c}}(\boldsymbol{\alpha}) 
= \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}\boldsymbol{y_w} \label{rw-Proj}\tag{10}, \\
\end{eqnarray}$$

where $$\boldsymbol{r}_w$$ is the _residual vector_.
When written like this, $$R_{WLS}$$ is called the *projection functional*, which
is the  the reason why the method is called  *Variable Projection* (Mullen 2009).

At this point we are almost halfway there. Our aim is to minimize the projection 
functional using a (possibly constrained) minimization algorithm. If we want to 
use high quality off-the-shelf least squared solvers, we typically need two things: first
we need to calculate the residual vector $$\boldsymbol{r}_w$$. This requires us
to solve the linear system in a numerically feasible manner to obtain $$\boldsymbol{\hat{c}}(\boldsymbol{\alpha})$$
for a given $$\boldsymbol{\alpha}$$. Secondly, we need 
to supply the [Jacobian](https://de.wikipedia.org/wiki/Jacobi-Matrix)
of $$\boldsymbol{r}_w$$ with respect to $$\boldsymbol{\alpha}$$. Solving the linear
system is typically achieved using either a [QR Decomposition](https://en.wikipedia.org/wiki/QR_decomposition#Rectangular_matrix) 
or [Singular Value Decomposition (SVD)](http://www.omgwiki.org/hpec/files/hpec-challenge/svd.html)
of $$\boldsymbol{\Phi}_w$$. These decompositions will also come in helpful when
calculating the Jacobian and we'll get back to them later.

# Analytical Derivatives

If we want to use a high quality nonlinear solver to minimize our projection functional,
we have to supply the Jacobian $$\boldsymbol{J}(\boldsymbol{\alpha})$$
of $$\boldsymbol{r}_w(\boldsymbol{\alpha})$$ with respect to $$\alpha$$. The Jacobian
Matrix of $$\boldsymbol{r}_w$$ is defined as the matrix $$\boldsymbol{J}$$ with entries
$$J_{ik} = \left(\frac{\partial \boldsymbol{r}_w}{\partial \alpha_k}\right)_i$$. It's a bit
more helpful for the following calculations to write it in a columnar format:

$$\boldsymbol{J}(\boldsymbol{\alpha}) =  (J_{ik})
= \left(\begin{matrix}
\vert & & \vert \\
\boldsymbol{j}_1, & \dots, &  \boldsymbol{j}_q \\
\vert & & \vert \\
\end{matrix}\right)
= \left(\begin{matrix}
\vert & & \vert \\
\frac{\partial}{\partial \alpha_1}\boldsymbol{r}_w, & \dots, &  \frac{\partial}{\partial \alpha_q}\boldsymbol{r}_w & \\
\vert & & \vert \\
\end{matrix}\right) \in \mathbb{R}^{m\times q}$$

The derivative $$\frac{\partial}{\partial \alpha_k} \boldsymbol{r}_w$$ is simply
the element-wise derivative of the residual vector with respect to the scalar
$$\alpha_k$$. Using eq. $$\eqref{rw-Proj}$$ we can write

$$
\boldsymbol{j}_k(\boldsymbol\alpha) = \frac{\partial \boldsymbol{r}_w}{\partial \alpha_k} (\boldsymbol{\alpha})
= \frac{\partial \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}}{\partial \alpha_k}\boldsymbol{y_w}  \label{jk-column-P}\tag{11},
$$

where the derivative with respect to the scalar $$\alpha_k$$ for the matrix and vector are
just applied element-wise. So, we need an expression for 
$$ \frac{\partial \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}}{\partial \alpha_k}$$ and
it turns out it is not that hard to calculate (see Appendix A):

$$
\frac{\partial \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}}{\partial \alpha_k}
= -\left[
\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}D_k \boldsymbol{\Phi_w}^\dagger(\boldsymbol{\alpha})
+\left(\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}D_k \boldsymbol{\Phi_w}^\dagger(\boldsymbol{\alpha})\right)^T
\right]
\label{diff-Proj}\tag{12},
$$

where $$\boldsymbol{D_k}$$ is the derivative of the weighted model function matrix with respect to $$\alpha_k$$.

$$
\boldsymbol{D_k}(\boldsymbol\alpha) 
:= \frac{\partial \boldsymbol{\Phi_w}}{\partial \alpha_k} (\boldsymbol\alpha) =
\boldsymbol{W} \frac{\partial \boldsymbol{\Phi}}{\partial \alpha_k} (\boldsymbol\alpha) \in \mathbb{R}^{m\times n},
\label{Dk-matrix}\tag{13}
$$

where the derivative, again, is performed element-wise for $$\boldsymbol{\Phi_w}$$.
Using these results, we find that we can calculate the $$k$$-th column of the Jacobian
as

$$
\boldsymbol{j}_k (\boldsymbol{\alpha})= -\left(\boldsymbol{a}_k(\boldsymbol{\alpha}) + \boldsymbol{b}_k (\boldsymbol{\alpha})\right),
\label{jk-ak-bk}\tag{14}
$$

where

$$
\boldsymbol{a_k}(\boldsymbol\alpha) = \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}\, \boldsymbol{D_k} \, \boldsymbol{\Phi_w}^\dagger \, \boldsymbol{y_w}
=  \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \, \boldsymbol{D_k} \, \boldsymbol{\hat{c}}
 \label{ak-vector}\tag{15},
$$

and 

$$
\begin{eqnarray}
\boldsymbol{b_k}(\boldsymbol\alpha) &=& \left(\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}\, \boldsymbol{D_k}\, \boldsymbol{\Phi_w}^\dagger\right)^T \boldsymbol{y_w} \\
&=& \left(\boldsymbol{\Phi_w}^\dagger\right)^T \boldsymbol{D_k}^T \, \left(\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}\right)^T \boldsymbol{y_w} \\
&=& \left(\boldsymbol{\Phi_w}^\dagger\right)^T \boldsymbol{D_k}^T \,  \boldsymbol{r_w}
\label{bk-vector}\tag{16}.
\end{eqnarray}
$$

Here we used that $$\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} = \left(\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}\right)^T$$,
cf. the Appendix A.

## The Kaufman Approximation

A widely used approximation in the context of Variable Projection is the Kaufman
approximation, which neglects the second term in eq. $$\eqref{diff-Proj}$$
and approximates it as:

$$
\frac{\partial \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}}{\partial \alpha_k}
\approx - \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}D_k \boldsymbol{\Phi_w}^\dagger(\boldsymbol{\alpha}).
\label{diff-Proj-Kaufmann}\tag{17}
$$

This approximation reduces the computational burden of calculating the Jacobian,
while still retaining good numerical accuracy (Kaufman 1975). It implies that
we can approximate the columns of the jacobian as:

$$
\boldsymbol{j}_k \approx - \boldsymbol{a_k}
= - \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \, \boldsymbol{D_k} \, \boldsymbol{\hat{c}}.
\label{jk-Kaufmann}\tag{18}
$$

This approximation is ubiquitous and seems to do very well for many applications
(O'Leary 2007, Mullen 2009, Warren 2013). O'Leary notes that using
this approximation will likely increase the number of iterations before a 
solution is obtained. If the model function is very expensive to calculate
(e.g. if it is the result of  a complex simulation), then it might be advantageous
to calculate the full Jacobian to benefit from less iterations.

## Analytical Derivatives Using Singular Value Decomposition

Further above, I mentioned that we typially use a matrix decomposition
of $$\boldsymbol{\Phi}_w$$ to solve the linear system and that we would see
those decompositions again when calculating the Jacobian. Now's that time. 

To calculate the Jacobian matrix, we need a numerically efficient decomposition 
of $$\boldsymbol{\Phi_w}$$ to calculate the pseudoinverse and the projection
matrix. This is done by either  QR Decomposition or SVD, as mentioned above. 
I will follow O'Leary in using the  SVD, although most other implementations use 
some form of QR Decomposition (O'Leary 2007, Sima 2007, Mullen 2009, Kaufman 1975, Warren 2013).

For a rectangular matrix $$\boldsymbol{\Phi_w}$$ with *full rank*, we can write 
$$\boldsymbol{\Phi_w}^\dagger=(\boldsymbol{\Phi}^T \boldsymbol{\Phi})^{-1} \boldsymbol{\Phi}^T$$, 
which is [usually a bad idea](https://eigen.tuxfamily.org/dox/group__LeastSquares.html) 
numerically. Furthermore, if $$\boldsymbol{\Phi_w}$$ does not have full rank, 
then $$(\boldsymbol{\Phi}^T \boldsymbol{\Phi})^{-1}$$ does not exist and we need 
a different expression for the pseudoinverse. This can be given in terms of the :
[*reduced* Singular Value Decomposition](https://en.wikipedia.org/wiki/Singular_value_decomposition#Reduced_SVDs) 
of $$\boldsymbol{\Phi_w}$$:

$$\boldsymbol{\Phi_w} = \boldsymbol{U}\boldsymbol\Sigma\boldsymbol{V}^T,$$

with $$\boldsymbol{U}\in \mathbb{R}^{m\times \text{rank}\boldsymbol{\Phi_w}}$$, 
$$\boldsymbol{V}\in \mathbb{R}^{\text{rank}\boldsymbol{\Phi_w} \times \text{rank}\boldsymbol{\Phi_w}}$$ 
and the diagonal matrix of nonzero eigenvalues $$\boldsymbol\Sigma$$. Note that 
the matrix $$\boldsymbol{U}$$ is not the square matrix from the *full* Singular
Value Decomposition. That means it is not unitary, i.e. $$\boldsymbol{U}\boldsymbol{U}^T$$ 
is not the identity matrix. For the matrix $$\boldsymbol{V}$$, however, we have 
$$\boldsymbol{I} = \boldsymbol{V}^T\boldsymbol{V}$$. The pseudoinverse of can 
be expressed as

$$\boldsymbol{\Phi_w}^\dagger = \boldsymbol{V}\boldsymbol\Sigma^{-1}\boldsymbol{U}^T  \label{pinv-svd}\tag{19}.$$

This implies $$\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} =\boldsymbol{I}-\boldsymbol{U}\boldsymbol{U}^T$$ 
and the expressions for the columns $$\boldsymbol{a_k}$$ and $$\boldsymbol{b_k}$$ 
can be written as

$$\begin{eqnarray}
\boldsymbol{a_k} &=& \boldsymbol{D_k}\boldsymbol{\hat{c}} - \boldsymbol{U}(\boldsymbol{U}^T(\boldsymbol{D_k}\boldsymbol{\hat{c}})) \label{ak-svd}\tag{20} \\
\boldsymbol{b_k} &=& \boldsymbol{U}(\boldsymbol{\Sigma^{-1}}(\boldsymbol{V}^T(\boldsymbol{D_k}^T\boldsymbol{r_w})) \label{bk-svd}\tag{21}.
\end{eqnarray}$$

The expressions are grouped in such a way that only matrix vector products need 
to be calculated (O'Leary 2007).

# Putting It All Together

Now we have all the ingredients to implement our own fitting library that
makes use of Variable Projection. As noted above, VarPro is an algorithm that rewrites
a separable problem into a purely nonlinear least squares problem. That problem
still has to be solved. Rather than implementing a nonlinear least squares solver
from scratch, it can make a lot of sense to use an off-the-shelf solver.

Typical nonlinear least squares solvers will request from us the residual vector
$$\boldsymbol{r_w}$$ and its Jacobian $$\boldsymbol{J}$$ at the nonlinear
parameters $$\boldsymbol{\alpha}$$. For that, we first build the model function
matrix $$\boldsymbol{\Phi_w}$$ and calculate its SVD. This allows us to solve
the linear subproblem to obtain $$\boldsymbol{\hat{c}}$$ and then calculate
the residual vector. We'll then use the singular value decomposition to
populate the columns of the Jacobian. One implementation detail is that we
might want to use a linear algebra library for the matrix calculations and 
decompositions. It might be worth considering to chose the same library that
the nonlinear solver uses as part of its API (since it will likely request
the residual as a vector and the Jacobian in matrix form). This is just to 
avoid unneccessary copying of data.

This concludes my first article on Variable Projection. In the next part of the 
series I'll explore how to fit multiple right hand sides, also termed *global analysis* 
in the time resolved microscopy literature (Mullen 2009). Feel free to 
check out my [vapro](https://crates.io/crates/varpro) Rust library, which
I have been maintaining since a couple of years and is still evolving slowly but
but steadily. It's fast, simple to use, and very well tested.

# Literature
**(Golub 1973)** Golub, G.; Pereyra, V. "The Differentiation of Pseudo-Inverses and Nonlinear Least Squares Problems Whose Variables Separate". SIAM J. Numer. Anal. **1973, 10, 413–432**. [https://doi.org/10.1137/0710036](https://doi.org/10.1137/0710036)

**(Kaufman 1975)** Kaufman, L. "A variable projection method for solving separable nonlinear least squares problems." *BIT* **15**, 49–57 (1975). [https://doi.org/10.1007/BF01932995](https://doi.org/10.1007/BF01932995)

**(O'Leary 2007)** O’Leary, D.P., Rust, B.W. "Variable projection for nonlinear least squares problems." *Comput Optim Appl* **54**, 579–593 (2013). [https://doi.org/10.1007/s10589-012-9492-9](https://doi.org/10.1007/s10589-012-9492-9). The article is behind a paywall. You can find the manuscript by O'Leary and Rust [publicly available here](https://www.cs.umd.edu/users/oleary/software/varpro.pdf). *Caution*: There are typos / errors in some important formulae in the paper and manuscript. I have (hopefully) corrected these mistakes in my post.

**(Sima 2007)** Sima, D.M., Van Huffel, S. "Separable nonlinear least squares fitting with linear bound constraints and its application in magnetic resonance spectroscopy data quantification," *J Comput Appl Math*.**203**, 264-278 (2007) [https://doi.org/10.1016/j.cam.2006.03.025](https://doi.org/10.1016/j.cam.2006.03.025).

**(Mullen 2009)** Mullen, K.M., Stokkum, I.H.M.v.: The variable projection algorithm in time-resolved spectroscopy, microscopy and mass spectrometry applications. *Numer Algor* **51**, 319–340 (2009). [https://doi.org/10.1007/s11075-008-9235-2](https://doi.org/10.1007/s11075-008-9235-2).

**(Warren 2013)** Warren, S.C *et al.* "Rapid global fitting of large fluorescence lifetime imaging microscopy datasets." *PloS one* **8,8 e70687**. 5 Aug. 2013, [doi:10.1371/journal.pone.0070687](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0070687).

**(Baerligea 2023)** Bärligea, A. *et al.* "A Generalized Variable Projection Algorithm for Least Squares Problems in Atmospheric Remote Sensing" *Mathematics* **2023, 11, 2839** [https://doi.org/10.3390/math11132839](https://doi.org/10.3390/math11132839)

# Appendix A: Calculating the Derivative of $$\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}$$

This section follows the very nice paper by Bärligea and Hochstaffl (Baerligea 2023).
To simplify notation, we will refer to $$\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}$$
as $$\boldsymbol{P}^\perp$$. Also we'll write $$\boldsymbol{\Phi_w}(\alpha)$$
as $$\boldsymbol\Phi$$ and it's Moore-Penrose pseudoinverse as $$\boldsymbol\Phi^\dagger$$.
We'll also note that $$\boldsymbol\Phi^\dagger$$ [by definition](https://en.wikipedia.org/wiki/Moore%E2%80%93Penrose_inverse#Definition)
satisfies the following equations (among other ones):

$$\begin{eqnarray}
\boldsymbol\Phi \boldsymbol\Phi^\dagger \boldsymbol\Phi &=& \boldsymbol\Phi \tag{A.1} \label{A-pseudo1} \\
(\boldsymbol\Phi  \boldsymbol\Phi^\dagger)^T &=&\boldsymbol\Phi  \boldsymbol\Phi^\dagger \tag{A.2} \label{A-pseudo2}
\end{eqnarray}$$

We now concern ourselves with the matrix $$P$$

$$\boldsymbol{P} := \boldsymbol\Phi  \boldsymbol\Phi^\dagger, \tag{A.3} \label{A-def-P}$$

which is related to $$\boldsymbol{P}^\perp$$ by

$$\boldsymbol{P}^\perp = \boldsymbol{1} - \boldsymbol{P}. \tag{A.4} \label{A-def-P-perp}$$

From the properties of the pseudoinverse we can see that:

$$\begin{eqnarray}
\boldsymbol{P}^T &=& \boldsymbol{P} \tag{A.5} \label{A-P-sym}\\
\boldsymbol{P}^2 &=& \boldsymbol{P} \tag{A.6} \label{A-P2}\\
\boldsymbol{P} \boldsymbol \Phi &=& \boldsymbol\Phi \tag{A.7} \label{A-P3}
\end{eqnarray}$$

Using the shorthand $$\partial_k$$ for the partial derivative
$$\frac{\partial}{\partial \alpha_k}$$ we can now write

$$\begin{eqnarray}
\partial_k \boldsymbol\Phi &=& \partial_k (\boldsymbol{P} \boldsymbol\Phi) \\
\Leftrightarrow \partial_k \boldsymbol\Phi &=& (\partial_k \boldsymbol{P}) \boldsymbol \Phi + \boldsymbol{P} (\partial_k \boldsymbol\Phi) \\
\Leftrightarrow (\boldsymbol{1} - \boldsymbol{P})\partial_k \boldsymbol\Phi &=& (\partial_k \boldsymbol{P}) \boldsymbol \Phi \\
\Leftrightarrow \boldsymbol{P}^\perp(\partial_k \boldsymbol\Phi) &=& (\partial_k \boldsymbol{P}) \boldsymbol \Phi \\
\Leftrightarrow \boldsymbol{P}^\perp(\partial_k \boldsymbol\Phi) \boldsymbol{\Phi}^\dagger &=& (\partial_k \boldsymbol{P}) \boldsymbol{P}. \tag{A.8} \label{A-partial-P}
\end{eqnarray}$$

In the last line we right-multiplied with $$\boldsymbol\Phi^\dagger$$ and used
$$\boldsymbol\Phi \boldsymbol\Phi^\dagger = \boldsymbol{P}$$. The right hand
side already looks like a term that would occur in $$\partial_k \boldsymbol{P}^2$$.
So let's look at that expression and use the fact that $$\boldsymbol{P}^2 = \boldsymbol{P}$$:

$$\begin{eqnarray}
\partial_k \boldsymbol{P} = \partial_k \boldsymbol{P}^2 = (\partial_k \boldsymbol{P})\boldsymbol{P}+\boldsymbol{P}(\partial_k \boldsymbol{P}) \tag{A.9} \label{A-partial-P-2}
\end{eqnarray}$$

For the final piece of the puzzle, we use eq. $$\eqref{A-P-sym}$$, which implies
that $$\partial_k \boldsymbol{P} = (\partial_k \boldsymbol{P})^T$$,
so that we can rewrite the second term in eq. $$\eqref{A-partial-P-2}$$ as

$$
\boldsymbol{P}(\partial_k \boldsymbol{P}) = \left( \boldsymbol{P}^T (\partial_k \boldsymbol{P})^T\right)^T = \left((\partial_k \boldsymbol{P})\boldsymbol{P} \right)^T. \tag{A.10}
$$

We can combine this result with eqns. $$\eqref{A-partial-P}$$ and $$\eqref{A-partial-P-2}$$ 
to obtain an expression for the partial derivative of $$\boldsymbol{P}$$. However,
we are interested in the partial derivative of $$\boldsymbol{P}^\perp$$. Luckily,
it follows from eq. $$\eqref{A-def-P-perp}$$, that 
$$\partial_k \boldsymbol{P}^\perp = -\partial_k \boldsymbol{P}$$, so that we
can write

$$\partial_k \boldsymbol{P}^\perp = - \left[ (\boldsymbol{P} (\partial_k {\Phi}) \boldsymbol{\Phi}^\dagger) + (\boldsymbol{P}(\partial_k \boldsymbol{\Phi}) \boldsymbol{\Phi}^\dagger)^T\right],$$

which, at last, is the result we set out to prove.


# Appendix B: VarPro with General Purpose Nonlinear Minimization

**UPDATE 2023** The ideas from this section featured pretty prominently in the
previous version of this article. While I don't think the ideas are wrong,
I am going back and forth on how useful they are. I thought they would
give me an elegant way of extending my varpro implementation to multiple right
hand sides. However, there are established methods to do that which still
compose well with off-the-shelf least squares solvers. So I don't feel
an urgent need to explore the ideas presented here, but I also cannot quite let
them go.

If we want to minimize the weighted residual $$R_{WLS}$$ using a general purpose minimizer, 
then it is preferrable to know its gradient with respect to $$\boldsymbol{\alpha}$$.
The weighted residual is given in eq. $$\eqref{Rwls}$$. Its gradient is:

$$\nabla R_{WLS}(\boldsymbol\alpha) = \left(\frac{\partial R_{WLS}}{\partial\alpha_1}(\boldsymbol\alpha),\dots,\frac{\partial R_{WLS}}{\partial\alpha_q}(\boldsymbol\alpha)\right)^T.$$

The $$k$$-th component is calculated using [the product rule for the dot product](https://math.stackexchange.com/questions/159284/product-rule-for-the-derivative-of-a-dot-product):

$$\begin{eqnarray}
\frac{\partial}{\partial \alpha_k} R_{WLS}(\boldsymbol\alpha) &=& \frac{\partial}{\partial \alpha_k} \lVert \boldsymbol{r}_w(\boldsymbol\alpha) \rVert^2 \\
 &=& \frac{\partial}{\partial \alpha_k} \left(\boldsymbol{r}_w(\boldsymbol\alpha) \cdot \boldsymbol{r}_w(\boldsymbol\alpha) \right) \\
 &=& 2\; \frac{\partial\boldsymbol{r}_w(\boldsymbol\alpha) }{\partial \alpha_k} \cdot \boldsymbol{r}_w(\boldsymbol\alpha) \\
 &=& 2\; \boldsymbol{j}_k (\boldsymbol\alpha) \cdot \boldsymbol{r}_w(\boldsymbol\alpha) \\
\end{eqnarray}$$

where $$\boldsymbol{j_k}$$ is the $$k$$-th 
column of the Jacobian $$\boldsymbol{J}(\boldsymbol\alpha)$$, and $$\boldsymbol{r_w}$$ 
is the weighted residual vector as defined above. We can simplify these expressions 
if we use the Kaufmann approximation for the Jacobian:

$$\begin{eqnarray}
\frac{\partial}{\partial \alpha_k} R_{WLS} &=& -2\, \boldsymbol{r_w}\cdot \boldsymbol{a_k} \\
&=& -2\,\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \boldsymbol{y_w} \cdot \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \,\boldsymbol{D_k} \boldsymbol{\hat{c}} \\
&=& -2\,\left(\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \right)^T\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \,\boldsymbol{y_w} \cdot \boldsymbol{D_k} \boldsymbol{\hat{c}} \\
&=& -2\,\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \boldsymbol{y_w} \cdot \boldsymbol{D_k} \boldsymbol{\hat{c}} \\
&=& -2\,\boldsymbol{r_w} \cdot \boldsymbol{D_k} \boldsymbol{\hat{c}}, \label{Kaufman_Approx_Gradient_RWLS} 
\end{eqnarray}$$

where we have used $$\left(\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \right)^T \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} =\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})}  \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} =\boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} $$ 
(see Appendix A) and the fact that [we can write](https://books.google.de/books?id=sMfjDwAAQBAJ&lpg=PA22&dq=scalar%20product%20X*Ay&hl=de&pg=PA22#v=onepage&q&f=false) 
$$\boldsymbol{x}\cdot \boldsymbol{A} \boldsymbol{y} = \boldsymbol{A}^T\boldsymbol{x}\cdot\boldsymbol{y}$$ 
for all vectors $$\boldsymbol{x},\boldsymbol{y} \in \mathbb{R^m}$$ and square 
matrices $$\boldsymbol{A} \in \mathbb{R}^{m\times m}$$.

It turns out that this formula is not only true under the Kaufmann approximation
but that it is exact. We can see that the second term always vanishes:

$$\begin{eqnarray}
\boldsymbol{r_w}\cdot \boldsymbol{b_k} &=& \boldsymbol{r_w}\cdot (\boldsymbol{D_k} \boldsymbol{\Phi_w}^\dagger)^T\,\boldsymbol{r_w} \\
&=& \boldsymbol{D_k}\boldsymbol{\Phi_w}^\dagger\, \boldsymbol{r_w} \cdot \boldsymbol{r_w} \\
&=& \boldsymbol{D_k} \boldsymbol{\Phi_w}^\dagger \boldsymbol{P}^\perp_{\boldsymbol{\Phi_w}(\boldsymbol{\alpha})} \boldsymbol{y_w}  \cdot \boldsymbol{r_w} \\
&=& \boldsymbol{D_k} \boldsymbol{\Phi_w}^\dagger (\boldsymbol{1}-\boldsymbol{\Phi_w}\boldsymbol{\Phi_w}^\dagger )\boldsymbol{y_w}  \cdot \boldsymbol{r_w} \\
&=& \boldsymbol{D_k} (\boldsymbol{\Phi_w}^\dagger - \boldsymbol{\Phi_w}^\dagger \boldsymbol{\Phi_w}\boldsymbol{\Phi_w}^\dagger )\boldsymbol{y_w}  \cdot \boldsymbol{r_w} \\
&=& \boldsymbol{0},
\end{eqnarray}$$

where we have used the property $$\boldsymbol{\Phi_w}^\dagger = \boldsymbol{\Phi_w}^\dagger \boldsymbol{\Phi_w}\boldsymbol{\Phi_w}^\dagger$$
of the Moore-Penrose pseudoinverse.

For a general purpose nonlinear minimizer we typically have to supply $$R_{WLS}$$
and its gradient, maybe additionally the Hessian if we feel particularly adventurous.
The gradient is very simple to calculate,since it does not 
require the projection matrix or its decomposition explicitly. I say explicitly 
because we will still need to solve the linear system to obtain $$\boldsymbol{\hat{c}}$$,
but we might use a linear algebra library that hides that complexity from us.

As an additional benefit, we can even give an analytical expression for the 
Hessian of $$R_{WLS}$$. I won't give the expression here because it's not as
simple as the ones above. I'll just note that calculating the partial derivative
$$\partial/\partial\alpha_l \boldsymbol{\hat{c}}$$ will require the partial derivatives
of the pseudoinverse. As noted [here](https://mathoverflow.net/questions/25778/analytical-formula-for-numerical-derivative-of-the-matrix-pseudo-inverse),
the formula for that is given as eq. $$(4.12)$$ in the orginal (Golub 1973)
publication. Note also that they give an expression for the gradient in eq $$(4.7)$$
of their paper, which is consistent with the expression I gave.

As mentioned in the update to this article, I don't believe these ideas are as useful as I once thought.
But who knows, maybe I'll try and explore them at some point and see how they turn out numerically.

# Endnotes

[^golub_pereyra2002]: See [here](https://pdfs.semanticscholar.org/3f20/1634276f9c1c79e421355b4915b69b4aae24.pdf) for a review paper on Variable Projection by Golub and Pereyra in 2002. In there you can also find references to their original work as well as the contributions by Linda Kaufman. There is also [a follow-up by Pereyra](http://vpereyra.com/wp-content/uploads/2019/08/Surveypaper2019.pdf) covering the time from 2002 until 2019.
[^errors_notation]: Errors are mine of course. I will also use their notation to make it easy to go back and forth from this article and their publication. This is why I am sparing you the references to their publication in the next sections. Just assume everything is taken from O'Leary and Rust unless stated otherwise.
[^nonlinear_base]: These functions could also be linear in their parameters but it makes little sense to have them be linear without good reason. One such reason could be that the parameter space is constrained, because the derivatives presented in here are only true for unconstrained linear parameters.
[^unconstrained]: This is not a principal limitation of the method. But in this post I am only reproducing the expressions for unconstrained fitting of the linear parameters. If the linear parameters were constrained, this would influence the derivatives presented later. See (Sima 2007) for more information.
[^notation_c_alpha]: In their manuscript, O'Leary and Rust refer to  $$\boldsymbol{\hat{c}}(\boldsymbol{\alpha})$$ as $$\boldsymbol{c}(\boldsymbol{\alpha})$$. I decided to add the hat to emphasize that this is the particular value that solves the linear least squares problem.
[^mistake_paper]: In the published version of the paper it is mistakenly stated that $$\boldsymbol{\hat{c}}$$ equals $$\boldsymbol{\Phi_w}(\boldsymbol{\alpha})^\dagger \boldsymbol{y}$$ instead of $$\boldsymbol{\Phi_w}(\boldsymbol{\alpha})^\dagger \boldsymbol{y_w}$$. This mistake is corrected in the online manuscript. However the mistake also occurs when the expression for the derivatives are given and is not corrected in either version. In both expressions for $$\boldsymbol{a_k}$$ and $$\boldsymbol{b_k}$$ the symbol $$\boldsymbol{y}$$ needs to be replaced by $$\boldsymbol{y_w}$$. Unless I am completely mistaken, which is always possible.
[^rank_of_Phi]: For any $$m \times n$$ matrix witn $$n<m$$ the rank is less than or equal to $$n$$. The matrix is [considered to have full rank](https://www.cds.caltech.edu/~murray/amwiki/index.php/FAQ:_What_does_it_mean_for_a_non-square_matrix_to_be_full_rank%3F) if its rank equals $$n$$.
[^full_rank_Phi]: Ideally the function matrix $$\boldsymbol{\Phi}(\boldsymbol{\alpha})$$ should have full rank, since the model is not well designed if the model base functions are linearly dependent. However, there are cases under which that could happen for particular values $$\boldsymbol{\alpha}$$. For example when fitting sums of exponential models with background terms.
[^model_base_functions]: This name might not always be accurate because the functions don't necessarily have to be linearly independent. However, for a good model they should be. See also the discussions later on the rank of $$\boldsymbol{\Phi}$$.
[^derivatives]: Under the condition that we have analytical expressions for the partial derivatives $$\partial/\partial\alpha_k \phi_j(\boldsymbol\alpha,t)$$ of the model base functions.
[^L2Solution]: The solution $$\boldsymbol{\hat{c}}$$ is not unique. The solution given here (using the pseudoinverse) has the smallest 2-Norm $$\lVert\boldsymbol{\hat{c}}\rVert_2^2$$ among all solutions that minimize the problem, see [here](https://en.wikipedia.org/wiki/Moore%E2%80%93Penrose_inverse#Linear_least-squares)
[^rank-conditions]: I've glossed over an important precondition that must hold before we can really separate the linear and nonlinear optimization as shown above. The matrix $$\boldsymbol{\Phi}(\boldsymbol{\alpha})$$ of the model base functions must have locally constant rank in a neighborhood of $$\boldsymbol{\alpha}$$. $$\boldsymbol{\Phi}$$ is the matrix introduced in the next sections.
