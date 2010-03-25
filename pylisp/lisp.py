import sexp as parser
import inheritdict
import builtin
import specialforms
import info
import importer

import sys
sys.setrecursionlimit(100000) # It's lisp! It must recurse!

debug = 0

class Lisp(object):
    run_stdlib = True

    def __init__(self):
        bt = builtin.builtins.copy()
        bt.update(specialforms.specialforms)
        bt.update({"eval": lambda *args: self.run(args)})

        self.vars = inheritdict.idict(None, bt).push()

        self.macros = {}
        self.call_stack = [self]
        self._lispprint = lambda: "#main"
        self._catches = {}

        self.run(info.lib("basics"))
        if Lisp.run_stdlib:
            Lisp.run_stdlib = False
            self.run(info.lib("stdlib")) # Assuming no error
            Lisp.run_stdlib = True

        self.vars = self.vars.push()
        self.vars.stop = True

    def run(self, s, mult=True):
        if isinstance(s, str): s = parser.parse(s)
        if not mult: s = [s]
        sexps = map(self.preprocess, s)
        return map(self.eval, s)[-1] if s else None

    def preprocess(self, tree):
        self.preprocess_flag = True
        while self.preprocess_flag:
            self.preprocess_flag = False
            self.preprocess_(tree)
        if debug:
            builtin.print_(tree)
        return tree

    def preprocess_(self, tree):
        if not isinstance(tree, list) or len(tree) == 0 or tree[0] in ("'", "`"): return
        elif tree[0] == "set!::macro":
            name = self.eval(tree[1])
            fn = self.eval(tree[2])
            self.macros[name] = fn
            if callable(self.macros[name]):
                self.macros[name].__name__ = name
            self.preprocess_flag = True
            ret = self.macros[name]
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
                self.macros.update(mod.__dict__["#macros"])
                self.preprocess_flag = True
            tree[:] = []
        elif tree[0] == "block::macro":
            self.run(tree[1:])
            self.preprocess_flag = True
            tree[:] = []
        elif isinstance(tree[0], str) and tree[0] in self.macros:
            l = self.macros[tree[0]](*tree[1:])
            if not isinstance(l, list):
                l = ["'", l]
            tree[:] = l
            self.preprocess(tree)
            self.preprocess_flag = True

        for i in tree:
            self.preprocess_(i)

    def eval(self, tree):
        if debug > 1:
            print "Eval'ing::",
            builtin.print_(tree)

        if isinstance(tree, str):
            if tree in self.vars:
                return self.vars[tree]
            else:
                raise NameError("Lisp: Name `%s` does not exist" % tree)
        elif not isinstance(tree, list):
            return tree
        elif len(tree) == 0:
            return None
        
        func = self.eval(tree[0])

        try:
            if hasattr(func, "_fexpr") and func._fexpr == True:
                return func(self, *tree[1:])
            elif hasattr(func, "_specialform"):
                return func(self, *map(self.eval, tree[1:]))
            else:
                return func(*map(self.eval, tree[1:]))
        except specialforms.BeReturnedI, e:
            if len(self.call_stack) == e.args[0]:
                return e.args[1]
            else:
                raise

    def quasieval(self, tree):
        if debug > 1:
            print "Quasieval'ing::",
            builtin.print_(tree)

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
    f = importer.Finder(info.import_path, Lisp)
    sys.meta_path.append(f)
setup_loader()

