---
layout: post
tags: rust generics design-patterns testing
#categories: []
date: 2025-06-15
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'A Tale of Testability: Sending Non-Send Types in Rust'
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

This is a story of testability, multithreading, and the age old question of
_how do we send a_ `!Send` _type in Rust_. I'll explore how (not) to do this,
while rambling on about how writing obsessively testable code leads to better design.
Hot takes incoming.

# Testability and Multithreading

Let's take a few steps back and set the scene: say we have a function that
spawns a thread. We'll keep it simple --trivial even-- to focus on the essentials.
Let's say that all this thread does, is play some audio[^trivial-example]. For a
first try, we could structure our code like so:

```rust
struct SystemAudio {/* ...*/}

impl SystemAudio {
    fn new(/* config */) -> Self {
        /*...*/
    }
    fn play_music(&self) {
        /* ...*/
    }
}

// ❓ how do we test this??
fn spawn_thread(audio: SystemAudio) {
    std::thread::spawn(move || {
        audio.play_music();
    });
}
```

To my mind, there's a problem with this code and it stems from the fact that
I am a huge nut for testability. I need to make sure that I can test the
behavior of that function. The least I want to do, is make sure that the
`play_music` function of the `audio` instance really gets called.

One great way to make all kinds of code testable is [dependency inversion](https://en.wikipedia.org/wiki/Dependency_inversion_principle),
which boils down to coding against interfaces rather than concrete types[^solid]. So
rather than passing in our imaginary `SystemAudio` instance directly, we'll
define a trait `Audio` to abstract over the behavior of the audio backend.
This allows us to mock the audio backend for testing. During testing, we can
pass in our mock to make sure that the correct behavior was indeed invoked. So
let's refactor our code:

```rust
trait Audio {
    fn play_music(&self);
}

struct SystemAudio {/* ...*/}

impl SystemAudio {
    fn new(/* config */) -> Self {
        /*...*/
    }
}

impl Audio for SystemAudio {
    fn play_music(&self) {
        /* ...*/
    }
}

// ⚡ this doesn't compile
fn spawn_thread<A>(audio: A)
    where A: Audio {
    std::thread::spawn(move || {
        audio.play_music();
    });
}
```

You probably already knew this wouldn't compile. The compiler will correctly
complain that `A` is neither `Send` nor `'static`, which is what we'd need
to move it into the thread. If we can further restrict `A` to be `Send` and
`'static`, that's a fine solution and that would be the end of this article.
But what if we _can't_? What if our production audio backend really does not
implement `Send`?

# How Do We `impl Send` for a Non-`Send` Type?

!!! TODO: THAT'S THE NEAT PART !!!

If we've written a type `T`, where the compiler doesn't automatically implement
`Send` but _we know it would be sound to do so_, we can of course [implement `Send`](https://doc.rust-lang.org/nomicon/send-and-sync.html)
manually and call it a day[^pointers]. However, what if the compiler doesn't implement
`Send` on our type for a good reason? Let's say we're using a field of foreign type
`U` that is itself not `Send`. We'd better assume that the authors of the type deliberately did not implement
`Send`. Thus, just overriding their decision and manually implementing `Send` on our
type might be unsound. So that's out of the question, unless we have a _very good_ reason
to believe it's sound.

## Using `Mutex<T>` and `Arc<Mutex<T>>`

Why don't we just wrap it in a `Mutex<T>`? Or an `Arc<Mutex<T>>` for good measure?
That usually helps with all kinds of multithreading-induced compile errors, right?
The unfortunate truth is that `Mutex<T>` is `Send` [if and only if](https://doc.rust-lang.org/std/sync/struct.Mutex.html#impl-Send-for-Mutex%3CT%3E)
`T` is `Send`, so sticking a non-`Send` type into a mutex won't make it `Send`.
[The same](https://doc.rust-lang.org/std/sync/struct.Arc.html#impl-Send-for-Arc%3CT,+A%3E)
is true for `Arc<T>` and thus for `Arc<Mutex<T>>`, so that won't help either[^mutex-sync].

## Interlude: Isn't There a Crate for That?

The short answer is: No, I don't think so, let's have a look on crates.io: 
* [`mutex-extra`](`https://crates.io/crates/mutex-extra`): aims to create a `Send`
  type from a non-`Send` type. Diplays a "my code is erroneous, don't use"
  warning. I guess we won't be using that then.
* [`send_cells`](https://crates.io/crates/send_cells): a pretty recent crate
  claiming to be an alternative to `fragile` (see below) and additionally
  offers unsafe interfaces.
* [`sendable`](https://crates.io/crates/sendable): I believe this crate is concerned
  with sharing resources, rather than moving values across threads. We might
  be able to use it for our purpose, but it would only give us runtime guarantees
  that we didn't do anything wrong.
* [`send-cell`](https://crates.io/crates/send-cell): deprecated in favor of
  `fragile`.
* [`fragile`](https://crates.io/crates/fragile): "wrap a value and provide a `Send` bound.
  Neither of the types permit access to the enclosed value unless the
  thread that wrapped the value is attempting to access it". That's the
  opposite of what we want.

Please tell me if I'm wrong about this: for fundamental reasons, I can't imagine a
crate existing that gives us `Send` wrappers for non-`Send` types without using
`unsafe` code that would be equivalent to implementing `Send` ourselves. We've
already ruled that out for good reason. 

# Why Even Test `spawn_thread`?

Yes, why even do that if the Rust compiler seems to make it hard? Even if we
generally agree on the value of testing, we might be tempted to refactor our
code like so:

```rust
fn spawn_thread() {
    std::thread::spawn(|| {
        let audio = SystemAudio::new(/*config*/);
        execute_thread(audio);
    });
}

fn execute_thread<A: Audio>(audio: A) {
    audio.play_music();
    /* and all other logic...*/
}
```

Now, we can write a nice test for `execute_thread`, since it depends
on an interface, rather than a concrete type. Isn't this basically just as
good as testing `spawn_thread`? After all, `spawn_tread` only calls
`execute_thread` with a `SystemAudio` instance, which we want to use in
production anyways. Call me crazy, but I'll argue this is not good enough.

To my mind, we should treat items under tests as black boxes as much as is
feasible. Testing `execute_thread` as a substitute for `spawn_thread` relies
on the knowledge that `spawn_thread` only calls `execute_thread` in a new
thread. But from a testing point of view, that's an implementation detail we
shouldn't care about. We should instead be interested in making sure that
`spawn_thread` does the right thing. This might seem overly pedantic, but
imagine someone else editing our `spawn_thread` and sticking some more logic
in there. I personally would want to have a test for `spawn_thread` that flags if something
unexpected happens, to catch errors higher up the chain. To my mind, this is
the most important thing. It's not about getting a couple lines more test coverage,
but it's about testing the behavior of the things that are actually used... at
_all_ levels of integration[^downstream-tests]. I'll go one further and will also
claim that putting in the effort to make `spawn_thread` testable leads to a better design.

# Advanced Dependency Inversion

Don't get me wrong, _if_ it's possible to restrict our type to be `Send + 'static`,
we should definitely do that and move it into the thread, like we initially
intended. We just have to come to terms with the fact that we simply _can't
do that_ in this scenario. To overcome this, we can take inspiration from
the previous section. What we did there, was to create the `audio` instance
in the thread itself, rather than move it into the thread from the outside.

Let's expand on this idea: rather than hardcode the creation of the `audio`
instance in the thread itself, we create an API to inject some _code to create
the instance for us_. This sounds more complicated than it is, and
there are many ways to do that[^constructor]. I like this one:

```rust
fn spawn_thread<F,A>(audio_constructor: F)
    where F: FnOnce()-> A + Send + 'static,
          A: Audio {
    std::thread::spawn(move || {
        let audio = audio_constructor();
        audio.play_music();
    });
}
```

Instead of passing in the `audio` instance itself, we now pass in a callable
that constructs the instance. The callable `F` itself is restricted on `Send + 'static`,
but `A` is _not_ restricted on either of these bounds. I've created a slighty
more involved [example on the playground](https://play.rust-lang.org/?version=nightly&mode=debug&edition=2021&gist=33e3b1f6629d93b946c221d2803029d4)
that illustrates the use. Here's what we can do now:

```rust
// passing a default system backend
// using a closure.
spawn_thread(||SystemAudio::default());
// a mocking backend 
spawn_thread(||MockAudio);
// passing in a configuratio to the
// closure
let config = AudioConfiguration {device: 123, volume: 0.5}; 
spawn_thread(move ||SystemAudio::with_config(config));
```

Using the new API like this is almost as simple as passing in
the instance, and it makes `spawn_thread` completely testable.
We just have to add `||` or `move ||`. One problem we have to deal with
is constructor failure, meaning the constructor function might
return a `Result<A,E>` rather than an `A` directly. We have to make the
thread communicate the error to the outside. However, that problem isn't unique
to this approach, so I'll leave it at that.

# Why It's Better

In this last section, let me defend my claim that this design is better,
_not only_ because it makes `spawn_thread` testable. This design also decouples
the implementation of `spawn_thread` from the actual audio backend again, by
using dependency inversion. This means that we can use different audio backends
either at runtime by refactoring to `dyn Audio`, or at compile time e.g. for
different operating systems or hardware.

I believe the benefits of this approach completely justify the additional complexity...
even if this starts looking a bit like a factory pattern. It's no
[`AbstractFactoryBean<T>`](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/beans/factory/config/AbstractFactoryBean.html), though.

# Endnotes
[^trivial-example]: Since this example is so trivial, there are other ways to go about testing it. But I want to focus on the bare essentials of the problem and I ask you to bear with me, dear reader.
[^mutex-sync]: Matters would be different if we were interested in implementing `Send` _and_ `Sync` on a type `T` that _only_ implements `Send`. In this case, reachig for `Mutex<T>` is a solution.
[^pointers]: This can happen if our type contains a raw pointer field.
[^downstream-tests]: Don't get me wrong: you shouldn personally would only test the highest, most integrated, levels of our code. It's good to test `execute_thread` in our example. But, to my mind, that should not absolve us from having to test `spawn_thread` as well.
[^constructor]: We could also extend the `Audio` trait to provide a constructor. I don't like this quite as much because different implementors of the `Audio` trait might need different parameters for callable `F` .
[^solid]: Say what you will about SOLID, but dependency inversion is the hill I am willing to die on.
