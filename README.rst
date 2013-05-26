==============================
Pylisp, a lisp for pythonistas
==============================

A small lisp written in Python. The goals are not
to implement any specific lisp dialect. That said,
aims are to be as Scheme-like as possible,
except with Common-Lisp style macros, and without
(so far) continuations. The largest overarching goal,
however, is to be as compatible as possible with
Python.

Usage
-----

One can call up a pylisp interpreter simply by running
the command ``pylisp``, and files can be passed as
arguments, which will be run.

One can also use ``import pylisp`` in a standard python
program. This will enable the importation of lisp files
as python modules. For example, one could create a file
called ``module.lsp``::

    (def testfunc (x y)
      (+ x y 7))

and a python file ``test.py``::

    import pylisp
    import module

    assert module.testfunc(7, 4) == 18

Language Features
-----------------

More can be found in the ``docs`` subdirectory, but in
short, pylisp includes almost-common-lisp-style
conditions/handlers, standard common-lisp-style macros,
functions and objects built off of the Python model,
and a package/module system identical to Python's.
