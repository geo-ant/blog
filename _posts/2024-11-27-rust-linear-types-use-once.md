---
layout: post
tags: rust metaprogramming generics
#categories: []
date: 2024-11-27
last_updated: 2024-11-29
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Cursed Linear Types In Rust'
#
#
# Make sure this image is correct !!!
og_image: cursed-linear-types.png
#
#
# make sure comments are enabled
comments_id: 74
math: false
---

Inspired by Jack Wrenn's post on [Undroppable Types](https://jack.wrenn.fyi/blog/undroppable/)
in Rust, I set out to see if it's possible to create types that must be used exactly
once. From my understanding, those things are called _linear types_, but
don't quote me on that[^title].

Let's see if we can create a struct `UseOnce<T>` which enforces that an instance
is used (or _consumed_) exactly once. It should be impossible to consume it
more than once, and it should produce a compile error if it's not consumed at all.
The first part is trivial with destructive move semantics, the second
part is where we ~~steal~~ adapt Jack's original idea.

# Implementation

```rust
use core::mem::ManuallyDrop;
use core::mem::MaybeUninit;

pub struct UseOnce<T>(MaybeUninit<T>);

impl<T> UseOnce<T> {
    pub fn new(val: T) -> Self {
        Self(MaybeUninit::new(val))
    }

    pub fn consume<F, R>(self, f: F) -> R
    where
        F: FnOnce(T) -> R,
    {
        // (1)
        let mut this = ManuallyDrop::new(self);
        // (2)
        let mut val = MaybeUninit::uninit();
        std::mem::swap(&mut this.0, &mut val);
        unsafe {
            let val = val.assume_init();
            f(val)
        }
    }
}

impl<T> Drop for UseOnce<T> {
    fn drop(&mut self) {
        const {
        panic!("UseOnce instance must be consumed!")
        }
    }
}

fn main() {
    let instance = UseOnce::new(41);
    // (3)
    // comment out this line to get a compile error
    let _result = instance.consume(|v| v + 1);
}
```


[Playground Link](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=8bb04cf8311fd98e0506a1b764b72d2b).
Again, the clever part is Jack Wrenn's original idea. I was also surprised this
works. To my understanding, it relies on the fact that the compiler can reason
that the drop implementation does not have to be generated when `consume` is 
called due to &#9312;. There's some additional unsafe trickery in &#9313;,
which is not terribly important but it's actually safe. It allows me to use
`MaybeUninit<T>` instead of `Option<T>` as the inner type so that there's no
space penalty as there could be if I had used an `Option`.

As is, the code compiles just fine, but if we comment out the `consume` below
&#9314;, it will fail with a compile error like so:

```
error[E0080]: evaluation of `<UseOnce<i32> as std::ops::Drop>::drop::{constant#0}` failed
  --> src/main.rs:27:9
   |
27 |         panic!("UseOnce instance must be consumed!")
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ the evaluated program panicked at 'UseOnce instance must be consumed!', src/main.rs:27:9
   |
   = note: this error originates in the macro `$crate::panic::panic_2021` which comes from the expansion of the macro `panic` (in Nightly builds, run with -Z macro-backtrace for more info)

note: erroneous constant encountered
  --> src/main.rs:26:9
   |
26 | /         const {
27 | |         panic!("UseOnce instance must be consumed!")
28 | |         }
   | |_________^

note: the above error was encountered while instantiating `fn <UseOnce<i32> as std::ops::Drop>::drop`
   --> /playground/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/src/rust/library/core/src/ptr/mod.rs:574:1
    |
574 | pub unsafe fn drop_in_place<T: ?Sized>(to_drop: *mut T) {
    | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For more information about this error, try `rustc --explain E0080`.
```

Not exactly pretty but it does the trick. Note, that the compile error
is [not triggered](https://www.reddit.com/r/rust/comments/1h0zcku/comment/lzexqsz/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
by simply running `cargo check`, but we need to run `cargo build`.

# Why It's Cursed

Unfortunately, the `UseOnce<T>` is not as useful or powerful as it might seem
at first sight. Firstly, since the compiler error is enforced by the `Drop` implementation, we
can just [`mem::forget`](https://doc.rust-lang.org/std/mem/fn.forget.html) the instance
and not actually consume it. I don't feel this is a giant problem because it's
still very explicit and arguably counts as a sort of consumption. However,
there's a [more fundamental problem](https://www.reddit.com/r/rust/comments/1h0zcku/comment/lzaggnp/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
with linear types in Rust as pointed out by `u/Shnatsel` in the reddit thread
for this post. Note also that I am using the term _linear types_ somewhat loosely and incorrectly,
please see [this comment thread](https://www.reddit.com/r/rust/comments/1h0zcku/comment/lz7xox5/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button).

Secondly, the presented API allows us to "exfiltrate" the inner value of the `UseOnce<T>` instance
by just calling `consume` with the identity function. To address this, we can
replace the implementation of `consume` by two functions like so:

```rust
pub fn consume<F, R>(self, f: F) -> R
where
    F: FnOnce(&T) -> R,
{
    let mut this = ManuallyDrop::new(self);
    let mut val = MaybeUninit::uninit();
    std::mem::swap(&mut this.0, &mut val);
    unsafe {
        let val = val.assume_init();
        f(&val)
    }
}

pub fn consume_mut<F, R>(self, f: F) -> R
where
    F: FnOnce(Pin<&mut T>) -> R,
{
    let mut this = ManuallyDrop::new(self);
    let mut val = MaybeUninit::uninit();
    std::mem::swap(&mut this.0, &mut val);
    unsafe {
        let mut val = val.assume_init();
        let pinned = Pin::new_unchecked(&mut val);
        f(pinned)
    }
}
```

[Playground Link](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=18cab23d9f56c50bfbae024f863233a7).
Calling any of these functions will still consume the instance of `UseOnce<T>`,
but the functions only expose access to the inner value by shared or mutable
reference, respectively. The borrow checker prohibits simply passing the reference
to the outside. Note, that we have used the infamous `Pin` in the `consume_mut`
function to express that the inner value must not be moved out of this reference[^unsafe].

Thirdly, as was [pointed out](https://play.rust-lang.org/?version=stable&mode=debug&edition=2021&gist=02cc5096672900f10fb190595c6361ff)
by `u/SkiFire13` in the [original reddit thread](https://www.reddit.com/r/rust/comments/1gzmwcb/undroppable_types/),
this trick relies on the compiler's ability to reason 
_without optimizations_ that the type will not be dropped[^unspecified]. Thus,
simply sticking a function call between the creation and consumption of the instance
will make this code fail[^panic]:

```rust
fn foo() {}

fn main() {
    let instance = UseOnce::new(41);
    foo();
    let _result = instance.consume(|v| v + 1);
}
```

This code does not compile despite the value being consumed. You can see how
this severely limits the applicability of `UseOnce`. There is an even more cursed
remedy for that, which is using the idea of the [prevent_drop](https://github.com/mickvangelderen/prevent_drop)
crate. In that crate, a non-existing external function is linked in the `Drop`
implementation, which moves the error to link time. That will make it work for
this case but it also makes the error even uglier[^linker].

# Endnotes
[^title]: Unless you are quoting the title of this article which explicitly says linear types... I feel stupid now.
[^linker]: Plus it introduces the can of worms of how to know that a symbol name is never going to be actually linked. There are ways around that, but I don't feel they'll be pretty.
[^panic]: If you want to find out why, it's explained in the comment thread.
[^unspecified]: To add insult to injury, this implementation relies on [unspecified behavior](https://www.reddit.com/r/rust/comments/1gzmwcb/comment/lyzj7yi/) of the compiler. This won't cause runtime UB though, to my understanding. So the worst thing that can happen is that this neat trick stops compiling alltogether. Thanks to `u/dydhaw` for [mentioning this](https://www.reddit.com/r/rust/comments/1h0zcku/comment/lz7xox5/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button).
[^unsafe]: It's still possible to use unsafe code that violates the semantic restrictions of `Pin` to do that, though.
