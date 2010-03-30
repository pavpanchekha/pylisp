import inheritdict
from builtin import str_

class ReturnI(Exception): pass
class BeReturnedI(Exception): pass
            
specialforms = {}

def lispfunc(name, fexpr=False):
    def decorator(f):
        specialforms[name] = f
        f._specialform = True
        f._fexpr = fexpr
        return f
    return decorator

@lispfunc("pyeval")
def pyeval(self, code):
    return eval(code, self.vars.dict, self.vars.parent)

@lispfunc("pyexec")
def pyexec(self, code):
    exec code in self.vars.dict, self.vars.parent

@lispfunc("compile")
def plcompile(self, *code):
    import compiler
    c = compiler.Compiler(self)
    return c.compile(code)

@lispfunc("has")
def has(self, var, arg=None):
    if arg is None:
        return var in self.vars
    else:
        return hasattr(var, arg)

@lispfunc("#include")
def _include(self, *args):
    import sys
    args = list(args)
    modname = ".".join(args)
    
    if modname in sys.modules:
        if sys.modules[modname].__dict__.get("#preprocess-only", False):
            del sys.modules[modname]
    
    __import__(modname)
    d = sys.modules[modname].__dict__
    self.vars.dict.update(d)

@lispfunc("if", True)
def _if(self, test, true, false=None):
    if self.eval(test):
        return self.eval(true)
    elif false:
        return self.eval(false)

@lispfunc("set!", True)
def set(self, name, value):
    value = self.eval(value)
    if not isinstance(name, list):
        raise SyntaxError("What the hell are you trying to set?")
    elif name[0] == "'" and isinstance(name[1], str):
        self.vars[name[1]] = value
        if callable(value): value.__name__ = name[1]
    elif name[0] == "::":
        setattr(self.eval(["::", name[:-1]]), self.eval(name[-1]), value)
    elif name[0] == "[]":
        self.eval(name[1])[self.eval(name[2])] = value
    else:
        raise SyntaxError("What the hell are you trying to set?")
    return value

@lispfunc("block")
def block(self, *exprs):
    return exprs[-1]

@lispfunc("handle")
def handle(self, type, handler):
    type = (type,) if isinstance(type, str) else tuple(type)

    f = self.call_stack[-1]
    f._catches[type] = handler

class Signal(Exception):
    def __init__(self, type, *args):
        self.type = type if isinstance(type, list) else [type]
        self.args = list(args) if isinstance(type, tuple) else args #ah, tuples are dumb

    def __str__(self):
        s1 = str_(self.type)
        if self.args:
            s1 += ": " + " ".join(map(str_, self.args))
        return s1

@lispfunc("signal")
def signal(self, type, *args):
    signal = Signal(type, *args)
    type = (type,) if isinstance(type, str) else tuple(type)

    for i, f in enumerate(reversed(self.call_stack)):
        ttype = tuple(type[:])
        while hasattr(f, "_catches") and ttype and ttype not in f._catches:
            ttype = tuple(ttype[:-1])
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

@lispfunc("return")
def _return(self, arg=[]):
    raise ReturnI(arg)

@lispfunc("fn", True)
def fn(self, sig, *body):
    if isinstance(body, tuple): body = list(body)
    if isinstance(sig, str): sig = [".", sig]
    
    if "." in sig:
        many_name = sig[sig.index(".") + 1]
        sig[sig.index("."):] = []
    else:
        many_name = None
    
    def llambda(*args):
        vars = dict(zip(sig, args))

        if many_name is not None:
            vars[many_name] = list(args)[len(sig):]

        old_vars = self.vars
        self.vars = llambda._vars.push(vars)
        self.call_stack.append(llambda)
        try:
            return self.run(body)
        except ReturnI, e:
            return e.args[0]
        finally:
            self.call_stack.pop()
            self.vars = old_vars
    llambda._vars = self.vars
    llambda._catches = {}
    llambda.__name__ = ""
    return llambda

@lispfunc("#class", True)
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

@lispfunc("'", True)
def quote(self, arg):
    return arg

@lispfunc("`", True)
def quasiquote(self, arg):
    return self.quasieval(arg)[0]
