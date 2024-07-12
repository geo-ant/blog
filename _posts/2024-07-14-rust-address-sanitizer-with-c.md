---
layout: post
tags: rust c++ c sanitizers
#categories: []
date: 2024-07-14
#excerpt: ''
#image: 'BASEURL/assets/blog/img/.png'
#description:
#permalink:
title: 'Using Address Sanitizer for a C or C++ Library Linked to a Rust Executable'
#
#
# Make sure this image is correct !!!
og_image: cpp-asan-rust.png
#
#
# make sure comments are enabled
comments_id: 64
math: false
---

When using Rust, it's easy to forget about segfaults, buffer overflows, and related
memory safety bugs. Recently, I had a problem when I linked a C++ library to my Rust executable
and said library was producing segfaults (among other things). The way I decided to tackle the
problem, was to use Address Sanitizer (ASan). I'll summarize the procedure here in case anyone
else runs into the same problem and they might find this useful.

# Scenario

Our scenario is this: we have a C library whose functions we invoke from a Rust
executable via Rust's FFI. This example will work just as well if the library
is written in C++ and exposes its functions via `extern "C"` linkage. 

Let's assume that we have the source code of the C or C++ library and we are able
to rebuild it. Here, we'll use CMake for building, but the specific build system is
not important, as long as we can pass the correct compiler and linker flags.
Other options are available, this workflow has just
become a preference for me personally. Finally, I also assume that we are running on x86 Linux,
since I am not sure what the status of address sanitizer is on Windows and I am too
lazy to find out.

# The C Library Code

The code in this article contains everything you need to run this example. Thus,
we'll use some silly code for both the C and the Rust part, just enough to trigger
problems that we can examine with ASan.

```c
// lib.c
#include <stdint.h>
#include <stdlib.h>

// "private", only used internally
static uint32_t access_internal(uint32_t *pointer,
                                size_t index);

// the "public" function
uint32_t allocate_and_access(size_t const size,
                             size_t const index) {
  uint32_t* data = calloc(size, sizeof(uint32_t));
  uint32_t const value = access_internal(data, index);
  free(data);
  return value;
}

static uint32_t access_internal(uint32_t *const pointer,
                                size_t const index) {
  return pointer[index];
}
```

When compiled as a shared library, it will export the function `allocate_and_access`,
which allocates `size` number of `u32` integers on the heap and returns the
value at index `index`. If the index is within the range `[0,...,size-1]`, the
function will return the value `0`, because `calloc` initializes the
memory to zero. If `index` is outside of the range, that's an out of bounds memory access,
which produces undefined behavior. I have used an internal "private"[^static] function
that performs the actual access, just so that Address Sanitizer has more of a 
stack trace to report.

Before we see how to build the library with Address Sanitizer so that it plays
nicely with a Rust executale, let's take a look at the overall project structure and
the Rust code.

# The Rust Project

Our simple project is structured as follows:
```
.
|- build.rs
|- Cargo.toml
|- myclib
|   |- CMakeLists.txt
|   |- lib.c
|- src
    |- main.rs
```

It's just a bog standard Rust executable project that contains our C library
in a subdirectory. Our Rust executable calls the C function via the
[foreign function interface](https://doc.rust-lang.org/rust-by-example/std_misc/ffi.html)
and prints the result.

```rust 
// main.rs
extern "C" {
    fn allocate_and_access(size: usize, index: usize) -> u32;
}

fn main() {
    println!("Calling C function...");
    let retval = unsafe { allocate_and_access(10, 11) };
    println!("...returned: {}", retval)
}
```

We can see that the program will perform an out of bounds access when run like that.
In this case, it will likely print some random nonsense[^ub]. For completeness, let's
see what the `build.rs` file looks like, before we get into how to debug the program
with ASan.

```rust
//build.rs
fn main() {
    let dst = cmake::build("myclib");
    println!("cargo:rustc-link-search=native={}/lib", dst.display());
    println!("cargo:rustc-link-lib=dylib=myclib");
}
```

This has a build-dependency on the [cmake](https://crates.io/crates/cmake) crate, just
because that is how I like to build my C and C++ projects. Let's now look at the CMake
file for the C project, because that is where we pass the necessary
compiler and linker flags to build our library with Address Sanitizer enabled.

# Building Our C Project With (Static) Address Sanitizer

Enabling Address Sanitizer for our library is as easy as passing the correct
compiler and linker flags. However, if we just pass `-fsanitize=address`, we will
run into [this error](https://github.com/rust-lang/rust/issues/114127) when executing our program:

```shell
==82818==Your application is linked against incompatible ASan runtimes.
```

That's because, at the time of writing, rustc only bundles the static version
of the Address Sanitizer runtime. Thus, to use our C library with our Rust executable,
we have to make sure that we also link the library with the _static_ version
of the Address Sanitizer runtime. Here is how that looks in our simple `CMakeLists.txt` file:

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.10)
project(MyCProject C)
add_library(myclib SHARED lib.c)

# the flags to use ASan statically
target_compile_options(myclib PUBLIC 
 -fsanitize=address)
target_link_options(myclib PUBLIC
 -fsanitize=address 
 -static-libasan)

# needed for the cmake crate
install(TARGETS myclib
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)
```

We have now made sure that the static runtime of ASan gets linked to our library.

# Running the Executable With Address Sanitizer

At the time of writing, we need the _nightly_ rust compiler to use Address Sanitizer
in our programs. So we have to make sure that our project uses the nightly
toolchain, if it's not already doing that:

```shell
$ rustup override set nightly
```
This will make sure that the given project, and _only that_, uses the nightly
compiler, which allows us to pass the `-Z` family of flags. To run our program,
we essentially just `cargo run` it with some extra compiler flags:

```shell
$ RUSTFLAGS="-Z sanitizer=address" cargo run --target x86_64-unknown-linux-gnu
```

Note that we also have to specify the target explicitly[^target]. 

# Analyzing the Address Sanitizer Output

We'll now have a quick look at how to analyze the output of Address Sanitizer,
without going into great detail, because there are tons of tutorials on the web. 
But let's at least see how we can make use of the output. When we run our program
we get an output such as this:

```
Calling C function...
=================================================================
==10654==ERROR: AddressSanitizer: heap-buffer-overflow on address [...]
READ of size 4 at 0x50400000003c thread T0
    #0 0x78d074480247  (./target/debug/build/[...]/out/lib/libmyclib.so+0x1247) [...]
    #1 0x78d0744801d4  (./target/debug/build/[...]/out/lib/libmyclib.so+0x11d4) [...]
    #2 0x63b647f83a64  (./target/debug/asan-rust+0xeea64) (BuildId: c547f75d1a8b7697)
    #3 0x63b647f83e1a  (./target/debug/asan-rust+0xeee1a) (BuildId: c547f75d1a8b7697)
    #4 0x63b647f83c3d  (./target/debug/asan-rust+0xeec3d) (BuildId: c547f75d1a8b7697)
    #5 0x63b647f84084  (./target/debug/asan-rust+0xef084) (BuildId: c547f75d1a8b7697)
[...]
```

There's more useful output, but this truncated version should suffice. ASan tells
us that we have a buffer-overflow as expected. It also gives us a stack trace,
which can be very helpful in debugging how that buffer overflow was actually
triggered. The top of the stack trace shows us where the overflow happened.
There's just one problem: ASan just gives us raw offsets in our
binaries, such as `libmyclib.so+0x1247`. That means "the code at offset
`0x1247` of `libmyclib`", which is still not very human readable.
There are a couple of things we can do to about that. Let's see some of them.

## Using addr2line
We can use the GNU [addr2line](https://linux.die.net/man/1/addr2line)
tool to convert addresses in binaries into lines of source code. This, and all the other
things I'll mention below, requires that our library be compiled with debug
symbols enabled. We have implicitly done that because CMake defaults to the
debug build type, unless otherwise specified.

```shell
$ addr2line -f -p -e ./target/debug/build/[...]/out/lib/libmyclib.so 0x1247
access_internal at ./myclib/lib.c:20
```

The `addr2line` tool tells us the function name and the line in the source
code that produced the buffer overflow. Not surprisingly, this is exactly the line
`return pointer[index];` in the `access_internal` function. Doing it like that
surely works, but it can become tedious quickly.

## Using the Symbolizer

If we have [llvm installed](https://apt.llvm.org/), there is a tool called the
`llvm-symbolizer`. It might not be called exactly like that, e.g. for my particular installation
it's called `llvm-symbolizer-18`. We can tell ASan about it by using a dedicated environment
variable. Then, we use another dedicated environment variable to instruct ASan to
use it to prettify its output.

```shell
$ export ASAN_SYMBOLIZER_PATH=$(which llvm-symbolizer-18)
$ export ASAN_OPTIONS=symbolize=1
```

If we now run our program as above, the output is much easier to grasp:

```
Calling C function...
=================================================================
==13863==ERROR: AddressSanitizer: heap-buffer-overflow on address [...]
READ of size 4 at 0x50400000003c thread T0
    #0 0x70e4a4ca2247 in access_internal ./myclib/lib.c:20:17
    #1 0x70e4a4ca21d4 in allocate_and_access ./myclib/lib.c:12:26
    #2 0x5b2614b25d74 in asan_rust::main::h67804a126392dee0 ./src/main.rs:7:27
[...]
```

This was exactly the information that I needed to fix my particular problem. If the output of ASan
is particularly unwieldy, we can also [direct it into a file](https://github.com/google/sanitizers/wiki/AddressSanitizerFlags#run-time-flags)
using the `ASAN_OPTIONS` environment variable, or via piping the `stderr` output
to a file.

# Conclusion

ASan proved invaluable for me, because it helped me find and eventually fix a weird
out of bounds memory access, that was producing segfaults sometimes and hot
garbage at other times. I was really happy that the integration across languages
was pretty smooth, after figuring out I needed the static runtime. There is much
more we can do with ASan in Rust, for example it can also help us find some problems
in unsafe Rust code, a small --but important-- subset of what [miri](https://github.com/rust-lang/miri) does,
where ASan lets the program run much faster than miri.

# Further Reading

* [rust-san](https://github.com/japaric/rust-san): (almost) all the sanitizers for Rust.
* [Google's documentation](https://github.com/google/sanitizers/wiki/AddressSanitizer) for Address Sanitizer.

# Endnotes

[^static]: The correct term is _static_ or _internal_ linkage. In effect, the function cannot be called from outside the library (or even outside of this particular C File... _compilation unit_... damn you voice in my head!).
[^ub]: But we cannot rely on that. Accessing an invalid pointer is _undefined behavior_, which can mean any number of things.
[^target]: Though I have also seen it work without the explicit target, but better safe than sorry.
