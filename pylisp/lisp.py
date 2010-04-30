import sexp as parser
import inheritdict
import builtin
import specialforms
import info
import importer

import sys
sys.setrecursionlimit(100000) # It's lisp! It must recurse!

debug = -1

def debugging(name, level=2):
    def decorator(f):
        def func(self, tree):
            if debug >= level:
                print name+"::", tree
            ret = f(self, tree)
            if debug >= level:
                print "->", ret
            return ret
        func._orig = f
        return func
    return decorator

macros = {}

class Lisp(object):
    run_stdlib = True

    def __init__(self):
        bt = builtin.builtins.copy()
        bt.update(specialforms.specialforms)
        bt.update({"eval": lambda *args: self.run(args), "#intp": self})

        self.vars = inheritdict.idict(None, bt).push()

        self.file = None
        self.macros = macros
        self.call_stack = [self]
        self._lispprint = lambda: "#main"
        self._catches = {}

        self.run(info.lib("basics"))
        if Lisp.run_stdlib:
            Lisp.run_stdlib = False
            self.run(info.lib("stdlib")) # Assuming no error
            Lisp.run_stdlib = True

        if debug > 0:
            print "StdLib:: Standard library loaded"

        self.vars.stop = True
        self.vars = self.vars.push()

    def run(self, s, mult=True):
        global debug
        if debug == -1:
            Lisp.preprocess_ = self.preprocess_._orig
            Lisp.eval = self.eval._orig
            Lisp.quasieval = self.quasieval._orig
            debug = -2
        if isinstance(s, str): s = parser.parse(s)
        if not mult: s = [s]
        return map(lambda x: self.eval(self.preprocess(x)), s)[-1] if s else None

    def preprocess(self, tree):
        self.preprocess_flag = True
        while self.preprocess_flag:
            self.preprocess_flag = False
            self.preprocess_(tree)
        return tree

    @debugging("Preprocess", 2)
    def preprocess_(self, tree):
        if not isinstance(tree, list) or len(tree) == 0 or tree[0] in ("'", "`"): return
        elif tree[0] == "set!::macro":
            name = self.eval(tree[1])
            fn = self.eval(tree[2])
            macros[name] = fn
            macros[name].__name__ = name
            self.preprocess_flag = True
            ret = macros[name]
            tree[:] = []
            return ret
        elif tree[0] == "#import::macro":
            modname = ".".join(map(self.eval, tree[1:]))
            importer.preprocess_only = True
            try:
                __import__(modname)
            finally:
                importer.preprocess_only = False
            mod = sys.modules[modname]
            if "#macros" in mod.__dict__:
                macros.update(mod.__dict__["#macros"])
                self.preprocess_flag = True
            tree[:] = []
        elif tree[0] == "block::macro":
            self.run(tree[1:])
            self.preprocess_flag = True
            tree[:] = []
        elif isinstance(tree[0], str) and tree[0] in macros:
            l = macros[tree[0]](*tree[1:])
            if not isinstance(l, list):
                l = ["'", l]
            tree[:] = l
            self.preprocess(tree)
            self.preprocess_flag = True

        for i in tree:
            self.preprocess_(i)

    @debugging("Evaluating", 1)
    def eval(self, tree):
        try:
            return self.vars[tree]
        except TypeError:
            pass
        except KeyError:
            if isinstance(tree, str):
                raise NameError("Lisp: Name `%s` does not exist" % tree)

        if not isinstance(tree, list):
            return tree
        elif len(tree) == 0:
            return None
        
        func = self.eval(tree[0])

        try:
            if hasattr(func, "_fexpr") and func._fexpr == True:
                assert "." not in tree, "Cannot apply `%s` to arguments; `%s` is a special form" % (func, func)
                return func(self, *tree[1:])
            
            args = []
            kwargs = {}
            expect_star = False
            for arg in tree[1:]:
                if isinstance(arg, list) and len(arg) > 0 and arg[0] == "#:":
                    if not isinstance(arg[1][0], str):
                        raise SyntaxError("First element of keyword must be identifier")
                    else:
                        if arg == ".":
                            kwargs.update(self.eval(arg[1][1]))
                        else:
                            kwargs[arg[1][0]] = self.eval(arg[1][1])
                elif arg == ".":
                    expect_star = True
                else:
                    c = self.eval(arg)
                    if expect_star: args += c
                    else: args.append(c)
                    expect_star = False

            if hasattr(func, "_specialform"):
                return func(self, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        except specialforms.BeReturnedI, e:
            if len(self.call_stack) == e.args[0]:
                return e.args[1]
            else:
                raise

    @debugging("Quasi-eval", 2)
    def quasieval(self, tree):
        if not isinstance(tree, list) or len(tree) == 0:
            return [tree]
        elif tree[0] == ",":
            c = [self.run([tree[1]])]
            return c
        elif tree[0] == ",@":
            return self.run([tree[1]])
        else:
            return [sum(map(self.quasieval, tree), [])]

def setup_loader():
    sys.path.append(info.lib_folder)
    f = importer.Finder(Lisp)
    sys.meta_path.append(f)
setup_loader()

