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
dogleg solver from scratch. You probably don't want to do that, but if you
did, then here's everything you'd need to know about it...

# References

Obviously _none_ of this is original and the best references I have on the
topic are [Nocedal&Wright](https://link.springer.com/book/10.1007/978-0-387-40065-5)
"Numerical Optimization", Madsen _et al._, and 
