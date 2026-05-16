---
layout: post
tags: image-processing least-squares
#categories: []
date: 2026-04-07
last_updated:
#excerpt: ''
#image:
#description:
#permalink:
title: "A Simple Image Brightness And Contrast Adjustment Techique"
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

I recently found myself squinting at two images at work and wondering if one
is actually "better" than the other. The two images were
showing the same object but (for reasons I can't go into) they had slightly
_but noticeably_ different value ranges. That made it hard for me to
understand which of the differences were due to display brightness and constrast
settings and which were part of the actual structure
of the image. Then I remembered a simple technique that I've been using on and
off since my PhD days.

# Context

So let's say we have two images $$I$$ and $$J$$, which we want to compare by
flicking between them the image processing software of our choice[^fiji].
Despite showing the same structures, maybe we have generated the two images
using slightly different processing techniques which means that both the structures
of interest present a little differently, but also the value ranges might be
shifted a little between the images. So now we want to find a simple brightness
transform that doesn't alter the fine structure of the image but 
also allows us to shift the images into the same value range so that the differences
that we do observe are caused by something interesting happening rather than
just b

First things first, obviously I'm not the first one to come up with this technique
since it's pretty simple for anyone

SOUCES: https://www.researchgate.net/publication/234800535_Automatic_relative_radiometric_normalization_using_iteratively_weighted_least_square_regression
SAUCE2: https://onlinelibrary.wiley.com/doi/10.1002/col.21889
congeal1: https://dl.acm.org/doi/10.1109/TPAMI.2006.34
congeal least squares: https://ieeexplore.ieee.org/document/4587573

# Endnotes

[^fiji]: For me, that would be [FIJI](https://github.com/fiji/fiji), but that's just because old habits die hard.
