import parser
import inheritdict
import builtin
import info
import importer

import sys
sys.setrecursionlimit(1000)

class ReturnI(Exception): pass
class BeReturnedI(Exception): pass
            
def iftuple(s):
    if isinstance(s, str):
        return (s,)
    else:
        return tuple(s)

class Lisp(object):
    run_stdlib = True

    def __init__(self, debug=False):
        bt = builtin.builtins.copy()
        bt.update({"eval": self.eval, "atom?": self._atomp, "#import": self._import, "has": self._has, "#include": self._include})
        self.vars = inheritdict.idict(None, **bt).push()
        self.macros = builtin.macros
        self.call_stack = [self]
        self._lispprint = lambda: "#main"
        self._catches = {}
        self.debug = debug

        if Lisp.run_stdlib:
            Lisp.run_stdlib = False
            self.run(info.lib("stdlib"))
            Lisp.run_stdlib = True

        self.vars = self.vars.push()

    def run(self, s):
        global sexp

        if isinstance(s, str):
            sexps = parser.parse(s)
        else:
            sexps = s
        sexps = self.preprocess(sexps)

        out = None
        for expr in sexps:
            out = self.eval(expr)
        return out

    def preprocess(self, tree):
        import random
        c = random.randint(1, 1000)

        if self.debug:
            print c,
            builtin.print_(tree)

        self.preprocess_flag = True
        while self.preprocess_flag:
            self.preprocess_flag = False
            self.preprocess_(tree)
        
        if self.debug:
            print c,
            builtin.print_(tree)

        return tree

    def preprocess_(self, tree):
        if not isinstance(tree, list) or len(tree) == 0: return
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
        elif tree[0] in ("'", "`"):
            return
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
            map(self.run, tree[1:])
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

    def _return(self, arg=[]):
        raise ReturnI(arg)

    def _import(self, *args):
        args = list(args)
        modname = ".".join(args)
        __import__(modname)
        return sys.modules[modname]

    def _include(self, *args):
        args = list(args)
        modname = ".".join(args)
        __import__(modname)
        self.vars.dict.update(sys.modules[modname].__dict__)

    def _has(self, var, arg=None):
        if arg is None:
            return var in self.vars
        else:
            return hasattr(var, arg)

    def _atomp(self, var):
        return type(self.eval(var)) in map(type, [0L, 0, 0., ""])

    def _if(self, test, true, false=None):
        if self.eval(test):
            return self.eval(true)
        elif false:
            return self.eval(false)

    def _fn(self, sig, *body):
        if isinstance(body, tuple):
            body = list(body)
        if isinstance(sig, str):
            sig = [".", sig]
        if any(not isinstance(x, str) for x in sig):
            raise SyntaxError("Arguments to function must just be identifiers")
        
        if "." in sig:
            many_name = sig[sig.index(".") + 1]
            sig[sig.index("."):] = []
        else:
            many_name = None
        
        
        def llambda(*args):
            args = list(args)
            vars = dict(zip(sig, args))

            if many_name is not None:
                vars[many_name] = args[len(sig):]

            self.vars = inheritdict.idict(self.vars, llambda._vars).push(vars)
            self.call_stack.append(llambda)
            try:
                out = self.run(body)
                return out
            except ReturnI, e:
                return e.args[0]
            finally:
                self.call_stack.pop()
                self.vars = self.vars.pop().pop()

        llambda._vars = self.vars
        llambda._catches = {}
        llambda.__name__ = ""
        return llambda

    def _class(self, inheritfrom, *body):
        d = {}
        self.vars = inheritdict.idict(self.vars, d)

        try:
            self.eval(["block"] + list(body))
            
            if "__init__" in d:
                k = d["__init__"]
                def __init__(*args, **kwargs):
                    k(*args, **kwargs)
                d["__init__"] = __init__
            
            if "__div__" in d:
                d["__truediv__"] = d["__div__"]
        
            bases = map(self.eval, inheritfrom)
            return type("", tuple(bases), d)
        finally:
            self.vars = self.vars.pop()

    def _set(self, name, value):
        value = self.eval(value)
        if not isinstance(name, list):
            raise SyntaxError("What the hell are you trying to set?")
        elif name[0] == "'" and isinstance(name[1], str):
            self.vars[name[1]] = value
            if callable(value): value.__name__ = name[1]
        elif name[0] == "::":
            setattr(self.eval(["::", name[:-1]]), self.eval(name[-1]), self.eval(value))
        else:
            raise SyntaxError("What the hell are you trying to set?")

        return value

    def _block(self, *exprs):
        if exprs:
            return map(self.eval, exprs)[-1]

    def _handle(self, type, handler):
        type = iftuple(self.eval(type))
        handler = self.eval(handler)
    
        f = self.call_stack[-1]
        f._catches[type] = handler

    def _signal(self, type, *args):
        l = self.eval(type)
        type = iftuple(l)
        args = map(self.run, args)
        signal = builtin.signal(l, *args)

        for i, f in enumerate(reversed(self.call_stack)):
            ttype = type[:]
            while ttype and ttype not in f._catches:
                ttype = ttype[:-1]
            if ttype:
                break
        else:
            raise signal
        
        handler = f._catches[ttype]
        control = handler(signal)

        if len(control) == 1:
            control[1:] = [None]

        if control[0] == "return":
            raise ReturnI(control[1])
        elif control[0] == "ignore":
            return control[1]
        elif control[0] == "bubble":
            raise BeReturnedI(i, control[1])
        elif control[0] == "debug":
            import sys, traceback
            traceback.print_exc()
            sys.exit()
        elif control[0] == "exit":
            import sys
            if len(control) > 1:
                print control[1]
            sys.exit()
        else:
            raise SyntaxError("Received non-control-word return value from signal handler")


    builtindict = {"if": _if, "set!": _set,
        "fn": _fn, "block": _block, "#class": _class,
        "signal": _signal, "handle": _handle}

    def eval(self, tree):
        if isinstance(tree, str):
            if tree in self.vars:
                return self.vars[tree]
            else:
                raise NameError("Lisp: Name `%s` does not exist" % tree)
        elif not isinstance(tree, list):
            return tree
        elif len(tree) == 0:
            return None
        elif isinstance(tree[0], str) and tree[0] in self.builtindict:
            return self.builtindict[tree[0]](self, *tree[1:])
        elif tree[0] == "'":
            return tree[1]
        elif tree[0] == "`":
            return self.quasieval(tree[1])[0]
        else:
            tree2 = map(self.eval, tree)
            try:
                return tree2[0](*tree2[1:])
            except BeReturnedI, e:
                if len(self.call_stack) == e.args[0]:
                    return e.args[1]
                else:
                    raise

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
    f = importer.Finder(info.import_path, Lisp)
    sys.meta_path.append(f)
setup_loader()

