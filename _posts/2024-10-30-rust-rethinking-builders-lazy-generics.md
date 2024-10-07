---
layout: post
tags: rust metaprogramming generics design-patterns
#categories: []
date: 2024-10-30
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Rethinking Builders... with Lazy Generics Support'
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
the boilerplate of generating the builders ourselves. If you are already familiar
with the builder pattern and at least one crate that allows you to automatically
derive a compile-time verified builder for structs, you might as well skip this section.

Here's a `#[non-exhaustive]` list of notable examples of the aforementioned
kind of crates and their taglines on crates.io:

* [`typed_builder`](https://crates.io/crates/typed-builder) (ver `0.20.0`) "Compile-time type-checked builder derive"
* [`bon`](https://crates.io/crates/bon) (ver `2.3.0`) "Generate builders for everything!"
* [`buildstructor`](https://crates.io/crates/buildstructor) (ver `0.5.4`) "[...] derive a builder from a constructor function."
* [`const_typed_builder`](https://crates.io/crates/const_typed_builder) (ver. `0.3.0`) "Compile-time type-checked builder derive using const generics"

Note, that I gave the current crate versions, at the time of writing this article,
in brackets. So, when I reference those crates in this article, it'll be based on those
versions. All of those crates are great, with `bon` and `typed_builder` being my personal
favorites and also the most widely used. All crates are compile-time validated builders,
so they will give errors _at compile time_ when you forget to set a mandatory field[^runtime-builders].

The core functionality in all of those crates lies in their ability to generate
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
    // ⭐ this is a feature, not a bug
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

Let's first look at piece of code that does not compile using any of the builder
crates mentioned above. Afterwards we'll discuss what that code might be useful
for. Say we have a runtime boolean condition `cond`:

```rust
// (1)
let common = Foo::builder().first(1.337f32);
if cond {
    // (2)
    let foo = common.second(1usize).build();
    // use foo of type Foo<f32,usize>
    // ...
} else {
    // (3)
    // ⚡ this does not compile
    let foo = common.second(&"hi").build();
    // use foo of type Foo<f32,&str>
    // ...
}
```

The reason this does not work, and we'll go into much more detail later in this
article, is that the `Foo::builder()` function returns a builder
`FooBuilder<S,T,Internal>` that has the same `S` and `T` generic parameters as the generic
type `Foo<S,T>` and then some additional internal parameters[^state-params]. At 
&#9312; the type `S` gets deduced to `f32`, which is what we want. However, 
at &#9313; the type `T` of the builder `common` gets deduced to `usize`. That
makes the instance `common` of type `FooBuilder<f32,usize,...>`,
which means it can only produce instances of `Foo<f32,usize>` and that makes
it a compilation error to pass a `&str` in &#9314;. There are many advantages
that come with this strong type deduction behavior and truth be told, I think
it's the correct default to have. But wouldn't it also be cool if the code above
had just worked? In a way, I want to avoid this eager evaluation of generics
that is the root of my problem and make the evaluation more *lazy*. Just because
I want to pass a `usize` to `second(...)` in &#9313;, doesn't mean I want to be
forced to pass the same type in &#9314;. This is what I mean with *lazy generics*. 

## So What?

If the prospect of learning how builder crates work behind the scenes and doing some
cool metaprogramming in the process doesn't already excite you, let me provide
some rationale for why the thing above could indeed be cool. Feel free to skip ahead.
I'll concede right away that this is a pretty niche use case and that there are other, saner
ways of achieving a very similar effect.

At work I have a function with a rather
nasty signature that takes a lot of parameters, concrete types and generic ones.
A bit simplified it looks like this: 

```rust
fn calculate<M,R>(data: &[f32], 
             param: f32, 
             mapping: M, 
             reduction: R) -> f32 
    where M: Mapping,
          R: Reduction 
{...}
```

This is simplified a lot, but it captures the spirit. The non-generic parameters
are the actual data and another parameter for the subsequent calculations. The
generic parameters are algorithms that change the actual logic that gets executed inside
the function. What I wanted to do was to use `bon`, which allows to construct builders
for functions. This works by transforming the functions to structs with a `.call()` method behind
the scenes. The `.call()` method is like the final `.build()` call in the builder
pattern, only that it calls the function with the final parameters instead of
returning a struct instance. Brilliant. What I'd like to work is this[^not-bon]:

```rust
let calc = CalculationBuilder::new()
            .data(my_data)
            .param(my_param)
            .mapping(my_mapping);

let result = if fiddle { 
                // my_fiddling: FiddleReduction
                calc.reduction(my_fiddling).call()
             } else {
                // my_frobnicate: FrobnicationReduction
                calc.reduction(my_frobnicate).call();
             };
```

I have run-time conditions that require the function to be called with the same
`data`, `param`, and `mapping` arguments, but with a `reduction` of different types.
If I try that, I'll run into the same problem as above, because the builder enforces
the generics eagerly.

# Goal Statement: Lazy Generics



# Limitations

* !!! const generics: as of now, they are not flexible like generic parameters. We can't stick them in an ever expanding tuple, so we would have to define as part of the generics in the builder. So there would not be lazy construction for them, but we might be able to still infer them...
* !!! "Free" generic parameters where only phantom data is used must be specified.
* !!! "Free" generic parameters which are only used in trait bounds or through their associated types `struct Foo<T:MyTrait> { f: T::Assoc}` must be defined as part of the generics of the builder.

# Endnotes
[^runtime-builders]: There's also the excellent and venerable [`derive_builder`](https://crates.io/crates/derive_builder) (ver `0.20.1`), which does all validations (including forgotten fields) at run time. The problems with generics addressed in this article also apply to this crate.
[^bon-core]: The `bon` crate allows to create builders not only for structs but also e.g. for functions. However, this functionality internally transforms the function into a structure with a `.call()` method. The function arguments are made into fields of the generated structure. Then, a builder for this new struct is generated and thus it has the same limitations as the builders that are applied directly to structures.
[^builder-capabilities]: Examples including: optional fields, `Into`-conversions, default parameters and much more, depending on the crate. [Here](https://elastio.github.io/bon/guide/alternatives) is a great overview by the `bon` maintainers.
[^state-params]: The exact form of the other generic parameters varies slightly between crates, but the principle is always the same. Again, bear with me... we'll go into the details later.
[^not-bon]: This is less elegant than [how it would actually look](https://elastio.github.io/bon/guide/overview#builder-for-a-function) in `bon`. But for the sake of this is simpler to write, since this looks more like the builder pattern in the intro section.
