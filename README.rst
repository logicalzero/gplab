gplab README
============


gplab is (or will be) a framework for experimenting with genetic programming. Central to the project is a simple stack-based programming language called SCHLEP. SCHLEP was designed specifically for use in genetic programming; any string of bits is a valid, functioning program. 


Currently, only the SCHLEP language and machine have been implemented.




What is Genetic Programming?
----------------------------


*Genetic programming* attempts to solve a problem by creating random programs, evaluating how close they come to solving the problem (their *fitness*), and then 'cross-breeding' the most successful programs to create the next generation. Over time, the resulting programs should produce results closer to the intended goal.



The Language: SCHLEP
--------------------


gplab evolves programs written in its own simple language: SCHLEP (Stack Constructing High-level Language for Evolving Programs). SCHLEP is conceptually similar to Forth, but has a much simpler syntax.


There are four types of instructions in a SCHLEP program:


* **Literals:** These are not really 'instructions' per se, but are actual numbers that get pushed verbatim onto the stack.
* **Operators:** Functions that do something, typically adding, removing, or changing data on the stack.
* **Conditionals:** These are Boolean logical operations. If the condition is true, the interpreter continues on to the next instruction. If false, the interpreter jumps over the next branch of code and continues from there. There are two types of conditional: regular conditionals and loops. Loops return to the conditional after completing a branch of code. By convention, the names of regular conditionals start with ``'if'``, and loops start with either ``'while'`` or ``'until'``. 
* **Terminators:** A subset of operator that marks the end of a branch of code. By default, there is only one: ``end``. In general, these are only markers and have no effect on the code. A well-formed program will have (*number of conditionals*)+1 terminators (one for each conditional, one for the program as a whole), but a program with more or fewer terminators is still functional.




History
-------


gplab was a project I originally started back in school a long, long ago. After many years, I decided to return to work on it. The original code (in Common Lisp) is long gone, so I rewrote it from scratch as a first foray into a large Python project. This Python implementation then languished for a couple of years, during which time I began using Python much more. Much of the old, poorly-designed code has been refactored, but some bits of ugliness persist. 
