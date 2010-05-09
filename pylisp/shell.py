#!/usr/bin/env python

import lisp
import info
import builtin
try:
    import readline
except ImportError:
    pass #Probably on Windows
import os, sys
import cProfile, pstats

profile = False

# Set up the interpreter
l = lisp.Lisp()

def handle_error(err):
    if len(l.call_stack) > 1:
        print "Call stack:"
        for i in l.call_stack:
            print "\t%s" % builtin.str_(i)
    print err
    return ["bubble"]
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
        if profile:
            v = []
            def f():
                v.append(l.run(s))
            cProfile.runctx("f()", globals(), locals(), "/tmp/profile.log")
            pstats.Stats("/tmp/profile.log").strip_dirs().sort_stats("time").print_stats(20)
            v = v.pop()
        else:
            v = l.run(s)
    except lisp.specialforms.BeReturnedI, e:
        pass
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
            sexps = list(lisp.parser.parse(s))
        except IndexError:
            s += raw_input("... > ") + "\n"
        except SyntaxError as e:
            print "(error standard syntax): " + str(e)
            return input()
        else:
            break
    return s

def shell():
    while 1:
        try:
            s = input()
            v = run(s, silent=False)
        except (SystemExit, EOFError, KeyboardInterrupt):
            return

def main():
    global profile
    import sys
    import os
    args = sys.argv

    if "-d" in args:
        i = args.index("-d")
        if len(args) > i + 1:
            lisp.debug = int(args[i+1])
            args = args[:i] + args[i+2:]
        else:
            lisp.debug = 1
            args = args[:-1]

    if "-p" in args:
        i = args.index("-p")
        profile = True
        args = args[:i] + args[i+1:]

    import compiler
    compiler.debug = lisp.debug
    
    if len(args) > 1:
        for f in args[1:]:
            l.file = f
            run(open(f).read())
    else:
        shell()

if __name__ == "__main__":
    main()
