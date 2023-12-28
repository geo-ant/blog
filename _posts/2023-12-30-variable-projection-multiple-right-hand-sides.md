---
layout: post
tags: least-squares image-processing algorithm math varpro
#categories: []
date: 2023-12-30
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Global Fitting with Variable Projection of Multiple Right Hand Sides'
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
are the same for all the datasets, while the linear coefficients are allowed to
vary between datasets. Using the formulation above, that implies that the nonlinear parameters of the fitting
problems are shared between datasets while the linear parameters are not. This
will allow us to use VarPro to its full potential and reap potentially massive
computational benefits. However, not every fitting problem will fit this bill.
We need a problem where it truly makes sense that the nonlinear parameters are
shared among datasets, while the linear coefficients are not. 

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

$$ \boldsymbol j_k = \frac{\partial\boldsymbol P^\perp_{\boldsymbol \Phi_w(\boldsymbol \alpha)}}{\partial \alpha_k} \boldsymbol y_w, \label{jk} \tag{7}$$

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
each dataset has its own vector of linear coefficients $$\boldsymbol c_s$$. We
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

where $$\boldsymbol r_{w,s} = \boldsymbol y_{w,s} - \boldsymbol \Phi_w(\boldsymbol \alpha) \boldsymbol c_s$$.
Here, $$\boldsymbol \alpha$$ and thus $$\boldsymbol \Phi_w(\alpha)$$ is the same
for each residual vector. Our minimization problem is now to minimize $$\sum_s \lVert r_{w,s} \rVert_2^2$$,
which we can write in matrix form like so: 

$$\begin{eqnarray}
&\min_{\boldsymbol \alpha, \boldsymbol C}& \rho_{WLS}(\boldsymbol \alpha, \boldsymbol C) \label{min-rho-mrhs} \tag{11} \\
\rho_{WLS} &:=& \lVert R(\boldsymbol \alpha, \boldsymbol C) \rVert_F^2 \label{redef-rho} \tag{12} \\
\boldsymbol R_w &:=& \boldsymbol Y_w - \boldsymbol \Phi_w \boldsymbol C \label{def-residual-matrix} \tag{13}, \\
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
&\min_{\boldsymbol \alpha}& \boldsymbol \rho_{WLS}(\boldsymbol \alpha) \label{min-rho-mrhs-varpro} \tag{14} \\
\boldsymbol \rho_{WLS} (\boldsymbol \alpha) &=& \lVert R (\boldsymbol \alpha) \rVert_F^2\\
\boldsymbol R &=& \boldsymbol P^\perp_{\boldsymbol \Phi_w(\boldsymbol \alpha)} \boldsymbol Y_w \\
\end{eqnarray}$$


# References

**(Warren2013)** Warren SC, *et al.* (2013) "Rapid Global Fitting of Large Fluorescence Lifetime Imaging Microscopy Datasets," PLOS ONE **8(8): e70687**. ([link](https://doi.org/10.1371/journal.pone.0070687))

**(Baerligea2023)** Bärligea, A. *et al.* (2023) "A Generalized Variable Projection Algorithm for Least Squares Problems in Atmospheric Remote Sensing," *Mathematics* **2023, 11, 2839** ([link](https://doi.org/10.3390/math11132839))

# Endnotes
[^baerligea-extension]: They extend the method for datasets where the members of a dataset may have different sizes. This is out of scope for this here article because we have to sacrifice computational savings for this extension. However, it's definitely worth checking out their paper. 
