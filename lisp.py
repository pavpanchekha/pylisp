import sexp
import inheritdict
import builtin

class ReturnI(Exception): pass
class BeReturnedI(Exception): pass
            
def iftuple(s):
    if isinstance(s, str):
        return (s,)
    else:
        return tuple(s)

# Known strange bugs: (while) needs to be expanded
# once, and then it will work fine...

class Lisp(object):
    def __init__(self, debug=False):
        self.vars = inheritdict.idict(None, **builtin.builtins)
        self.macros = builtin.macros
        self.call_stack = [self]
        self._catches = {}
        self.debug = debug

    def run(self, s):
        global sexp

        if isinstance(s, str):
            sexps = sexp.parse(s)
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
            self.macros[tree[1]] = self.eval(tree[2])
            if callable(self.macros[tree[1]]):
                self.macros[tree[1]].__name__ = tree[1]
            self.preprocess_flag = True
            ret = self.macros[tree[1]]
            tree[:] = []
            return ret
        elif tree[0] in ("'", "`"):
            return
        elif isinstance(tree[0], str) and tree[0] in self.macros:
            l = self.macros[tree[0]](*tree[1:])
            if not isinstance(l, list):
                l = ["'", l]
            tree[:] = l
            self.preprocess(tree)
            self.preprocess_flag = True

        for i in tree:
            self.preprocess_(i)

    def _atomp(self, var):
        return type(var[0]) in map(type, [0L, 0, 0., ""])

    def _if(self, test, true, false=None):
        if self.eval(test):
            return self.eval(true)
        elif false:
            return self.eval(false)

    def _fn(self, sig, body):
        if any(not isinstance(x, str) for x in sig):
            raise SyntaxError("Arguments to function must just be identifiers")
        
        def llambda(*args):
            vars = dict(zip(sig, args))
            self.vars = inheritdict.idict(self.vars, llambda._vars).push(**vars)
            self.call_stack.append(llambda)
            try:
                out = self.run([body])
                return out
            except ReturnI, e:
                return e.args[0]
            finally:
                self.call_stack.pop()
                self.vars = self.vars.pop()

        llambda._vars = self.vars
        llambda._catches = {}
        llambda.__name__ = ""
        return llambda

    def _set(self, name, value):
        value = self.eval(value)
        self.vars[name] = value
        if callable(value): value.__name__ = name
        return value

    def _block(self, *exprs):
        return map(self.eval, exprs)[-1]

    def _handle(self, type, handler):
        type = iftuple(self.eval(type))
        handler = self.eval(handler)
    
        f = self.call_stack[-1]
        f._catches[type] = handler

    def _signal(self, type, *args):
        type = iftuple(self.eval(type))
        args = map(self.eval, args)
        signal = builtin.signal(type, args)

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

        assert isinstance(control[0], str), "Received non-control-word return value from signal handler"

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
            print control[1]
            sys.exit()

    builtindict = {"atom?": _atomp, "if": _if,
        "fn": _fn, "set!": _set, "block": _block,
        "signal": _signal, "handle": _handle}

    def eval(self, tree):
        if type(tree) in map(type, (0, 0L, 0.)):
            return tree
        elif isinstance(tree, str):
            if tree in self.vars:
                return self.vars[tree]
            else:
                raise NameError("Lisp: Name `%s` does not exist" % tree)
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
            c = [self.eval(tree[1])]
            return c
        elif tree[0] == ",@":
            return self.eval(tree[1])
        else:
            return [sum(map(self.quasieval, tree), [])]

