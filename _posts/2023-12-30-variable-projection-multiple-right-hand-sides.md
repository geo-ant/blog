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

# Variable Projection

This article is an extension of my [previous article](/blog/2020/variable-projection-part-1-fundamentals/),
so I assume that the reader is familiar with it. I'll use the same notation
as before so that its easy to go back and forth between the articles and
I'll keep repetition to a minimum.

# Global Fitting for Multiple Right Hand Sides
In the last article we were concerned with least squares fitting a vector valued
separable model function $$\boldsymbol{f}$$, written as

$$
\boldsymbol{f}(\boldsymbol{\alpha},\boldsymbol{c}) = \boldsymbol{\Phi}(\boldsymbol\alpha)\boldsymbol{c} \in \mathbb{R}^m
$$

to a vector of observations $$\boldsymbol{y} \in \mathbb{R}^m$$. Specifically
we were concerned with finding $$\boldsymbol{\alpha}$$ and $$\boldsymbol c$$
such that the weighted sum of squared residuals $$R_{WLS}$$ is minimized

$$\begin{eqnarray}
R_{WLS} &=& \lVert \boldsymbol{r_w} \rVert^2_2 \\
\boldsymbol{r_w} &=& \boldsymbol{y_w} - \boldsymbol{f}(\boldsymbol \alpha, \boldsymbol c)$$
\end{eqnarray}$$




