---
layout: post
tags: rust metaprogramming generics design-patterns
#categories: []
date: 2024-10-30
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Rethinking Builders with Lazy Generics Support'
#
#
# Make sure this image is correct !!!
og_image: 
#
#
# make sure comments are enabled
comments_id: 
math: false
---

!!!!  TODO intro  !!!
bear with me, I promise we are going to do some neat metaprogramming.

# Intro To Builders

The [builder pattern](https://rust-unofficial.github.io/patterns/patterns/creational/builder.html)
in Rust is so popular that there are a lot of crates that allow us to avoid
the boilerplate of generating the builders ourselves. Here's a `#[non-exhaustive]`
list of notable examples and their taglines on crates.io:

* [`typed_builder`](https://crates.io/crates/typed-builder) (ver `0.20.0`) "Compile-time type-checked builder derive"
* [`bon`](https://crates.io/crates/bon) (ver `2.3.0`) "Generate builders for everything!"
* [`buildstructor`](https://crates.io/crates/buildstructor) (ver `0.5.4`) "[...] derive a builder from a constructor function."
* [`const_typed_builder`](https://crates.io/crates/const_typed_builder) (ver. `0.3.0`) "Compile-time type-checked builder derive using const generics"

Note that I gave the current crate versions, at the time of writing this article,
in brackets. So, when I reference those crates in this article, it'll based on those
versions. All of those crates are great, with `bon` and `typed_builder` being my personal
favorites and the most widely used. All crates are compile-time validated builders,
so they will give errors _at compile time_ when you forget to set a mandatory field[^runtime-builders].

The core functionality in all of those crates is their ability to generate
builders for structs[^bon-core]. If you've never used builders, this is best
explained with an example. 

```rust
#[derive(bon::Builder)]
pub struct Foo<S, T> {
    first: S,
    second: T,
}

fn main() {
    // foo1: Foo<usize,f32>
    let foo1 = Foo::builder()
                // build order is
                // arbitrary
                .second(2f32)
                .first(1usize)
                .build();
                
    // ⚡ but this will not compile
    // ⚡ because we have not provided
    // ⚡ all arguments
    let foo3 = Foo::builder()
                    .first(1f32)
                    //⚡ forgot second
                    .build();
}
```
This example uses `bon`, but it will work with (almost) no modifications with
all the other mentioned crates. There's much more that those crates can do
for you[^builder-capabilities], but now let's get to the interesting part,
which is what none of them can do.

# Problem Statement: Lazy Generics




# Limitations

* !!! const generics: as of now, they are not flexible like generic parameters. We can't stick them in an ever expanding tuple, so we would have to define as part of the generics in the builder. So there would not be lazy construction for them, but we might be able to still infer them...
* !!! "Free" generic parameters where only phantom data is used must be specified.
* !!! "Free" generic parameters which are only used in trait bounds or through their associated types `struct Foo<T:MyTrait> { f: T::Assoc}` must be defined as part of the generics of the builder.

# Endnotes
[^runtime-builders]: There's also the excellent and venerable [`derive_builder`](https://crates.io/crates/derive_builder) (ver `0.20.1`), which does all validations (including forgotten fields) at run time. The problems with generics addressed in this article also apply to this crate.
[^bon-core]: The `bon` crate allows to create builder not only for structs but also e.g. for functions. However, this functionality is relies on generating builder structures, which have the same limitations as the builders that are generated for structures.
[^builder-capabilities]: Examples including: optional fields, `Into`-conversions, default parameters and much more, depending on the crate. [Here](https://elastio.github.io/bon/guide/alternatives) is a great overview by the `bon` maintainers.
