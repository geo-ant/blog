---
layout: post
tags: least-squares image-processing algorithm math varpro
#categories: []
date: 2023-12-30
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Global Fitting of Multiple Right Hand Sides with Variable Projection'
# todo add correct comment id
comments_id: 
math: true
---

About three years ago, I announced in my [previous article](/blog/2020/variable-projection-part-1-fundamentals/)
on variable projection, that I would write a follow up about VarPro with
multiple right hand sides. This is that article. Global fitting with multiple
right hand sides is an application where VarPro really shines because it offers
significant computational savings. Let's dive right in.

# Motivation or: What is Global Fitting?

Global fitting is a term I came across in fluorescence lifetime literature
back in the day when I was working in the field (cf. e.g. Warren2013). I am not
sure whether it is a widely used term, but the professional data analysis software
OriginLab&reg; Origin&reg; also seems to use it and [their definition](https://www.originlab.com/doc/Tutorials/Fitting-Global)
is quite instructive:

> The term "global fitting" generally refers to simultaneous curve fitting operations
> performed on multiple datasets. Because datasets remain distinct, they may or
> may not "share" parameter values during the fit process. When a parameter is shared
> a single parameter value is calculated for all datasets. When a parameter is
> not shared, a separate parameter value is calculated for each dataset. 

For this article we are concerned with global fitting of a vector valued function $$\boldsymbol f \in \mathbb{R}^m$$
to $$S$$ vector valued datasets $$\boldsymbol y_s \in \mathbb{R}^m$$, $$s = 1,\dots,S$$.
For this article, we are concerned only with fittin a so called _separable_ model
function $$\boldsymbol f$$, which can be written as the linear combination of $$n$$
nonlinear functions. Now for our problem, we will assume that the nonlinear parameters
are the same for all the members of the datasets, while the linear coefficients are allowed to
vary between members. Using the formulation above, that implies that the nonlinear parameters of the fitting
problems are shared between members of the dataset while the linear parameters are not. This
will allow us to use VarPro to its full potential and reap potentially massive
computational benefits. However, not every fitting problem will fit this bill.
We need a problem where it truly makes sense that the nonlinear parameters are
shared among members of the datasets, while the linear coefficients are not. 

One example of a problem that satisfies the condition above is Fluorescence Lifetime 
Imaging ([FLIM](https://en.wikipedia.org/wiki/Fluorescence-lifetime_imaging_microscopy)): 
it requires us to fit a number of lifetimes (the nonlinear parameters) from a 
multiexponential decay, with varying amplitudes of the individual exponential  
terms (the linear coefficients). It is a reasonable approximation that only a 
handful of distinct lifetimes are present in any one particular sample (corresponding 
to different fluorophores), but that the linear coefficients (corresponding to 
fluorophore concentration) might vary spatially across a sample (Warren2013). 

# VarPro: A Quick Recap
Since this article is a follow up of my [previous article](/blog/2020/variable-projection-part-1-fundamentals/),
so I assume that you, kind reader, are familiar with it. I'll use the same notation
as before so that its easy to go back and forth between the articles and
I'll keep repetition to a minimum.

In the last article we were concerned with least squares fitting a vector valued
separable model function $$\boldsymbol{f}$$, written as a linear combination
of nonlinear basis functions:
 
$$
\boldsymbol{f}(\boldsymbol{\alpha},\boldsymbol{c}) = \boldsymbol{\Phi}(\boldsymbol\alpha)\boldsymbol{c} \in \mathbb{R}^m \label{def-f} \tag{0}
$$

to a vector of observations $$\boldsymbol{y} \in \mathbb{R}^m$$. Here $$\boldsymbol \alpha$$
are the nonlinear parameters of the model function, while $$\boldsymbol c$$ are the linear
coefficients. Specifically we were concerned with finding $$\boldsymbol{\alpha} \in \mathbb{R}^q$$
and $$\boldsymbol c \in \mathbb{R}^n$$ such that the weighted sum of 
squared residuals $$\rho_{WLS}$$ is minimized

$$\begin{eqnarray}
&\min_{\boldsymbol \alpha, \boldsymbol c}& \rho_{WLS}(\boldsymbol \alpha, \boldsymbol c) \label{min-rho-single} \tag{1} \\
\rho_{WLS}(\boldsymbol \alpha, \boldsymbol c) &:=& \lVert \boldsymbol{r_w}(\boldsymbol \alpha, \boldsymbol c) \rVert^2_2 \label{def-rwls} \tag{2}\\
\boldsymbol r_w(\boldsymbol \alpha, \boldsymbol c) &:=& \boldsymbol W (\boldsymbol y - \boldsymbol{f}(\boldsymbol \alpha, \boldsymbol c)) \\
&=& \boldsymbol y_w - \boldsymbol \Phi_w(\boldsymbol \alpha) \boldsymbol c \label{def-rw} \tag{3} \\
\boldsymbol \Phi_w &:=& \boldsymbol W \boldsymbol \Phi \label{def-phiw} \tag{4} \\
\boldsymbol y_w &:=& \boldsymbol W \boldsymbol y \label{def-yw} \tag{5},
\end{eqnarray}$$

where $$\boldsymbol W \in \mathbb{R}^{m\times m}$$ is a weighting matrix. 
We learned that the magic of VarPro is to rewrite the minimization
problem from a minimization over $$\boldsymbol \alpha$$ _and_ $$\boldsymbol c$$
to a minimization problem over the nonlinear parameters $$\boldsymbol \alpha$$ _only_
by rewriting the vector of residuals as

$$ \boldsymbol r_w = \boldsymbol r_w (\boldsymbol \alpha) = \boldsymbol P^\perp_{\boldsymbol \Phi_w(\boldsymbol \alpha)} \boldsymbol y_w. \label{rw-P-y} \tag{6}$$

The [previous article](/blog/2020/variable-projection-part-1-fundamentals/) goes
into detail on how the _projection matrix_ $$\boldsymbol P^\perp_{\boldsymbol \Phi_w(\boldsymbol \alpha)}$$
is calculated. To minimize the squared sum of the residuals, we feed
$$\boldsymbol r_w (\boldsymbol \alpha)$$ into a least squares solver of our choice.
It is often favorable to provide the Jacobian $$\boldsymbol J(\boldsymbol \alpha)$$
matrix of the residuals as well, and it turns out we can calculate the $$k$$-th column
$$\boldsymbol j_k$$ of the Jacobian as

$$ \boldsymbol j_k = \frac{\partial \boldsymbol r_w}{\partial \alpha_k} = \frac{\partial\boldsymbol P^\perp_{\boldsymbol \Phi_w(\boldsymbol \alpha)}}{\partial \alpha_k} \boldsymbol y_w, \label{jk} \tag{7}$$

where the expression for the derivative of the projection matrix is given in the
previous article. Now we have all the ingredients together to tackle the global
fitting problem.

# Global Fitting with VarPro

In this section I'll follow the excellent presentation of Bärligea and Hochstaffl
(Baerligea2023) [^baerligea-extension]. In the initial motivation I stated this
article is concerned with fitting separable models to a dataset where the nonlinear
parameters are shared across the whole dataset, while the linear coefficients
are allowed to vary for each member of the set. Let's formalize this now and group
the data vectors $$\boldsymbol y_s$$ for $$s = 1,\dots,S$$ into a matrix:

$$\boldsymbol Y 
= \left(\begin{matrix}
\vert & & \vert \\
\boldsymbol y_1, & \dots, & \boldsymbol y_S \\
\vert & & \vert \\
\end{matrix}\right)
\in \mathbb{R}^{m \times S}. \label{def-Y} \tag{8}
$$

We allowed the linear coefficients to vary across the data set, so 
each member of the dataset has its own vector of linear coefficients $$\boldsymbol c_s$$. We
can also group those into a matrix

$$\boldsymbol C
= \left(\begin{matrix}
\vert & & \vert \\
\boldsymbol c_1, & \dots, & \boldsymbol c_S \\
\vert & & \vert \\
\end{matrix}\right)
\in \mathbb{R}^{n \times S}.\label{def-C} \tag{9}
$$

Finally, we can also group the weighted residual vectors for each member
of a dataset into a matrix:

$$\boldsymbol R_w
= \left(\begin{matrix}
\vert & & \vert \\
\boldsymbol r_{w,1}, & \dots, & \boldsymbol r_{w,S} \\
\vert & & \vert \\
\end{matrix}\right)
\in \mathbb{R}^{m \times S}, \label{def-Rmatrix} \tag{10}
$$

where $$\boldsymbol r_{w,s} = \boldsymbol y_{w,s} - \boldsymbol \Phi_w(\boldsymbol \alpha) \boldsymbol c_s$$,
where 

$$\boldsymbol y_{w,s} = \boldsymbol W \boldsymbol y_s \tag{11} \label{weighted-data}$$ 

are the weighted data sets. Note that the same weights are applied to each membre of the dataset.
Note further, that $$\boldsymbol \alpha$$ and thus $$\boldsymbol \Phi_w(\alpha)$$ are the same
for each residual vector. Our minimization problem is now to minimize $$\sum_s \lVert r_{w,s} \rVert_2^2$$,
which we can write in matrix form like so: 

$$\begin{eqnarray}
&\min_{\boldsymbol \alpha, \boldsymbol C}& \rho_{WLS}(\boldsymbol \alpha, \boldsymbol C) \label{min-rho-mrhs} \tag{12} \\
\rho_{WLS}(\boldsymbol \alpha, \boldsymbol C) &:=& \lVert \boldsymbol R_w(\boldsymbol \alpha, \boldsymbol C) \rVert_F^2 \label{redef-rho} \tag{13} \\
\boldsymbol R_w(\boldsymbol \alpha, \boldsymbol C) &:=& \boldsymbol Y_w - \boldsymbol \Phi_w \boldsymbol C \label{def-residual-matrix} \tag{14}, \\
\end{eqnarray}$$

where $$\boldsymbol Y_w = \boldsymbol W \boldsymbol Y$$ and $$\lVert . \rVert_F$$
is the [Frobenius Norm](https://mathworld.wolfram.com/FrobeniusNorm.html), i.e.
the sum of absolute squares of the matrix elements. I have reused the symbol
$$\rho_{WLS}$$ for the sum of the squared residuals, since this contains eq.
$$\eqref{def-rwls}$$ as a special case for a dataset with only one element ($$S = 1$$).

Using the ideas VarPro as presented in the presivous article, we can rewrite 
minimization problem $$\eqref{min-rho-mrhs}$$ into a minimization 
over $$\boldsymbol \alpha$$ only:

$$\begin{eqnarray}
&\min_{\boldsymbol \alpha}& \boldsymbol \rho_{WLS}(\boldsymbol \alpha) \label{min-rho-mrhs-varpro} \tag{15} \\
\boldsymbol \rho_{WLS} (\boldsymbol \alpha) &=& \lVert \boldsymbol R_w (\boldsymbol \alpha) \rVert_F^2 \label{rho-varpro} \tag{16} \\
\boldsymbol R_w(\boldsymbol \alpha) &=& \boldsymbol P^\perp_{\boldsymbol \Phi_w(\boldsymbol \alpha)} \boldsymbol Y_w \label{rw-varpro} \tag{17} \\
\end{eqnarray}$$

The matrix equations $$\eqref{rho-varpro},\eqref{rw-varpro}$$ are generalizations
of the vector identities $$\eqref{def-rwls}, \eqref{def-rw}$$. But there's
a problem here, that prevents us from just plugging these results into off-the-shelf
nonlinear least squares -such as Levenberg-Marquardt- minimizers like we did last time.
The problem is that those implementations usually require us to give the 
residual as one single vector. Additionally, we typically need to specify the
Jacobian matrix of the residual vector.

Luckily, all is not lost and we are not forced to resort to inefficient
approaches[^naive-approach] to shoehorn our nice matrix equations into vector format.
The residual $$\rho_{WLS}$$ in eq. $$\eqref{rho-varpro}$$ is just the squared
sum of the elements of the matrix $$\boldsymbol R_w$$. It's obvious that
$$\lVert \boldsymbol R_w (\boldsymbol \alpha) \rVert_F^2$$ is the same as the 
L2-norm $$\lVert \boldsymbol z_w (\boldsymbol \alpha)\rVert_2^2$$ of a vector
$$\boldsymbol z_w (\boldsymbol \alpha)$$ defined as:

$$
\boldsymbol z_w(\boldsymbol \alpha) := \text{vec}\; \boldsymbol R (\boldsymbol \alpha) = 
\left(
\begin{matrix}
\boldsymbol r_{w,1} \\
\vdots \\
\boldsymbol r_{w,S} \\
\end{matrix}
\right) =
\left(
\begin{matrix}
\boldsymbol P^\perp_{\boldsymbol \Phi_w (\boldsymbol \alpha)} \boldsymbol y_{w,1}\\
\vdots \\
\boldsymbol P^\perp_{\boldsymbol \Phi_w (\boldsymbol \alpha)} \boldsymbol y_{w,S}\\
\end{matrix}
\right), \label{z-vec} \tag{18}
$$

The mathematical operation $$\text{vec}$$ is called 
[vectorization](https://en.wikipedia.org/wiki/Vectorization_(mathematics))[^caveat-vectorization]
and turns a matrix into a vector by stacking the matrix columns on top of each
other. Now we have a vector that we can pass into our nonlinear minimization
step. We can use eq. $$\eqref{rw-varpro}$$ to calculate $$\boldsymbol z_w$$ and
then turn the resulting matrix into a vector by stacking the columns. Ideally,
this is basically a free operation in our linear algebra backend.

The final piece of the puzzle is an expression for the Jacobian of $$\boldsymbol z_w(\boldsymbol \alpha)$$,
which I'll denote $$\boldsymbol J \{\boldsymbol z_w\}(\boldsymbol \alpha)$$.
It's $$k-th$$ column is, by definition, just

$$\boldsymbol j_k^{(z)} = \frac{\partial z_w}{\partial \alpha_k},$$

which, using the same insights as above, we can write it as

$$\boldsymbol j_k^{(z)} = 
\left(
\begin{matrix}
\frac{\partial \boldsymbol r_{w,1} }{\partial \alpha_k} \\
\vdots \\
\frac{\partial \boldsymbol r_{w,S} }{\partial \alpha_k} \\
\end{matrix}
\right) =
\left(
\begin{matrix}
\frac{\partial \boldsymbol P^\perp_{\boldsymbol \Phi_w (\boldsymbol \alpha)}}{\partial \alpha_k} \boldsymbol y_{w,1}\\
\vdots \\
\frac{\partial \boldsymbol P^\perp_{\boldsymbol \Phi_w (\boldsymbol \alpha)}}{\partial \alpha_k} \boldsymbol y_{w,S}\\
\end{matrix}
\right) = \text{vec} 
\left(
\frac{\partial \boldsymbol P^\perp_{\boldsymbol \Phi_w (\boldsymbol \alpha)}}{\partial \alpha_k}
\boldsymbol Y_w
\right).
\label{jkz} \tag{19}
$$

The previous article explains how to calculate the matrix
$$\frac{\partial \boldsymbol P^\perp_{\boldsymbol \Phi_w (\boldsymbol \alpha)}}{\partial \alpha_k}$$.
Again, we can use the matrix form to efficiently calculate the result and then
transform the matrix into a column vector. If we compare the equations for the
single right hand side $$\eqref{rw-P-y}, \eqref{jk}$$ with the equations for multiple
right hand sides $$\eqref{rw-varpro}, \eqref{jkz}$$, we can see that the matrix equations
are just pretty straightforward generalizations of the original vector identities.

# Advantages and Limitations

The presented approach to solving multiple right hand sides with variable
projection has many advantages. VarPro eliminates the linear parameters from
the nonlinear minimization process, which -together with the fact that the nonlinear
parameters are shared across the dataset- means that instead of $$S\cdot n + q$$ parameters,
the nonlinear solver only has to solve for $$q$$ parameters. This is a
substantial reduction in parameters even for moderately sized datasets. Furthermore,
the matrix $$\boldsymbol P^\perp_{\boldsymbol \Phi_w}$$ and it's derivative only needs
to be calculated once for the whole dataset. This will also massively speed up
the fitting process.

However, this comes at a price: the whole calculation that I presented here depends on
the fact that the same weights are applied to all members of the dataset, see eq. $$\eqref{weighted-data}$$.
This might not be as bad of a limitation as it sounds at first. Warrent _et al._
show that [it's pretty simple](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0070687#s2)
to come up with decent global weights even for Poisson distributed data (Warren2013).

# Further Extensions

I'll conclude this article here, since it is the simplest and most efficient
application of VarPro to problems with multiple right hand sides. It's main
limitation is that the model functions and the weights must be the same for
each member of the dataset, i.e. they may not vary with the member index $$s$$ of the dataset. However,
it is straightforward to extend the method presented here to allow a dependency
on $$s$$, cf. eg. (Baerligea2023). The problem then is that we will need to 
calculate the matrix $$\boldsymbol \Phi_w^{(s)}$$, and consequently the projection
matrix and it's derivative, for each member of the dataset. This will cost us
dearly[^svd-product] but can still beat a purely nonlinear minimization without VarPro (Baerligea2023).

# References

**(Warren2013)** Warren SC, *et al.* (2013) "Rapid Global Fitting of Large Fluorescence Lifetime Imaging Microscopy Datasets," PLOS ONE **8(8): e70687**. ([link](https://doi.org/10.1371/journal.pone.0070687))

**(Baerligea2023)** Bärligea, A. *et al.* (2023) "A Generalized Variable Projection Algorithm for Least Squares Problems in Atmospheric Remote Sensing," *Mathematics* **2023, 11, 2839** ([link](https://doi.org/10.3390/math11132839))

# Endnotes
[^baerligea-extension]: They extend the method for datasets where the members of a dataset may have different numbers of elements. This is out of scope for this here article because we have to sacrifice computational savings for this extension. However, it's definitely worth checking out their paper. 
[^naive-approach]: If you're interested, check out the section titled _naive approach_ in the Bärligea paper.
[^caveat-vectorization]: Not to be confused with the concept of _vectorization_ in programming.
[^svd-product]: _Maybe_ [this](https://math.stackexchange.com/questions/67231/singular-value-decomposition-of-product-of-matrices) could help for the case where only the weights vary with $$s$$. But I'm not so sure...
