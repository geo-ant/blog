---
layout: post
tags: least-squares image-processing algorithm math varpro
#categories: []
date: 2023-12-15
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Variable Projection Revisited - Multiple Right Hand Sides'
# todo add correct comment id
comments_id: 
---

At last, here is a math post again in which we'll revisit
the Variable Projection algorithm. We'll explore how to fit problems
with multiple right hand sides, where the linear parameters
can vary for each right hand side, side but the nonlinear parameters
cannot. This is sometimes called global fitting LINK!!! glotaran.

# Context

More than three years ago I wrote [an article TODO link!!!]()
on the Variable Projection (VarPro) algorithm which I long planned to revise
and extend, because I am not happy with the way I ended it.
I still believe I did a good job in describing the fundamentals
and, as a matter of fact, it laid the foundation for my [varpro LINK!!!]() numerics library, which
I have continually improved all these years. However, I am now
at a point where I want to extend the library to support solving
problems with multiple right hand sides. This is where this article
comes in and has to correct some of my past ideas at the end
of my previous post. At that time I liked the idea
of using general purpose minimizers instead of using specialized
least squares minimizers (like the Levenberg-Marquardt Algorithm) as part of my VarPro implementation. I've
always wanted to enable multiple right hand sides (MRHS), so I thought
this would be a great way to lay the foundation for that, because
the math works out to be very simple. When I implemented the varpro
library, however, I went the established route and used specialized least
squares solvers rather than general purpose minimizers. Now I am at the point that I want
to enable MRHS, but I don't like my old ideas about using general purpose
minimizers anymore and want to follow established ways of implementing MRHS[^mrhs-old].

Instead of just revising it silently I decided to write a second
part in which I would retcon LINK!!! the ending and also extend the
article significantly beyond its initial scope.

# Recap: The Variable Projection Algorithm



# Endnotes
[^mrhs-old]: 
