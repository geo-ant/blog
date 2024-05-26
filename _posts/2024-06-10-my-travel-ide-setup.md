---
layout: post
tags: ide android tools helix
#categories: []
date: 2024-06-10
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Coding Wherever: My Fully-Featured Travel Dev Setup from Sea Level to 40,000 feet'
#
#
# Make sure this image is correct !!!
og_image: sea-air.png
#
#
# make sure comments are enabled
comments_id: 61
math: false
---

What do you do if you want to code using an (almost) fully featured IDE setup, but
you're up 40,000 feet in the air, without internet? And you don't want to pay for
business class[^dont-want-to]? I'll show you what I did and I'm definitely
interested in feedback and other solutions to this problem.

# tl;dr

It's just helix, tmux and some language servers running via termux on an Android
tablet with a bluetooth keyboard.

# Overview

<figure>
 <img src="/blog/images/travel-coding/sea-air.png" alt="travel setup in action" style="width:100%">
 <figcaption>Figure 1. Action shots of my trusty (and dusty) tablet at sea level and in front of an airplane window 40,000 feet above the Atlantic.</figcaption>
</figure>

As you can see, my travel setup demonstrably works from sea level up to at least 40,000 feet.
I'm pretty sure it would work even higher, and if some billionaire wants to take me up to space
I'm up for it ;) Anyways... my setup features syntax highlighting, code completion,
diagnostics, quick actions, code navigation, and --of course-- compiling and executing my code.
And yes: this text was also written on it during a vacation, but I used my PC
back home for editing the images.

## A Brief History

The first step that I inadvertently took towards this setup was trying to set up VsCode on my 
tablet a couple of years ago. At the time, I did not find any guides, though today
[they exist](https://www.codewithharry.com/blogpost/install-vs-code-in-android/). Maybe
they did at the time and I just didn't look hard enough. Whatever the case may be,
I ended up going down a very different rabbit hole, and by now I use basically the same
setup at work, at home, or when travelling. I think it's a testament to the inherent
power of the software components involved. All of them are open source and none of
them are my projects.

# How It Works

If you read the tl;dr, you saw that there's nothing magical about my setup, just
a few off-the-shelf open source products working together. My hardware is an
Android tablet and I use a small bluetooth keyboard for input. There's no mouse,
because I rarely need one.

## The Terminal - Termux

The software stack rests on the excellent [termux](https://termux.dev/en/)
app, which is a terminal emulator that acts almost like a full linux environment. You
can download a lot of essential software through its package manager, such as compilers,
git, and also the editor I use.

## The Editor - Helix

As my code editor I use [helix](https://helix-editor.com/), which is a modal, terminal-based
source code editor like vim or emacs. In a previous iteration I used [neovim](https://neovim.io/),
which is also excellent and can make some steps of this setup even easier[^lsps-neovim].
I just switched over to helix as a matter of personal preference.

To me, the most important thing is having an editor that is keyboard-first, because
it saves me from using a mouse or my fingers on the screen. Plus, the way that
helix or neovim deal with screen real estate is great. There is no unneccessary clutter,
just the code, which is all the more valuable on a limited tablet display[^sidebar]. 
Helix also has great LSP-integration which allows it to provide the IDE goodness 
we've come to expect and love, such as code completion, navigation, diagnostics and so on.
I'll get back to this in more detail below.

## The Multiplexer - Tmux

<figure>
 <img src="/blog/images/travel-coding/tmux-helix.jpg" alt="travel setup in action" style="width:100%">
 <figcaption>Figure 2. The terminal multiplexer allows me to quickly open (and close) terminal panes as background tabs or even in a new split.</figcaption>
</figure>

The third pillar of my setup is [tmux](https://github.com/tmux/tmux/wiki), which
is a terminal multiplexer that allows me (among other things) to add panes to my terminal
either in "split screen" mode or in different "tabs". That's very helpful when
coding because helix has no built-in support for executing binaries or tests.
This might seem like a limitation at first, but it has become a feature for me
in the spirit of "do one thing well" and the integration with tmux is seamless. 
I usually have two tabs open where I use one for editing in helix and the other
one for git operations and running my binary or test suite. If I need to see code
and output together, I open a vertical split and close it as soon as I don't need it
anymore, to save valuable screen real estate. 

Termux, by default, displays some extra keys as a touch keyboard on screen that
aren't really useful when using a bluetooth keyboard. I suggest to get rid of them as
described  [here](https://android.stackexchange.com/questions/241180/remove-termuxs-extra-keys).

# Setting It Up

To get a nice development experience for a particular language with helix, we 
have to set up the compilers (and/or runtimes) and the language server for it. 
The language servers are extra programs that helix can run in the background. Those
give us the desired IDE functionalities such as code completion, navigation,
and diagnostics. However, we have to install them on our system for helix to 
be able to find them, so in the following sections I'll describe what 
I did for C++, Rust, and Python. But first, we need to install helix and tmux:

```shell
$ pkg update
$ pkg install -y tmux helix
```

## C++

To install the necessary toolchains and the language server (clangd),
use the following command:

```shell
$ pkg update
$ pkg install -y clang clangd llvm cmake ninja
```

You might have to restart termux. To verify that the C++ integration of helix
works, you can run `hx --health cpp` and you should see that everything (except
for debug adapters, more on that later) is marked as okay.

One thing I always do in my C++ projects, at least for the ones where
I have the freedom to decide for cmake as a build system, is to add the following lines
to my top-level `CMakeLists.txt`:

```cmake
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
file(CREATE_LINK
  "${CMAKE_BINARY_DIR}/compile_commands.json"
  "${CMAKE_SOURCE_DIR}/compile_commands.json"
  SYMBOLIC
)
```

This makes cmake emit a `compile_commands.json` file that the clangd language
server can use to parse nontrivial dependencies and project structures. It also
symlinks it into a directory where clangd will look for it.

## Rust 

First install the rust compiler and toolchain (including cargo), as well as the
language server using: 

```shell
$ pkg update
$ pkg install -y rust rust-analyzer
```

Now if you check `hx --health rust`, you should see everything (again, except for
the debug adapter, see below) marked as okay.

## Python

The bare bones python setup is also pretty simple, but I had some trouble installing
popular numerics packages numpy and scipy. It's easy once you know how, so I'll mention
it here as well.

```shell
$ pkg update
$ pkg install -y python
```

To install the language server for helix we can use `pip`:

```shell
$ pip install python-lsp-server
```

The important thing here is to install `python-lsp-server` and not the similarly
named `python-language-server`, which cost me an hour of my life to debug. If you
want to install numpy follow [these instructions](https://github.com/termux/termux-packages/discussions/19126),
while installing scipy is best done via termux' package manager using
`pkg install python-scipy`.

# Personalization

These are the essentials of the setup I use and I'll leave it at that for now. One thing
I like about it, is that it is very personalizeable. Take what you like from it and
change what you don't like. If you are looking for a way to manage your configuration
across systems, I can recommend [yadm](https://yadm.io/), which is available as
a termux package as well.

# Problems and Caveats

While I am very happy with this setup, there are some things that I did not yet
get to work or that are otherwise worth mentioning here.

Firstly, I did not get debugging working for Rust and C++. Unfortunately
helix' debugging support so far isn't great anyways, but I could not even get the required
debug adapter installed on my system (`lldb-vscode`). I'm grateful for hints.

Another program that I dearly miss is `perf`. Termux does not have it packaged and it
would be cool to do some performance measurements. I saw peope 
[on reddit](https://www.reddit.com/r/termux/comments/1c333l3/has_someone_gotten_perf_working/)
recommending to use llvm's profiling instrumentation capabilities. Sadly, I did not get it to do
what I wanted, which is to give me page faults and some other `perf` metrics like
instructions retired, cache misses, and so on. Help appreciated.

Thirdly, and this might be a personal spleen, I wasn't yet able to remap CapsLock
to Ctrl. There are key remapping tools for Android out there, but I could not yet get one
working for me. Leave a comment if you know.

The last thing that should be mentioned is that Android tablets typically use
Arm processors. That means if you (or a library that you depend on) use x86 instrinsics,
they won't work. Depending how you look at it, it can also be pretty cool
to have easy access to an Arm processor. Most of the time you won't notice anyways.

One problem I never had was performance. Granted, I don't use my travel setup
for huge projects, but I have recently developed and shipped a new version of my Rust [nonlinear regresssion
library](https://crates.io/crates/varpro) with it.

# Final Words

So that was it. None of this is rocket-science, but I'm still very happy with
my setup. Let me know what you think. Help, criticism, and any other feedback is 
welcome. Just leave a comment below.

# Endnotes

[^dont-want-to]: Let's just pretend that I _don't want_ to pay for business class, not that I _can't_...
[^lsps-neovim]: For example, if you use the mason plugin, downloading an LSP is super easy, barely an inconvenience.
[^sidebar]: I remember missing the project navigation bar when I switched over from CLion and VsCode to neovim. Two weeks in I couldn't remember why I ever missed it and just appreciated the extra screen real estate. It's hard to imagine, but trust me, there are much better alternatives. Such as having fuzzy file finders pop up on demand, rather than having the project navigation, the menu bar etc. take up so much screen.
