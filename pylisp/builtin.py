import operator
import prettyprinter
import sys

builtins = {"nil": [], "#t": True, "#f": False, "#0": None}

def lispfunc(name):
    def decorator(f):
        builtins[name] = f
        return f
    return decorator

def foldable(f, default = None):
    def t(*args):
        if not args and default is not None:
            return default
        else:
            return reduce(f, args)
    return t

# -----------------------------------------

def car(l):
    if not isinstance(l, str):
        return l[0]
    else:
        raise TypeError("Cannot take `car` of a list")

def cdr(l):
    if not isinstance(l, str):
        return l[1:] 
    else:
        raise TypeError("Cannot take `cons` of a list")

def last(l):
    if not isinstance(l, str):
        return l[-1] 
    else:
        raise TypeError("Cannot take `last` of a list")

def cons(a, b):
    if not isinstance(b, str):
        return [a] + b
    else:
        raise TypeError("Cannot `cons` onto a string")

def dict_(*args): return dict(args)
def atomp(var): return not isinstance(var, list)

@lispfunc("#import")
def _import(*args):
    args = list(args)
    modname = ".".join(args)

    if modname in sys.modules:
        if sys.modules[modname].__dict__.get("#preprocess-only", False):
            del sys.modules[modname]

    __import__(modname)
    return sys.modules[modname]

@lispfunc("gensym")
def gensym():
    import random
    return "#:%d" % random.randint(0, 2**31-1)

@lispfunc("print")
def print_(*args):
    for v in args:
        print "\n".join(prettyprinter.str_(v, breakline=True)),
    print
    return args[-1] if args else None

@lispfunc("str")
def str_(v):
    return prettyprinter.str_(v)[0]

@lispfunc("silent")
def silent(*args, **kwargs):
    return None

@lispfunc("-")
def subtract(*args):
    if len(args) == 1:
        return -args[0]
    else:
        return foldable(operator.sub)(*args)

@lispfunc("read")
def read(s=""):
    import sexp
    v = raw_input(s)
    return sexp.parse(v)

_t = {"+": foldable(operator.add, 0), "*": foldable(operator.mul, 1),
        "/": foldable(operator.truediv), "^": operator.pow, "=": operator.eq,
        "!=": operator.ne, "<": operator.lt, ">": operator.gt, "<=": operator.le,
        ">=": operator.ge, "not": operator.not_, "conj": operator.invert,
        "::": foldable(getattr), "[]": foldable(operator.getitem),
        "mod": operator.mod,
        "static-method": staticmethod, "class-method": classmethod,
        "callable?": callable, "raw_input": input, "#property": property,
        "sort": sorted, "help": help, "dict": dict_,
        "in": operator.contains, "input": raw_input, "atom?": atomp,
        "===": operator.is_, "is": isinstance}

for name, fn in _t.items():
    lispfunc(name)(fn)

_t2 = [len, slice, range, dir, abs, sys.exit, hash, all, map, zip, filter,
        any, bin, bool, chr, open, format, hex, id, int, max, min,
        oct, ord, reduce, round, sum, car, cdr, cons, last, list]

for fn in _t2:
    lispfunc(fn.__name__)(fn)

