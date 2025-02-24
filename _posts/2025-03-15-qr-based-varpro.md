---
layout: post
tags: least-squares algorithm varpro
#categories: []
date: 2025-03-15
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Variable Projection with '
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

This article is part of a long running series on Variable Projection (VarPro)
on this blog, so I will rush through a lot of the fundamentals. VarPro is an
algorithm for nonlinear least squares fitting certain classes of model functions
to observations[^fitting]. I've written about the fundamentals of varpro
[here](/blog/2020/variable-projection-part-1-fundamentals/) and its extension
to global fitting [here](/blog/2024/variable-projection-part-2-multiple-right-hand-sides/)
--as well as [other places](/blog/tags/#varpro)-- on this blog. I also maintain
the free and open-source [`varpro`](https://crates.io/crates/varpro) library in the Rust
language.

What sparked this article is that fact that the core computations in
this library use the SVD matrix decomposition for calculation. While this makes
the algorithm very robust, it also comes with a speed penalty for problems that
don't actually require this degree of robustness. That's why I want to write down
how to use the QR-decomposition for those calculations, which is actually the
approach used in many other implementations.

# Endnotes

[^fitting]: VarPro isn't strictly for function fitting only, since it's a way of rewriting _separable_ nonlinear least squares minimization problems. It's just widely employed for model fitting, which is also what I am using it for.
