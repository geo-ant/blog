---
layout: post
tags: least-squares image-processing algorithm math varpro
#categories: []
date: 2020-05-24
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Variable Projection Revisited - Multiple Right Hand Sides'
# todo add correct comment id
comments_id: 
---

After long last, here is a math post again in which we'll revisit
the Variable Projection method and see how we can extend it
to multiple right hand sides. We'll then see how to fit problems
with multiple right hand sides, where the linear parameters
of a fitting problem are allowed to change with the right hand
side but the nonlinear parameters are identical for all right
hand sides.

# Motivation

More than three years ago I wrote [an article TODO link!!!]()
on the Variable Projection (VarPro) method which I always planned to revise
and extend, because I am not happy with the way I ended it.
I still believe I did a good job in describing the theory 
and as a matter of fact, it laid the foundation for my [varpro LINK!!!]() numerics library, which
I have continually improved all these years. However, I am now
at a point where I want to implement a solver for multiple
right hand sides for my varpro library and this is where this
article has to correct some of my past ideas at the end
of my previous post. At the time I had gotten the idea in
my head that I could use general purpose minimizers, instead
of using established least squares minimizers (like the Levenberg-
Marquardt Algorithm) as part of my VarPro implementation. I've
always wanted to enable multiple right hand sides (MRHS), so I thought
this would be a great way to lay the foundation for that, because
the math works out to be very straightforward.
Eventuall, did not actually implement it like this though and decided to
go with the established route. Now I am at the point that I want
to enable MRHS, but I don't like my old ideas
about using general purpose minimizers anymore and want to follow
established ways of implementing MRHS[^mrhs-old].

Instead of just revising it silently I decided to write a second
part in which I would retcon LINK!!! the ending and also extend it
it significantly beyond its initial scope.

# Endnotes
[^mrhs-old]: 
