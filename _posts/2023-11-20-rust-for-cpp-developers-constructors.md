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
provide one way to initialize an instance of a type [^initialization-cpp]. Say 
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
`Rectangle` class, which is very useful if we appreciate encapsulation. Before 
we jump into how to do that in Rust, let's note that in C++ constructors are so
called _special member functions_. They have special syntax both how 
they are defined and how they are used, but really constructors are 
just functions that take some arguments and return an instance 
of the type. There's nothing stopping us from just creating a static member 
function that takes the width and height and returns a rectangle. In fact,
this idiom in C++ is called [Named Constructors](https://isocpp.org/wiki/faq/ctors#named-ctor-idiom).
The ISO C++ website calls it a "technique that provides more intuitive and/or
safer construction operations for users of your class" ([link](https://isocpp.org/wiki/faq/ctors#named-ctor-idiom)).

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
}

// Usage
fn main() {
    let rect = Rectangle::new(1.,2.);
    // ...
}
```

TODO 
* mention constructors less useful with errors as values

# Default Constructors

!!

# Copy Constructors

Another major usecase of constructors is copying data using the copy constructor.

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
