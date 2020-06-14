# Overview

<div align="center">
<img src="/assets/cavy_small.png" width=250 alt="Cavy logo: a capybara with an orange on its head."></img>
</div>


Cavy is an imperative programming language for quantum computers with
semicolon-and-curly-brace syntax. It's designed to be accessible to everyday
programmers, without sacrificing correctness: "as simple as possible, but no
simpler." It uses a internal intermediate representation (IR) to generate code
in multiple low-level languages, including QASM and Cirq. You can run it on real
hardware, or in a simulator, and execute it from within Python. Oh, and it has a
REPL, too, that works with real hardware!

This is not the only quantum programming language out there. Both academic and
corporate researchers have written their own. I'm just a student who did this
for fun, and make no claims to extreme originality in any of Cavy's
components--but I do think that the whole package is something pretty special.
For the most part, the existing options are a good deal harder to use for
beginners--sometimes not being at all abstracted from the quantum circuit
model--and either _(a)_ exist as DSLs embedded in some metalanguage (_e.g._ the
fantastic Quipper, which did a lot to inspire Cavy), or _(b)_ are actually
libraries. However, the REPL environment for interacting with a live system is
(to the best of my knowledge: send me a reference if I'm wrong!) a first.

This version of Cavy is written in Python for the sake of easy integration with
existing scientific computing tools and packages. I'd like to rewrite it in Rust
(or Idris 2!) for that language's support for affine types. There are also
performance reasons for a rewrite: I'd like the compiler to do more optimization
on its own, rather than relying on similarly-slow (but great!) packages like
Cirq. I do not expect that Cavy will ever become self-hosting. ;)

**All the examples and description below are written as though the
implementation were complete, which it is not. Only some of these things
actually work. For the time being, see the /tests directory for essentially all
the supported behaviors.**

# Examples
Cavy is a small language, so we can get the gist of most of it by looking at
some quite simple examples.

## Quantum random number generation
```cavy
q <- qubit();    // allocate one qubit
p <- split(q);   // Split the wavefunction into two branches with equal weight.
                 // (This is a quantum logic gate known as a "Hadamard.")
r <- !p;
print r;
```

## Quantum interference

```cavy
q <- split(split(qalloc()));
c <- !q[0];
print c;
```

If acting on a qubit with `split` were like flipping a coin, This program's
trace would be a stream of random bits, just like the previous program. But it's
not. The output is always `0`! On the second `split`, both the |0⟩ and
|1⟩ branches split in turn:

              |0⟩
             /   \
            /     \
           /       \
          /         \
        |0⟩    +    |1⟩
        / \         / \
       /   \       /   \
     |0⟩ + |1⟩ + |0⟩ - |1⟩

The laws of quantum mechanics dictate that there _must_ be a minus sign, causing
_interference_ between branches of the wavefunction, and annihilating the weight
on |1⟩. Every call to `split` really _does_ split the wavefunction on the
current branch, but the value-dependent signs cause some branches to be
annihilated: this is quantum interference, the fundamental property of quantum
mechanics from which all the other "weirdness" follows.

## Entanglement generation
We can create an entangled pair like this:

```cavy
q <- qalloc(2);       // Allocate two qubits in their initial states, notionally |0⟩|0⟩

q[0] <- split(q[0]);  // our little register is now in the state |0⟩|0⟩ + |1⟩|0⟩.

if q[0] {             // On the branch where q[0] is |1⟩...
    q[1] <- ~q[1];    // Invert q[1].
}                     // Now we have a Bell pair |0⟩|0⟩ + |1⟩|1⟩.

c <- !q;              // Read out the register!
print c[0];           // Write to stdout.
print c[1];
```

This program's trace will be either `0\n0` `1\n1`.

The behavior of `qalloc` _may_ be hardware-dependent. On my hardware, and in
most simulator backends, it will initialize the qubits to (approximately) |0⟩.
But, like C's `malloc`, anything **could** be in those qubits! As you'll see
below, there is _no_ equivalent to `calloc` that guarantees zero initialization.

We can also make _large_ entangled states:

```cavy
n <- 128;
q <- qalloc(n);       // classical numbers can be used...
q[0] <- split(q[0]);
for i in 1..n {       // ...more than once.
  if q[0] {
      q[i] <- ~q[i];
  }
}

c <- !q;              // Read out the register!
print c[0];           // Write to stdout.
print c[1];
```

<!--
## Grover's algorithm

This is where we'll see our first genuine asymptotic quantum speedup (only a
quadratic one, but a speedup nonetheless!).

Suppose we have a subroutine

```cavy
mem <- qalloc(n);

```
-->

# Installation

## On your laptop
Cavy has no compulsory external dependencies besides `pytest` for testing. You
can simply install `cirq` if you would like to use Cirq as a backend.

## For your quantum computing infrastructure
Please email `cavy` dash `lang` dash `support` at `mit` dot `edu`.

# Programming Cavy

Cavy is a very simple language, having only four primitive types: natural
numbers, booleans, quantum booleans, and arrays. There are no type annotations:
all types are inferred.

## Linear types

This should be familiar to Rust programmers, since it's exactly the _move
semantics_ of non-`Clone`/`Copy` types.

This is why I've chosen the `<-` syntax for assignment: it somehow makes
you think of _moving_ a value in a way that the `=` sign doesn't.

## Measurement: the `!` operator.

So far, I've written quantum states in the
[Dirac notation](https://en.wikipedia.org/wiki/Bra%E2%80%93ket_notation).

Values |ψ⟩ inside a little (brac)"ket" represent quantum states are
distinguished in the following ways:

* They cannot be accessed directly.
* Their concrete value is _literally_ indeterminate.

To convert a value inside a ket to an ordinary value, we must unwrap it by
"measuring" the quantum state. Cavy, breaking with tradition, reserves the `!`
operator to do this (this choice comes from Selinger and Valiron's [Quantum
Lambda Calculus](https://www.mscs.dal.ca/~selinger/papers/qlambdabook.pdf).
Selinger is the author of Quipper, a more mature quantum programming language
embedded in Haskell.)

## Calling Cavy from Python

```python
import pycavy
pycavy.backend = 'bf2'

def qrandom():
    prog = pycavy.compile(""" 
        print !split(qubit());
    """)
    output = prog.run()
    return output[0]
```

## The REPL environment

Cavy's real knockout feature is its REPL. Here's the same example from above, run
at a command line! By executing quantum programs lazily, we can create an illusion
of interactive programming

```
$ cavy

Welcome to the alpha version of this repl and language.
We hope that you enjoy your stay.
You can type ':q' to quit, and ':h' for help.

ψ⟩ 4 * 3             // calculator stuff
12
ψ⟩ q <- qubit()      // quantum stuff: execution is deferred until...
ψ⟩ q <- split(q) 
ψ⟩ r <- !q           // ...NOW!
ψ⟩ print r
1
ψ⟩ r + 4             // Now it's just a cvalue
5
ψ⟩ :q
Thanks for hacking with us!
```

# "Missing" features
There are a lot lot of features I'd like to incorporate into Cavy which are
currently unimplemented. Each of them is missing for a reason. Often, that
reason is "hardware limitations." Since Cavy is a real language intended to run
on real devices, features that we can't really use are of lower priority.

### QRAM
In the examples above, we call `qalloc` to acquire a reference to some memory,
which is indexed by an integer.

### Freeing memory
Up at the top, I showed you how to allocate qubits.

### Feedback
It's currently impossible for qubit operations to depend on classical values
that cannot be determined at compile time. This is due to the technical
challenge of fast feedback--within the qubit coherence time--between a classical
computer and a quantum coprocessor. The difficulty of doing this is lower in
trapped-ion systems, which enjoy rather long coherence times, but as I don't
work with these systems, feedback has taken a back seat.

The other reason for its absence is that the my compile targets don't support
it. Only a few labs actually do this in-house, and they generally don't run
programs defined in QASM or Cirq when they do.

### Random circuits
There are interesting tricks you can play if you're allowed to apply quantum
gates stochastically. There's no reason not to include this feature, and I
probably will in a future version.

# Thanks
I'm no programming languages expert, so I had to learn how to do this by first
emulating others. In particular, I want to acknowledge Bob Nystrom, whose book
[Crafting Interpreters](https://craftinginterpreters.com/) I used as a guide in
the early stages. Cavy's surface syntax is not quite the same as its _Lox_
language, and--more saliently--the semantics of quantum operations in Cavy is
totally foreign to it. However, much of the language's lexing and parsing
backbone comes _straight_ from this book, down to the names and structure of
many functions. I _highly_ recommend reading this book if you want to learn how
to write a practical programming language, and to give Bob money for it.

# Contributing
If you discover a bug, please open an issue and/or email `cavy` dash `lang` dash
`support` at `mit` dot `edu`.
