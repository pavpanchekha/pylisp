#!/usr/bin/env python

import lisp
import info
import builtin
try:
    import readline
except ImportError:
    pass #Probably on Windows
import os, sys

# Set up the interpreter
l = lisp.Lisp()

def handle_error(err):
    print "Call stack:"
    for i in l.call_stack:
        print "\t%s" % builtin.str_(i)
    print "Error:", err
    return ["exit"]
l.call_stack[0]._catches[("error",)] = handle_error

warn_cache = dict()
def handle_warning(err):
    e = str(err)

    if warn_cache.get(e, 0) < 5:
        print "In %s: %s" % (
                builtin.str_(l.call_stack[-1]),
                str(err))
    elif warn_cache.get(e, 0) == 5:
        print "Further %s warnings suppressed" % e
    warn_cache[e] = warn_cache.get(e, 0) + 1
    return ["ignore"]
l.call_stack[0]._catches[("warning",)] = handle_warning

def run(s, silent=True):
    import traceback
    
    try:
        v = l.run(s)
    except Exception, e:
        traceback.print_exc()
    else:
        if v is not None and not silent:
            builtin.print_(v)
        return v

def input():
    s = raw_input("lisp> ") + "\n"

    while True:
        try:
            sexps = lisp.parser.parse(s)
        except IndexError:
            s += raw_input("... > ") + "\n"
        else:
            break
    return s

def shell():
    while 1:
        try:
            s = input()
        except (SystemExit, EOFError, KeyboardInterrupt):
            return
        v = run(s, silent=False)

def main():
    import sys
    import os
    args = sys.argv

    if "-d" in args:
        l.debug = True
        i = args.index("-d")
        args = args[:i] + args[i+1:]
    else:
        l.debug = False
    
    if len(args) > 1:
        for f in args[1:]:
            run(open(f).read())
    else:
        shell()

if __name__ == "__main__":
    main()
