---
layout: post
tags: update
#categories: []
date: 2023-03-02
last_updated: 
#excerpt: ''
#description:
#permalink:
title: 'Idiomatic Rust for C++ Devs: Constructors'
#
#
# Make sure this image is correct !!!
og_image: 
#
#
# Make sure comments are enabled !!!	
comments_id: 
---

When coming to Rust as a C++ developer, one of the features I missed the most
at first were constructors. This post tries to explore the many functions that
constructors take in C++ and see how they can (or can't) be mapped to different
parts of the Rust language and standard library. Although I'll use the terminology
of C++, this article is likely helpful for developers coming to Rust from other
backgrounds as well.

There are many types of constructors in C++ and as we'll see, they serve a wide
range of purposes. I'll address those purposes section by section and we'll explore
if and how we can map them to Rust.

# Initialization

One of the most obvious (and most important) purposes of constructors is to 
provide one way to initialize an instance of a type [^initialization-cpp]. 

TODO 
* mention constructors less useful with errors as values

# Copying

Rust: EXPLICITNESS

TODO
Copy constructors...
* one of the things that are potentially impossible to see from glancing a line 
in c++ code is whether a value is being copied. 

# Moving

TODO: rust has destructive move semantics, so there's no equivalent for move constructors
and they would not serve any purpose in Rust. 

# Conversion

Rust also EXPLICIT

* a fact that c++ beginners stumble over: very one parameter constructor is a 
converting constructor

## AsRef, AsMut: Not strictly part of this but helpful conversion traits nonetheless

## TryFrom: solves same problem as above: what is when a conversion fails? EXPLICITNESS!

# Endnotes
[^initialization-cpp]: It would not be C++ if there weren't potentially many ways of initialization that interact in complex ways with each other. There's even [a book](https://leanpub.com/cppinitbook) dedicated solely to this very topic.
