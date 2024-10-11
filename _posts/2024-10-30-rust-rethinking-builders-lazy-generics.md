---
layout: post
tags: rust metaprogramming generics design-patterns
#categories: []
date: 2024-10-11
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Rethinking Builders... with Lazy Generics'
#
#
# Make sure this image is correct !!!
og_image: rethinking-builders.png
#
#
# make sure comments are enabled
comments_id: 73
math: false
---

While using compile-time builder generator crates, I realized that I had run into
a niche problem that required lot more flexibility with generic structs and 
functions than I was getting. If you like, follow me down a rabbit hole 
and explore the builder pattern from a very generic-centric perspective.

# Intro To Builders

The [builder pattern](https://rust-unofficial.github.io/patterns/patterns/creational/builder.html)
in Rust is so popular that there are a lot of crates that allow us to avoid
the boilerplate of generating the builders ourselves. Probably you're already
familiar with the builder pattern and at least one crate that allows you to automatically
derive a compile-time verified builder for structs.

Here's a highly `#[non-exhaustive]` list comprising these
kind of crates and their taglines on crates.io, ordered in descending order by total
number of downloads at the time of writing:

* [`typed_builder`](https://crates.io/crates/typed-builder) (ver `0.20.0`) "Compile-time type-checked builder derive"
* [`buildstructor`](https://crates.io/crates/buildstructor) (ver `0.5.4`) "[...] derive a builder from a constructor function."
* [`bon`](https://crates.io/crates/bon) (ver `2.3.0`) "Generate builders for everything!"
* [`const_typed_builder`](https://crates.io/crates/const_typed_builder) (ver. `0.3.0`) "Compile-time type-checked builder derive using const generics"
* [`typestate_builder`](https://crates.io/crates/typestate-builder) (ver `0.1.1`) "[...] combines `Typestate` and `Builder` patterns"

Note, that I gave the current crate versions in brackets, at the time of writing.
So, when I reference those crates, it'll be based on these particular
versions. All of those crates are great, with `bon` and `typed_builder` being my personal
favorites and also among the most widely used. All these crates generate compile-time validated builders,
so they will give errors _at compile time_ when you forget to set a mandatory field[^runtime-builders].
The `typestate_builder` crate is an honorable mention here, that I stumbled upon after
doing the proof-of-concept implementation presented in this article. At the time
of writing it's very young and incomplete, but it's different from the other mentioned crates
in some important details that --I believe-- would enable it to implement
the ideas presented in this article.

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
    // ⚡ values for all fields
    // ⭐ this is a deliberate feature
    let foo2 = Foo::builder()
                    .first(1f32)
                    //⚡ forgot second
                    .build();
}
```

This example uses `bon`, but it will work --with minimal modifications-- with
all the other mentioned crates[^typed-builder-generics]. There's much more that all these crates can do
for you and it's well worth checking out[^builder-capabilities]. But now let's
take a look at something that none of them can do, at least I wasn't able to make them[^tried-this].

# Problem Statement: Lazy Generics

Let's first look at piece of code that _does not_ compile using any of the builder
crates mentioned above. Afterwards we'll discuss what that code might be useful
for. Say we have a runtime boolean condition `cond`:

```rust
// (1)
let builder = Foo::builder().first(1.337f32);
if cond {
    // (2)
    let foo = builder.second(1usize).build();
    // use foo of type Foo<f32,usize>
    // ...
} else {
    // (3)
    // ⚡ this does not compile
    let foo = builder.second(&"hi").build();
    // use foo of type Foo<f32,&str>
    // ...
}
```
In essence what I try to do is branch the builder on a runtime condition. Both
branches take the same argument for `first`, but different arguments for `second`.
Not only different arguments, but arguments of different _types_. This won't compile
with any of the crates I tested; [here](https://github.com/geo-ant/builder-experiments/blob/main/src/crosschecks.rs)
is a link to a repo that shows what I tried.

The reason this doesn't work is, that the `Foo::builder()` function returns a builder
`FooBuilder<S,T,Internal>` that has the same `S` and `T` generic parameters as the generic
type `Foo<S,T>` and then some additional internal parameters[^state-params]<sup>,</sup>[^typestate-builder]. At 
&#9312; the type `S` of `FooBuilder` gets deduced to `f32`, which is what we want. However, 
at &#9313; the type `T` of `builder` gets deduced to `usize`. That
fixes the type of `builder` to `FooBuilder<f32,usize,...>`, and that makes
it a compilation error to pass a `&str` in &#9314;. If we had passed a different
value of type `usize` that would, of course, have been fine. There are many advantages
that come with this strong type deduction behavior and truth be told, I think
it's the correct default to have.

But wouldn't it also be cool if the code above had just worked? In a way, 
I want to avoid this eager evaluation of generics that is the root of my problem
and make the evaluation more *lazy*. Just because I want to pass a `usize` to
`second(...)` in &#9313;, doesn't mean I want to be forced to pass the 
same _type_ in &#9314;. This is what I mean with *lazy generics*. I feel 
the eager/lazy wording is not quite what I want to express, but I couldn't
come up with a better term. Maybe _decoupled_ is better? I'll happily
take suggestions.

## So What?

If the prospect of learning how builder crates work behind the scenes and doing some
metaprogramming in the process doesn't already excite you, let me provide
some rationale for why the thing above could indeed be cool. Feel free to skip ahead.
I'll concede right away that this is a pretty niche use case and that there are
other, saner ways of achieving a very similar effect. Also it is decidedly not my intention
to badmouth the crates above, I hope that much is clear by now.

At work I have a function with a rather nasty signature that takes a lot of 
parameters, some concrete types and some generic ones. It looks something like this:

```rust
fn calculate<M,R>(data: &[f32], 
             param: f32, 
             mapping: M, 
             reduction: R) -> f32 
    where M: Mapping,
          R: Reduction 
{...}
```

This is still simplified substantially, but it captures the spirit. The non-generic parameters
are `data` and `param`. The generic parameters influence the logic which gets executed inside
the function. What I wanted to do, was to use `bon` --which allows to construct [builders
for functions](https://elastio.github.io/bon/guide/overview#builder-for-a-function)--
to make my callsites more readable. It works by transforming the  functions to structs
with a `.call()` method behind the scenes. The `.call()` method is like the final
`.build()` call in the builder pattern, only that it calls the function with the 
finalized parameters instead of returning a struct instance. Brilliant. 
What I'd like to work is something like this[^not-bon]:

```rust
let calc = CalculationBuilder::new()
                        .data(data)
                        .param(param)
                        .mapping(mapping);

let result = if fiddle { 
                // fiddling: Fiddling
                calc
                    .reduction(fiddling)
                    .call()
             } else {
                // frobnicate: Frobnication
                calc
                    .reduction(frobnicate)
                    .call();
             };
```

I have run-time conditions that require the function to be called with the same
`data`, `param`, and `mapping` arguments, but with a `reduction` of different types.
If I try that, I'll run into the same problem as above, because the builder enforces
the generics eagerly.

# Goal Statement: Lazy Generics

Now with all of the introductory stuff out of the way, let's state the goals
and non-goals for this article: 

*  We want to come up with a builder pattern that supports lazy
   generics and explore the complexities that arise from it.
*  We won't go so far to actually write the procedural macro that generates
   that builder. Instead we'll write the builder by hand
   and think through the steps that we'd take to automate this.

We'll stick with writing a builder for a struct because that's the necessary 
first step to writing builders for functions[^function-builders-where]. Meet
our struct:

```rust
struct Pod<'a, S, T>
where
    S: std::fmt::Display,
    T: std::fmt::Debug + MyTrait,
{
    field1: f32,
    field2: S,
    field3: &'a T,
    field4: T::AssocType,
    field5: Option<T>,
}

// this is just a bogus
// trait that gives us 
// associated types
trait MyTrait {
    type AssocType;
}
```

We'll write a builder for that structure that allows lazy generics, similar
to what I presented above. There are a couple of things going on in this 
struct, so let's examine it:

* We have 3 generic parameters: the lifetime `'a` and the types `S` and `T`.
* We have a concrete type for `field1` thrown in for good measure.
* The generic parameters are constrained in a `where` clause[^constraints].
* `field2`, `field3` and `field5` have a _direct_ dependency on one of
  the generic type parameters.
* `field4` _indirectly_ depends on `T`, via an associated type.

## Interlude: Direct and Indirect Dependencies on Types

I should explain what I mean with _direct_ and _indirect_ dependencies on 
generic types. People more experienced in type-theory will probably scoff at me for
reinventing terms for things that already exist, but alas, I don't know type
theory. I'm a mere programmer with a penchant for type system trickery. Do feel
free to leave a comment, though. I'm very happy to learn.

A _direct_ dependency on a generic type `T` is when a field type can be deduced
from an assignment to the corresponding field. Let's make this more concrete
by imagining you had a function that's generic on `T` and takes the field type 
(which has some dependency on type `T`) as an argument:

```rust
fn takes_field<T>(t: /*field type*/) {}
```

The question is now: can you write `takes_field(value)` without explicitly specifying
the generic type `T`? For example if the field type is `T`, `&T`, `Option<T>`,
`Option<Result<T,()>>`, you definitely can! That's a _direct_ dependency of the
field type on the generic type `T`. However, if the field type is something like
`T::AssocType`, you can't. One reason is that many types `T` or `U` could have
the same `AssocType`. Let's call that an _indirect_ dependency. Those are 
going to be important later.

# First Steps

Since we want to have a compile-time verified builder, we must write the builder
as a state machine, where the state is encoded in the type of the builder itself.
This is called the _typestate pattern_ in Rust and I'm going to explain it in this
article. There's also tons of information about it online. For each field, we want
to encode _via the type of the builder_, whether it has been set. We have five fields
in our structure, so we give our builder five generic types and five fields.

```rust
struct PodBuilder<F1,F2,F3,F4,F5> {
    field1: F1,
    field2: F2,
    field3: F3,
    field4: F4,
    field5: F5,
}
```

Note that these parameters `F1`,...,`F5` are totally generic and have no relation
to the actual field types yet. This is essential for avoiding the problems with eager evaluation
of generics mentioned in the introduction. Not even the `field1` type is fixed to `f32`, although
we know that it can only be `f32`. However, we want to use the _types_ to also 
encode whether a field has been set. For that, let's define a couple of newtypes:

```rust
#[derive(Default)]
struct Empty;
struct Assigned<T>(T);
```

The `Empty` type indicates that a field has not been set, whereas the
`Assigned<X>` type indicates that it was assigned with a value of type `X`. Each
generic type of the builder starts at `Empty` and transitions to `Assigned<...>`
by invoking the corresponding setter function on the builder. Once a field is assigned,
it cannot be assigned again[^assigned-once]. That is the basic logic
we'll implement in the rest of this article, but there are subtleties to consider
as we'll see. Let's also define a couple of traits to indicate if a type 
has a value or if it can be assigned still.

```rust
trait Assignable<T> {}
impl<T> Assignable<T> for Empty {}

trait HasValue {
    type ValueType;
    fn value(self) -> Self::ValueType;
}
impl<T> HasValue for Assigned<T> {
    type ValueType = T;

    fn value(self) -> Self::ValueType {
        self.0
    }
}
```

Those two traits are not strictly necessary for the code in this article, because they
are only implemented by the `Empty` and `Assigned` types, respectively.
I'll mention in this endnote[^default-values] how those traits help us to 
extend the presented method to allow for default values of fields.

## Start and Finish

Before we implement the state transitions, let's see where the builder starts
and where it finishes. The builder starts with all fields empty, so we implement
a constructor for exactly that case.

```rust
impl PodBuilder<Empty, Empty, Empty, Empty, Empty> {
    pub fn new() -> Self {
        Self {
            field1: Default::default(),
            field2: Default::default(),
            field3: Default::default(),
            field4: Default::default(),
            field5: Default::default(),
        }
    }
}
```

This allows us to call `PodBuilder::new()` to obtain a builder with all fields
empty. Note, that this builder is not coupled to the generics of the original
`Pod` struct. Note further, that this also [prevents us](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=1fd9cda519eaa0e952692a2dacf9725a)
from exposing a `Pod::builder()` function to obtain the builder, which is the
--very elegant, but in this case also limiting-- API that the other crates prefer. 

The final stage of the builder is reached when all fields were assigned. Only
then do we allow the user to call the `build()` function. This function
consumes the builder and returns an instance of `Pod`.

```rust
impl<F1, F2, F3, F4, F5> PodBuilder<F1, F2, F3, F4, F5> {
    fn build<'a, S, T>(self) -> Pod<'a, S, T>
    where
        T: Debug + MyTrait,
        S: std::fmt::Display,
        F1: HasValue<ValueType = f32>,
        F2: HasValue<ValueType = S>,
        F3: HasValue<ValueType = &'a T>,
        F4: HasValue<ValueType = T::AssocType>,
        F5: HasValue<ValueType = Option<T>>,
    {
        Pod {
            field1: self.field1.value(),
            field2: self.field2.value(),
            field3: self.field3.value(),
            field4: self.field4.value(),
            field5: self.field5.value(),
        }
    }
}
```

Note, that the `build` function _does_ include the generic types `'a`, `S`, and `T`
of `Pod`, that we had avoided before. It also includes all the trait bounds on
`S` and `T`. It allows us to call `builder.build()` on an instance of `PodBuilder`
if and only if it indicates --via its type signature-- that all fields have been set.
Now let's see how we actually implement state transitions to get us from
an all-empty builder to its final state one by one.

## Setting Field 1: State Transitions for Concrete Types

`Pod::field1` is a concrete type, in this case `f32`. This is the simplest case
we can encounter when implementing state transitions. Whether `field1` is set in our
builder is encoded via the corresponding type `F1`. If this type implements the
`Assignable<f32>` trait (which in our case is just a more complicated way of 
saying that `F1` is `Empty`), then we want to consume our builder,
set the field, and return a new builder that encodes in its type that `field1`
was set.

```rust
impl<F1, F2, F3, F4, F5> PodBuilder<F1, F2, F3, F4, F5> {
    fn field1(self, field1: f32) 
       -> PodBuilder<Assigned<f32>, F2, F3, F4, F5>
    where
        F1: Assignable<f32>,
    {
        PodBuilder {
            field1: Assigned(field1),
            field2: self.field2,
            field3: self.field3,
            field4: self.field4,
            field5: self.field5,
        }
    }
}
```

In the type signature of the builder returned from this setter, `F1` is now of type `Assigned<f32>`
and carries the assigned value in `field1`. All other types `F2`,...,`F5`
just stay as they were and their values get moved into the new instance of
the builder. That allows us to call the setter function before or after any
of the other setter functions, the order of initialization does not matter. 

## Setting Field 2: Simple State Transitions for Generic Types

Setting `field2` is almost as simple as setting `field1`, let's see how its
done:

```rust
impl<F1, F2, F3, F4, F5> PodBuilder<F1, F2, F3, F4, F5> {
    fn field2<S>(self, field2: S) 
       -> PodBuilder<F1, Assigned<S>, F3, F4, F5>
    where
        S: Display,
        F2: Assignable<S>,
    {
        PodBuilder {
            field1: self.field1,
            field2: Assigned(field2),
            field3: self.field3,
            field4: self.field4,
            field5: self.field5,
        }
    }
}
```

The only thing that changed compared to above, is that our setter function
now accepts a generic type `S` and that we restrict `S` in a `where` clause
with the same restrictions as in the original `Pod` type. It's really that
simple, but as we'll see below it's not always going to be this simple when
generic types are involved. It works like this here because of these
reasons:

1. the type of `Pod::field2` has a _direct_ dependency on `S`. That means the type can be
   deduced in the setter function _and_
3. the `where` clause restricting `S` has no dependencies on other types

This gives us a taste of the complexities that we'll be faced with in the
next sections, so let's enjoy for a moment that it really can be this simple
sometimes before we move on.

## Setting Fields 3 and 5: Coupled Generic Types

Both the types of `Pod::field3` (which is `&'a T`) and the type of `Pod::field5`
(which is `Option<T>`) have a _direct_ dependency on `T`, which means `T` can be
deduced by assigning to either of these types. When I initially drafted this section
and the corresponding code, I had a whole spiel about how it was important to
check whether `field3` was already set when setting `field5` (and vice versa), to
help the type deduction. I've archived that code 
[on the playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=ff4392d0e60e2c65e0d89e06dc946ad2),
but it was completely overblown. It turns out, if the field types
obey the conditions mentioned above, we can just treat them like we treated the
previous field. The correspoding setter implementations become:

```rust
impl<F1, F2, F3, F4, F5> PodBuilder<F1, F2, F3, F4, F5> {
    fn field3<'a, T>(self, field3: &'a T) 
       -> PodBuilder<F1, F2, Assigned<&'a T>, F4, F5>
    where
        T: Debug + MyTrait,
        F3: Assignable<&'a T>,
    {
        PodBuilder {
            field1: self.field1,
            field2: self.field2,
            field3: Assigned(field3),
            field4: self.field4,
            field5: self.field5,
        }
    }

    fn field5<T>(self, field5: Option<T>) 
       -> PodBuilder<F1, F2, F3, F4, Assigned<Option<T>>>
    where
        T: Debug + MyTrait,
        F5: Assignable<Option<T>>,
    {
        PodBuilder {
            field1: self.field1,
            field2: self.field2,
            field3: self.field3,
            field4: self.field4,
            field5: Assigned(field5),
        }
    }
}
```
It's just the same as in the section above, there's not much more to it than that.
 A note on type deduction: the final call to `build()` forces that `T` is deduced
as one unified type. So, as long as we end our builder
chains --including the ones that are forked between branches-- with a call to
`build()`, the type system is smart enough to conclude that the assigned types
are supposed to be the same. 

```rust
let builder = PodBuilder::new()
    .field5(Some("hi".into()));
    .field3(&String::new())
// -- other field assignments, possibly branches --
// let builder = ...

// assuming this is now a finished builder
let foo = builder.build();

```

We'll have all the sweet type deduction we come to expect. The important thing
is that the builder chains gets finished with the `build()` method. However, that's
guaranteed to happen, because why else would you have a builder in the first place...?

## Setting Field 4: Field Types with Indirect Dependencies on Generic Types

The type of `Pod::field4` is `T::AssocType`, which means it depends on the
generic type `T` indirectly. We can't deduce `T` from assigning to `field4`.
Somehow, we have to know the type `T`. We could force the user to explicitly
tell us, but I don't like that so much. We could also expose
the setter for `field4` only if we know `T` already, which is the option
that I went with. That is the case when `field3` or
`field5` (or both) have already been assigned.

### Excursion: Dependency Graphs

Since the ultimate goal (not in this article, but eventually) is to implement this
into a derive macro, let's go through this analysis a little more formally. Let's
visualize the direct and indirect dependencies of the builder types (lower row)
and the structure generic types (upper row).

```
Pod:              S    'a     T
                  |    |     /|\
                  |    |    / | \
                  d    d   d  i  d    
                  |    |  /   |   \
                  |    | /    |    \
Builder:   F1     F2   F3     F4   F5
```

The generic types of the builder `F1`,...,`F5` have a one-to-one correspondence
with the builder fields `PodBuilder::field1`,...`Podbuilder::field5`.
Their dependency on the generic types `'a`, `S`, and `T` is via the field types
`Pod::field1`,...,`Pod::field5` of the original structure. Here, a line with an
`i` is an _indirect_ dependency and a line with a `d` is a _direct_ dependency.
Here we have a pretty simple (not fully connected) dependency graph. We are
trying to set `field4`, which is associated with type `F4`. So we look at the graph
and collect all the original generic types on whom `F4` depends _indirectly_. Here, 
that's just `T`, which only has other _direct_ dependencies. So we go
ahead and collect those, in our case
`F3` and `F5`. Now we know that it's a prerequisite that either one (or both)
of the generic arguments `F3`, `F5` have their corresponding value assigned, before
we can assign to the `field4` associated with `F4`. 

### Implementing Setters that Require Other Fields to be Set

Let's now see how to implement the setter for `field4` only if `F3` and/or `F5`
were set. There are three combinations for (`F3`,`F5`) where we want to allow the
setter to be invoked, which are (Empty, Assigned), (Assigned, Empty), and (Assigned, Assigned). In
a procedural macro, I'd probably output dedicated code for all of those 
combinatorial cases. However, for this particular application we can see that
we can collapse (for example) the last two cases into a single `impl` block.

```rust
// covers the case (F3,F5) = (Empty,Assigned)
impl<'a, T, F1, F2> PodBuilder<F1, F2, Empty, Empty, Assigned<Option<T>>>
where
    T: Debug + MyTrait,
{
    fn field4(
        self,
        field4: T::AssocType,
    ) -> PodBuilder<F1, F2, Empty, Assigned<T::AssocType>, Assigned<Option<T>>> {
        PodBuilder {
            field1: self.field1,
            field2: self.field2,
            field3: Empty,
            field4: Assigned(field4),
            field5: self.field5,
        }
    }
}

// covers the cases (F3,F5) = (Assigned, Empty) or (Assigned, Assigned)
impl<'a, T, F1, F2, F5> PodBuilder<F1, F2, Assigned<&'a T>, Empty, F5>
where
    T: Debug + MyTrait,
{
    fn field4(
        self,
        field4: T::AssocType,
    ) -> PodBuilder<F1, F2, Assigned<&'a T>, Assigned<T::AssocType>, F5> {
        PodBuilder {
            field1: self.field1,
            field2: self.field2,
            field3: self.field3,
            field4: Assigned(field4),
            field5: self.field5,
        }
    }
}
```

And just like that, we have finished our implementation of the builder. Let's see
what we can do with it.

# Using the Builder with Lazy Generics

I've put [the code on the playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=579320ddbe4c8cfd95f4cdbb95b431dc),
so please do play with it. Of course, the builder supports the most basic
application, which is constructing a `Pod` from one complete chain:

```rust
let pod = PodBuilder::new()
    .field2(1f64)
    .field1(337.)
    .field5(Some("hi".into()))
    .field3(&String::new())
    .field4(1)
    .build();
```

But that's what all the other builder crates can do as well, so let's look
at some lazy generics:

```rust
impl MyTrait for i32 {
    type AssocType = f32;
}

impl MyTrait for String {
    type AssocType = usize;
}

fn foo(cond: bool, othercond: bool) {
    let s = String::new();
    let builder = PodBuilder::new().field1(1.);
    if cond {
        let builder = builder
            .field2("foo");
        if othercond {
            // pod: Pod<&str,String>
            let pod = builder
                .field5(None)
                .field4(1)
                .field3(&s)
                .build();
            // use pod...
        } else {
            // pod: Pod<&str,i32>
            let pod = builder
                .field5(None).
                .field4(1.)
                .field3(&1)
                .build();
            // use pod...
        }
    } else {
        // pod: Pod<i32, String>
        let pod = builder
            .field3(&s)
            .field5(Some("hi".into()))
            .field2(1)
            .field4(2)
            .build();
        // use pod...
    }
}
```

It shows that we can fork the builder based on runtime conditions without
locking in unassigned types across forks. The builder becomes a stemcell with
lazy generics.

# Outlook: Function Builders and Where Clauses

This has been a long and complicated article, but allow me some final remarks. I think
the most interesting application of builders with lazy generics, is the possibility
of using them to create builders for generic functions.
In principle, there's nothing stopping us from doing that now, based on what
we did. There are two problems that we'll run into:

1. Generic types which are not part of the function arguments or not
   deducable via the function argument types.
2. More complicated trait bounds, such as the circular bounds `where T: Add<S>, S: Sub<T>`.

We can encounter both problems[^phantom-data] in structs as well. I think the first
one is easy to solve, since we can just have our builder's constructor force the user to specify those
types that cannot be deduced. The second problem is a bit trickier:

```rust
fn do_something(first: S, second: T) -> bool 
    where S: Sub<T> + Clone,
          T: Add<S> + Ord,
          
{...}
```

In the setters above, we just copied all the trait bounds of the particular generic type.
That won't work anymore because we can't name `T` in the setter for `S`,
except if we require the type `T` to be known. However, we'd then 
also have to require the type `S` to be known in our setter for `T`. 
We could then never actually set _any_ of these fields due to the circular dependency.
But I _think_ the solution is easier than it looks at first: we should just be
able to skip all the restrictions that depend on generic types other the ones
named in the field type associated with the setter. That means in the setter for `first`
we just restrict `S` on `Clone` and in the setter for `second` we restrict
`T` only on `Ord`. In the final `build()` call, we can then enforce all the
restrictions again, because we can name all of the types.

# Final Words

If you read this far, cheers to you. There are more things that I'd like to say
about this method, but this post is already very long. So I'll just leave it at
that. I don't claim that all builders need to support the lazy generics as presented
here. I just hadn't seen it anywhere else, maybe it's out there and I did not
look hard enough. I'm very happy to engage in the comments at the end of this
article.

# Endnotes
[^runtime-builders]: There's also the excellent and venerable [`derive_builder`](https://crates.io/crates/derive_builder) (ver `0.20.1`), which does all validations (including forgotten fields) at run time. The problems with generics addressed in this article also apply to this crate.
[^bon-core]: The `bon` crate allows to create builders not only for structs but also e.g. for functions. However, this functionality internally transforms the function into a structure with a `.call()` method. The function arguments are made into fields of the generated structure. Then, a builder for this new struct is generated and thus it has the same limitations as the builders that are applied directly to structures.
[^builder-capabilities]: Examples including: optional fields, `Into`-conversions, default parameters and much more, depending on the crate. [Here](https://elastio.github.io/bon/guide/alternatives) is a great overview by the `bon` maintainers.
[^state-params]: The exact form of the other generic parameters varies slightly between crates, but the principle is always the same. Again, bear with me... we'll go into the details later.
[^not-bon]: This is less elegant than [how it would actually look](https://elastio.github.io/bon/guide/overview#builder-for-a-function) in `bon`. But for the sake of this article, it's better like this, since this looks more similar to the builder pattern in the intro section.
[^tried-this]: I've of course tried the code in question with all the mentioned crates and verified that it fails to compile. I've also looked at the macro expansion, which makes me pretty confident that this is not something that these crates _can_ do. However, I might still have gotten things wrong or missed additional options and I am happy to be corrected. See [here](https://github.com/geo-ant/builder-experiments/blob/main/src/crosschecks.rs) to see what I did.
[^function-builders-where]: Function builders don't necessarily follow trivially, because `where` clauses for generics in functions typically involve constraints that are not essential to construct the arguments, but to perform the logic of the function (think `T: Add<U::AssocType>`). In this case we'd like a way to specify two where clauses: one with the essential requirements that enable us to construct the argument types without compilation errors. This where clause would go on the builder struct. And an additional where clause for all the logic requirements that the function needs. This (plus the essential where clause) would then be stuck on the `.call()` method. We could achieve this by allowing attribute macros that capture the essential `where` clause, like `#[essential(where T: Scalar)]` and then the stuff that is not essential for constructing the types could go into the actual `where` clause of the function. Our procedural macro would then take care of splitting and combining the where clauses as necessary.
[^constraints]: When writing procedural macros, it's important to keep in mind that `where` clauses are not the only places where constraints can be places on parameters. To gather all the constraints one has to parse the generic types in the struct definition as well.
[^typestate-builder]: This is where the `typestate_builder` crate does something different. It still runs into the trap of exposing the `Foo::builder()` function as the only way to expose a builder. That is the reason why this example will fail. But it can be tricked into providing an empty builder and then we can actually make this example compile. However, this crate is currently not able to work with the more complex example that I'll present in the sections below.
[^assigned-once]: This is a choice on my part, but it's something that the other builders to as well. We could also modify the state machine pattern to allow overwriting, but I feel it's more likely an indication of an accident on the user's part.
[^default-values]: At least for non-generic field types it's easy to allow for default values (it gets more complicated if the field type is generic). What we do is introduce another type `WithDefault<T>(T)` that implements `Assignable<T>`, but also `HasValue<ValueType = T>`. For fields where we want to allow default values in case the user does not set one, we start with a `WithDefault<T>` containing the default value rather than `Empty`. If we assign to a `WithDefault`, then it transitions to `Assigned`. But even if we don't, the builder will allow to call `build` because `WithDefault` also implements `HasValue`.
[^typed-builder-generics]: Except the `typestate_builder` crate which, at the time of writing, still struggles with generics. At least when we use the intended API. It can be hacked to make this and the simple lazy generic example work, see [here](https://github.com/geo-ant/builder-experiments/blob/main/src/crosschecks.rs)
[^phantom-data]: In structs we can't have types that aren't part of the fields at all. We'll at least have phantom fields, but in practice those should not expose setters, but instead force the user to specify the types explicitly.
