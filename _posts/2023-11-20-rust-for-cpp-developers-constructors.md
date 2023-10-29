---
layout: post
tags: update
#categories: []
date: 2023-11-20
last_updated: 
#excerpt: ''
#description:
#permalink:
title: 'Idiomatic Rust (for C++ Devs): Constructors & Conversions'
#
#
# Make sure this image is correct !!!
og_image: 
#
#
# Make sure comments are enabled !!!	
comments_id: 
---

When I started in Rust as a C++ developer, one of the features I missed the most
at first were constructors. This post tries to explore the many roles that
constructors have in C++ and to see how they can (or can't) be mapped to different
parts of the Rust language. Although I'll use C++ terminology,
this article is likely helpful for developers coming to Rust from other
backgrounds as well.

There are many types of constructors in C++ and, as we'll see, they serve a wide
range of purposes. I'll address these purposes section by section and we'll explore
if and how we can map them to Rust.

# Initialization

One of the most obvious (and most important) purposes of constructors is to 
provide a way to initialize an instance of a type [^initialization-cpp]. Say 
we have a simple class definition like so:

```c++
class Rectangle {
public:
    Rectangle(double width, double height);
private:
    double width;
    double height;
}
/**omitted definitions**/

// Usage
int main() {
    Rectangle rect(1.,2.);
    //...
}
```

Here the constructor allows us to initialize the private fields of the 
`Rectangle` class, which is very useful if we appreciate encapsulation. 

Before we jump into how map this usecase to Rust,
let's note that in C++ constructors are so called _special member functions_.
They have special syntax both how they are defined and how they are used,
but really constructors are just functions that take some arguments and return an instance 
of the type. There's nothing stopping us from just creating a static member 
function that takes the width and height and returns a rectangle [^named-constr].
In fact, this idiom in C++ is called [Named Constructors](https://isocpp.org/wiki/faq/ctors#named-ctor-idiom).
The ISO C++ website calls it a "technique that provides more intuitive and/or
safer construction operations for users of your class" ([link](https://isocpp.org/wiki/faq/ctors#named-ctor-idiom)).

Interestingly, that's exactly how we would do it in Rust. We just write an associated
function (the equivalent of a static member function) and pass arguments to it.

```rust
struct Rectangle {
    width: f64,
    height: f64,
}

impl Rectangle {
    pub fn new(width: f64, height: f64) -> Self {
        Self {
            width,
            height,
        }
    }

    pub fn square(dim : f64) -> Self {
        Self {
            width : dim,
            height : dim,
        }
    }
}
```

Rust has no special syntax or semantics for constructors. If we want to provide them,
we just write associated functions that return an instance of our type. Since 
`new` is not a keyword in Rust, it is customary (but by no means mandatory) to call 
one constructor of your type, preferrebly one that a lot of users will interact with,
`new`. That `new`-function can take the number of arguments that make sense (including no arguments).
For our rectangle that would be the width and height.

If we want to provide another constructor, Rust forces us to create a new associated
and call it by a different name than `new`. There is no function overloading in 
Rust [^function-overloading] and no default arguments, so we are forced to create 
a different function which makes us think about a useful name. For our `Rectangle`
struct that would be the `square` associated function which makes everything very
explicit. In C++ we could be tempted to overload a constructor that just takes
one parameter. While this might be be okay-ish for a rectangle type, it can quickly
become a problem for more complex types.

One example from the standard library is for example [`Vec::new`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.new)
that takes no arguments and constructs an empty vector. To create a vector with 
a given capacity we use [`Vec::with_capacity`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.with_capacity)
and pass it the initial capacity.

## Enforcing Invariants with Constructors that Fail

Constructors are also a great way to help us enforce some invariants about a type.
In our Rectangle example we might want to make sure that the dimensions
of our rectangle are nonnegative. In a constructor in C++ we would have to signal this
with an exception. Even if we were big errors-as-values proponents, we could not 
return a [`std::expected<Rectangle,std::runtime_error>`](https://en.cppreference.com/w/cpp/utility/expected)
if we wanted to. A constructor for a type `T` is a special member function that can 
only return `T`. However, the named constructor idiom would allow us
to make this adjustment.

There's a lot to be said about the pros and cons of exceptions
and this is not the place to say it. Rust does not have them and thus the way
to communicate errors is as values. If we have a constructor that can fail, we 
just make it explicit in the signature and have it return `Result<Self, Error>`
where `Error` is an appropriate error type. An example in the standard
library is `CString::new` that takes a string of bytes and transforms it into a 
C-style (null-terminated) string, but it will return an error if there 
internal null-bytes in the given input. 

# Default Constructors

Another supremely important use case of constructors is _default construction_.
A constructor that can be called with no arguments [^no-arg-constructor] is a default
constructor and is required e.g. for many operations in standard library containers.
It's so essential in C++ that writing `T t;` for a user defined `T` will not give us 
an uninitialized instance of `T` but a default constructed one.

The extand of what _default constructed_ means semantically will vary from type to type but
at least it implies that the instance will not contain random nonsense. A default 
constructed `std::shared_ptr` will not be safe to dereference but at least it contains 
a null pointer, which is much better than a random address. If you are writing a 
numerical optimization library, the default constructed instance of your `Optimizer` type 
could contain sensible default values for stopping criteria and the like and might
be ready to use right away.

The way we signal that a type is default constructible in Rust is to implement the 
[`Default`](https://doc.rust-lang.org/std/default/trait.Default.html) trait on it.
`Default` requires exactly one associated function `fn default() -> Self`, which 
already implies that default construction cannot return an error. It's a good
idea to check whether a type implements `Default`. For example `Vec` implements 
`Default`, and it turns out writing `Vec::default()` is the same as writing `Vec::new()`.
If we write a type that exposes a `new() -> Self` constructor it is customary to 
also implement the `Default` trait. In fact, there is even 
[a clippy lint](https://rust-lang.github.io/rust-clippy/master/#/new_without_default)
for exactly that.


# Copy Constructors

Another major usecase of constructors is copying data using the copy constructor.
If we invoke a copy constructor that is because we want a copy of the instance


TODO: with the arrival of smart pointers the need to manually write copy constructors 
is drastically reduced. TOTODOSO !!!!!!!!!!!!!!! Manually writing a copy constructor implies
that for copying an instance something has to happen that 
goes beyond just calling all the member copy constructors or just doing a 
byte for byte copy. Before the arrival of smart pointers the canonical example 
was the _deep copy_ of a type that manages some memory behind a pointer member.


In C++, depending on a few conditions, copy constructors may be automatically
generated for a type, but they can also be explicitly manually declared.

FIRST DO FULL FLEDGED CLONE / COPY CONSTRUCTORS

## Trivially Copyable Types

For some types, even calling default copy constructors (which in turn invoke the
copy constructors of the type's members) may be unnecessarily expensive, because
just doing a byte-for-byte copy to a new location would suffice. That's why, in C++,
we have the concept[^concept-triv] of [trivially copyable](https://en.cppreference.com/w/cpp/named_req/TriviallyCopyable)
types in C++. Those are types that can be copied by doing a byte-for-byte copy of the memory. 
Whether a type is trivially copyable can be tested at compile time with the
[`std::is_trivially_copyable`](https://en.cppreference.com/w/cpp/types/is_trivially_copyable)
type trait, which the compiler will specialize for our types. Say we define a struct 
that is an aggregate of trivially copyable types like so:

```c++
struct Point {
    double x;
    double y;
}
```

This type, [as per the standard](https://en.cppreference.com/w/cpp/language/classes#Trivially_copyable_class),
is then also trivially copyable. If we then created an aggregate
of multiple `Point`s, that will still be trivially copyable and so on. That's
a really neat thing in C++ because it will let the compiler replace calls to 
many copy constructors by one memory copy. It's important to note that it's
undefined to rely on manual specializations of `std::is_trivially_copyable`.

Rust also has the concept of trivially copyable types and has a marker trait 
called [Copy](https://doc.rust-lang.org/std/marker/trait.Copy.html) for it. Marker 
traits are traits that have no associated methods and instead tell the compiler 
some properties about your type. Although it has no methods, the compiler will 
not implement the `Copy` trait on your types, since Rust wants you to be 
explicit about the semantics of your types [^auto-traits].

TODO copy trait example. TODO mention that copy implies clone and that I don't 
know a clone of a copy type is always optimized away.

# Move Constructors

I'm not sure if this concept is widely applicable to other language but 
C++ and Rust both have move semantics. However, the way the languages think about
move semantics is _very_ different. We'll explore the differences a bit in this
section, before coming to our surprisingly short conclusion of how move constructors
work in Rust.

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
[^concept-triv]: It's not a _concept_ in the C++20 meaning of the word. Strictly speaking it is a _named requirement_.
[^auto-traits]: There are a handful of marker traits that the compiler will implicitly implement for you if appropriate. Those are called [Auto Traits](https://doc.rust-lang.org/beta/reference/special-types-and-traits.html#auto-traits) and are very carefully chosen. The most common auto traits that programmers interact with are the `Send` and `Sync` traits that are important for describing thread safety via the type system.
[^named-constr]: One drawback I can think of with using static functions as named constructors in C++ is that they won't be useful in contexts like `emplace` or `std::make_shared` where we use perfect forwarding of constructor arguments for in place construction of objects.
[^function-overloading]: You _can_ abuse the trait system to get something like overloading. Don't do that.
[^no-arg-constructor]: Note the wording "can be called with no arguments", not "takes no arguments". See [here](https://isocpp.org/wiki/faq/ctors#default-ctor).
