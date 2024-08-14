---
layout: post
tags: rust unstable traits const
#categories: []
date: 2023-09-01
last_updated: 2023-09-07
title: 'Curiously Cumbersome Rust: Type-level Programming'
#excerpt: ''
#description:
#
#
# Make sure this image is correct !!!
og_image: cumbersome-rust-meta.png
#
#
# Make sure comments are enabled !!!	
comments_id: 51
---

The moment that spawned this article was when I asked myself _how hard
can it be to make sure two types have the same size at compile time_? Well...
it's complicated. In here, we'll do a deep dive into the limits of compile
time metaprogamming in today's (and tonight's) Rust.

# Motivation

In my [last article](/blog/2023/unsafe-rust-exploration/)
I wrote a function to perform an in place mapping from a `Vec<T>` to a `Vec<U>`
where the important precondition was that `T` and `U` have the same size and
alignment. The function looked something like this:

```rust
fn map_in_place<T,U,F>(v: Vec<T>, mut f: F) -> Vec<U> 
    where F: FnMut(T) -> U {
    assert_eq!(std::alloc::Layout::<T>::new(), 
        std::alloc::Layout::<U>::new());
    // loads of unsafe code here
}
```
I won't go into the unsafe code here because that was the topic of the aforementioned
article. The thing that bugged me was that `assert_eq!` in there.
Not the fact that it was in there at all, but that the panic would only occur
at runtime [^runtime-panic]. As a die-hard metaprogramming fan, 
it felt weird to check a condition at runtime
that we can clearly check at compile time. It would be great if we
can stick this condition into the function signature, possibly using traits
to make it blatantly obvious that we want the types `T` and `U` to have the same
size and alignment. 

## Today's Problem: Same Size for Two Types

For this post, let's consider a slightly simplified problem and just
check that the two types `T` and `U` have the same size and not bother with
the alignment. This is just to keep the examples concise, because once we 
figure out how to check for size, adding an alignment requirement is trivial.
So what we want is this:

```rust
fn do_somehting<T,U>(t: T, u: U) 
    // where: T and U have same size 
{
    // do something
}

// this compiles
do_something(1u8,2u8);
// this also compiles
do_somehting(1f32,2i32);
// this must not compile
do_something(1u8,2u32);
```

Our goal is to make the compiler accept the code only if our two types
`T` and `U` have the same size and emit an error message otherwise. 
The compiler knows the size of a (sized) type at compiletime. That's why it
should be simple enough to find a solution that enforces identical size at compile time,right? Right?

# Using Associated Constants

My first intuition was that associated constants would help us elegantly enforce trait bounds
to restrict our `do_something` function arguments to types with same size.

There are many ways to skin this cat and my ideas were definitely influenced
by how metaprogramming in C++ uses associated types and compile time constants
to give us metafunctions. I married this with a more Rusty idea of 
trait bounds and I came up with the following, pretty straightforward, code:

```rust
pub trait SameSizeAs<T> {
    const VALUE: bool;
}

impl<T,U> SameSizeAs<T> for U {
    const VALUE: bool = 
        std::mem::size_of::<T>() == std::mem::size_of::<U>();
}
```

So what we do is implement a trait `SameSizeAs<T>` for every type `U`, which
indicates whether `T` and `U` have the same size via an associated constant. That's
not too bad. We can use the trait like so:

```rust
pub fn do_something<T,U>(t: T, u: U) 
where U: SameSizeAs<T,VALUE=true> {
    // do something
}
```

I find this pretty elegant and concise and it turns out the error messages are
very readable if we try to call the function with two types of different size.
There's just one problem with this: it does not compile on stable Rust. Current stable Rust 
(1.72 at the time of writing) does not allow us to compare associated
constants for equality; we need the feature
[`associated_const_equality`](https://github.com/rust-lang/rust/issues/92827)
to compile it. I found that a bit disappointing because I liked the simplicity of the solution and I would like this to work on stable Rust.

For completeness let me link to another [known way](https://github.com/rust-lang/rfcs/issues/3162)
of using compile time booleans in `where` clauses via a clever combination of 
Const Generics and Traits. However, it requires the unstable feature
[`generic_const_exprs`](https://github.com/rust-lang/rust/issues/76560). I won't 
go into detail here but we will see this feature pop up in a different context.

# Using Associated Types

So the problem with the solution above was that we cannot yet compare 
associated constants for equality in trait bounds. But we definitely can
compare types for equality in trait bounds and so that is the core of the
next approach I took. Translate the boolean _values_ into _types_ and do the
equality comparison on the types rather than the values. So that's what I tried next.

Coming from C++, I know that metaprogramming with types can
get a bit hairy at times. However, I was pretty confident that I could find a solution.
Because after all I was only trying to make the compiler enforce something 
that it already knows! 

Now, since I didn't want to use actual boolean values at compile time 
I had to translate the idea of booleans into types:

```rust
struct TrueType;
struct FalseType;

trait BoolType {}
impl BoolType for TrueType {}
impl BoolType for FalseType {}
```

Strictly speaking, the whole `BoolType` trait is not necessary but I feel it makes the
downstream code easier to read. Now we can define a trait that 
tells us whether a type `T` that implements it has the same size as another
type `U`:

```rust
pub trait SameSizeAs<U> {
    type Value : BoolType;
}
```

You can see why I like the `BoolType` trait here: it mirrors the syntax we would use to define
the type of a struct field or an associated constant. Compare this implementation with the way we did it above. Finally, we can add a nice `where` clause into
our function definition:

```rust
pub fn do_something<T,U>(t: T, u: U) 
where T: SameSizeAs<U,Value=TrueType> {
    // do something
}
```

This reads very similar to the constant based code above but now it is fine to write 
`Value=TrueType`  in the `where` clause in stable Rust. The reason is that
we are testing for equality of an associated _type_ and not a compile time 
constant _value_. 

Finally, there is just one thing missing and that is to write a blanket implementation for `SameSizeAs`
that serves our purpose.  We need to have some way to go from a compile time known condition (a `const bool`)
to a type. Since [Rust 1.51](https://blog.rust-lang.org/2021/03/25/Rust-1.51.0.html) we
have Const Generics to help us make this transition. That's the only way I saw
how to do that. In C++ we would use a templated struct with boolean template
parameters and associated typed. In Rust we can to a similar
thing when we bring traits into the mix:

```rust
pub struct Condition<const B: bool>;

pub trait TruthType {
    type ValueType : BoolType;
}

impl TruthType for Condition<true> {
    type ValueType = TrueType;
}

impl TruthType for Condition<false> {
    type ValueType = FalseType;
}
```

We can use the struct and the trait together to go from a compile time
known condition to a type. Unfortunately, as of the time of writing
we cannot simply use it as `Condition<Cond>::ValueType` but we have to use
the fully qualified type so that the compiler can understand the associated
type, even if it is actually unambiguous. That means we must use it as
`<Condition<Cond> as TruthType>::ValueType` which is a bit cumbersome but
does the trick [^where-clause]:

```rust
impl<T,U> SameSizeAs<U> for T 
where Condition<{core::mem::size_of::<T>() 
        == core::mem::size_of::<U>()}>: TruthType {
    type Value = <Condition<{core::mem::size_of::<T>() 
        == core::mem::size_of::<U>()}> as TruthType>::ValueType;
}
```

We have now created a metafunction that transforms a compile time known
boolean into a type. We can use it to find out whether two given types are of 
the same size. That's great and all, but we again have to use an unstable feature
for that. This where the feature [`generic_const_exprs`](https://github.com/rust-lang/rust/issues/76560)
pops up again. We need this to use generic parameters `T` and `U` as part of
the Const Generic parameter for `Condition`. It's a bit unfortunate since
the whole exercise was to go from a compile time boolean to a type and it seems to me
we need an unstable feature to accomplish that in our particular case. I would be happy to be proven
wrong here.

Be that as it may, we can now use our type and trait to restrict the generic 
types passed to our `do_something` function:

```rust
pub fn do_something<T,U>(t: T, u: U) 
where T: SameSizeAs<U,Value=TrueType> {
    // do something 
}
```

Now the compiler will let us invoke `do_something` with types of the
same size and will give an error otherwise. I find it hard to compare which
unsafe feature has a better chance of making it to stable soon, but it is
worth noting that as of now, `generic_const_exprs` is still
described as "highly experimental" in the [associated tracking issue](https://github.com/rust-lang/rust/issues/76560)
and that the compiler issues a dedicated warning when it is used.

# Rethinking and Making it Work on Stable

There is another way to go about the whole problem, which does not involve
traits. [For a while](https://github.com/rust-lang/rust/pull/89508) stable Rust
has offered the possibility of panicking in `const` evaluated contexts. A
panic in `const` context will produce a compile error, though
I can't find the exact Rust version that stabilized it. Framing the problem like
this makes it conceptually similar to a `static_assert` in C++, though it is not quite 
as straightforward.

What we need to do to invoke a `const` panic is to force the compiler to 
constant evaluate the panic. What we do is:

```rust
const ASSERTION : () = assert!(Cond,"condition was not satisfied");
```

Here, `Cond` needs to be a compile time known boolean. This code produces a 
compile error if and only if `Cond` evaluates to `false`. 
So now we might just try to replace the runtime assertion in our function
by a compile time assertion like so:

```rust
fn do_something<T,U>(t: T, u: U) {
    const ASSERTION : () = assert!(core::mem::size_of::<T>()
                            ==core::mem::size_of::<U>(),
                           "T and U must have the same size");
    // do something
}
```

However, this does not compile because the compiler points to `T` and
`U` with the error message _use of generic parameter from outer function_.
What does that mean? The way [it was explained to me](https://users.rust-lang.org/t/cant-use-type-parameters-of-outer-function-but-only-in-constant-expression/96023)
is that `const` items exist as if they were global, even if they were defined
inside a function. That is why we cannot access the generic parameters of the
function in the `const` item `ASSERTION`. But there is a way around it. Let's
make `ASSERTION` an associated constant of a struct:

```rust
struct SameSize<T, U> {
    phantom: std::marker::PhantomData<(T, U)>,
}

impl<T,U> SameSize<T,U> {
    const ASSERTION: () = assert!(std::mem::size_of::<T>() 
                           == std::mem::size_of::<U>(),
                          "types do not have the same size");
}
```

Now what we have to do is force the creation of that constant inside the
function. But we can't just use another `const` item to do that 
because that would, again, not allow us to access the types `T` and `U` for the
reasons stated above. However, we _can_ do it in a context that is not `const`
evaluated and whose only purpose is to force the [monomorphization](https://en.wikipedia.org/wiki/Monomorphization)
of the compile time assertion we are interested in.

```rust
pub fn do_something<T,U>(t: T, u: U) {
    _ = SameSize::<T,U>::ASSERTION;
    // do something
}
```

Now when we try to invoke `do_something` with types of different sizes 
the compiler will print an error message. This one finally works on stable Rust, which
is pretty satisfying. However, while it is nice that this does work at compile
time, there is no indication in the function signature that we require
`T` and `U` to be of the same size. We must relegate this fact to the documentation.

# Providing Fallback Implementations

The stated goal of this article was to enforce that `T` and `U` have the same
size at compile time and we have achieved that in different ways, one of
which works on stable. But what if we did not want to issue a compile error in 
case `T` and `U` have different sizes but rather provide a fallback implementation?
Let's go very briefly through the presented solutions starting with the last one:

I see no way of using compile time assertions for branching in code generation
because their only purpose is to emit a compile error. So that one is out, I think. The case
is different when using associated types in traits, because in principle we could
write two incarnations of `do_something`: one where `T: SameSizeAs<U,Value=TrueType>`
and one where `T: SameSizeAs<U,Value=FalseType>`. However, currently the
trait solver in Rust does not recognize these two things as disjoint cases so
that one won't work yet. There's some clever ways around those limitations,
but I am not sure they'll work for this case. You can read all about it --shameless
plug incoming-- in my article on [mutually exclusive traits in Rust](/blog/2021/mutually-exclusive-traits-rust/).
Lastly, using associated constants: again, we could in theory write two implementations,
but as of now the cases `U: SameSizeAs<T,VALUE=true>` and `U: SameSizeAs<T,VALUE=false>`
are not recognized as disjoint.  However, it is stated as a [future goal](https://github.com/rust-lang/rust/issues/92827#issuecomment-1260486226)
in the associated tracking issue.

If you are aware of [specialization](https://github.com/rust-lang/rust/issues/31844)
you'll recognize that this would offer another way of providing
a fallback implementation. It does not work quite like the solutions outlined 
above but it can be used to achieve something to that effect. Specialization
is a big complex of features that is, as of the time of writing, unsound
and even [a minimal subset](https://github.com/rust-lang/rust/pull/68970) is
still unstable.

## Fallback Implementations without Specialization

This section is an idea that was posted by reddit user `u/Dragon-Hatcher`
[here](https://www.reddit.com/r/rust/comments/168zdh6/comment/jyz2pfx/?utm_source=share&utm_medium=web2x&context=3)
that has to be one of the most brilliant applications of the KISS principle
I have seen. Let's just do the obvious thing and stick an `if` inside the
function like so:

```rust
fn do_stuff<T,U>(t: T, u: U) {
    use std::mem::size_of;
    if size_of::<T>() == size_of::<U>() {
        // do one thing
    } else {
        // do another thing
    }
}
```

What happens here is that the compiler will evaluate the condition
at compile time and just optimize out the branch that is not taken. Don't believe
me? [Try it on godbolt](https://godbolt.org/z/EqzM35qha). The one thing I don't
know is that the compiler will always evaluate a `const fn` at compile time when
it can [^const-fn], but here it clearly works.

# Final Thoughts

First of all, I'm happy to hear all the things I got wrong in this article
because this is indeed a complex topic. Secondly, I would be interested in other 
ways to solve this problem that I missed here, especially ones that work on stable.

While this writeup has been fun, it has demonstrated to me that interacting with
types in nontrivial ways during metaprogramming in Rust is hard, especially in
the context of conditional compilation. Furthermore,
the trait system still has some rough edges, where stuff that 
intuitively should work does not [^chalk]. That's a compliment
to Rust because it is surprising to run into these problems in such a well designed
language. I'm also not trying to say that the current trait system is badly implemented because when it works
(which is almost all of the time) it works _amazingly_, but this exercise would
have been a oneliner in _Modern C++_&trade; [^cpp]. 

## Other Solutions
I'll collect some other solutions that people send me here:

* I already added a section on fallbacks without specialization above. (thanks again [u/Dragon-Hatcher](https://www.reddit.com/user/Dragon-Hatcher/))
* [Another nightly solution](https://www.reddit.com/r/rust/comments/168zdh6/comment/jz44fgs/?utm_source=share&utm_medium=web2x&context=3)
that works entirely inside a `where` clause. (thanks [u/matthieum](https://www.reddit.com/user/matthieum/), thanks [u/Dragon-Hatcher](https://www.reddit.com/user/Dragon-Hatcher/))

# Endnotes
[^where-clause]: If it strikes you as odd that we have to repeat the exact same condition in the where clause that we used in the body, you are not alone. In principle the compiler should know that `TruthType` is implemented for all incarnations of `Condition<C>`. It also does not help if we write `where Condition<true>: TruthType, Condition<false>:TruthType`. I suspect those are limitations in the current trait solver.
[^chalk]: There are efforts to implement [a new trait solver](https://blog.rust-lang.org/inside-rust/2023/07/17/trait-system-refactor-initiative.html) with the aim of improving the current situation. Thanks to reddit user `u/Sharlinator` for pointing it out [here](https://www.reddit.com/r/rust/comments/168zdh6/comment/jyz37s3/?utm_source=share&utm_medium=web2x&context=3) that this was not Chalk, as I had stated in a previous version of this endnote.
[^cpp]: I _know_ C++ has massive problems and I will choose Rust over it any time but the (non macro based) metaprogramming and conditional compilation is currently stronger in C++. Though for normal (non-meta) usecases Traits beat Concepts any day of the week.
[^const-fn]: Meaning when we don't force the evaluation in a `const` context.
[^runtime-panic]: The actual condition inside the assert is likely evaluated at compile time and the code is optimized accordingly, but the panic will occur only at runtime. Thanks `Shnatsel` for pointing that out [here](https://www.reddit.com/r/rust/comments/168zdh6/comment/jz08b6o/?utm_source=share&utm_medium=web2x&context=3).
