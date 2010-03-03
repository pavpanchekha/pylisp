import operator
import prettyprinter
import sys

builtins = {"nil": [], "#t": True, "#f": False, "#0": None}
def lispfunc(name):
    def decorator(f):
        def g(*args, **kwargs):
            return f(*args, **kwargs)
        g.__name__ = name
        g._catches = {}
        g._orig = f # For a nasty hack here and there
        builtins[name] = g
        return g
    return decorator

def foldable(f):
    def t(*args):
        return reduce(f, args)
    return t

@lispfunc("car")
def car(l):
    return l[0]

@lispfunc("cdr")
def cdr(l):
    return l[1:]

@lispfunc("last")
def last(l):
    return l[-1]

@lispfunc("cons")
def cons(a, b):
    return [a] + b

@lispfunc("gensym")
def gensym():
    import random
    return "#:%d" % random.randint(0, 2**31-1)

@lispfunc("print")
def print_(*args):
    for v in args:
        print "\n".join(prettyprinter.str_(v, breakline=True)),
    print
    return args[-1]

@lispfunc("str")
def str_(v):
    return prettyprinter.str_(v)[0]

class signal(Exception):
    def __init__(self, type, *args):
        self.type = type if isinstance(type, list) else [type]
        self.args = list(args) if isinstance(type, tuple) else args #ah, tuples are dumb

    def __str__(self):
        s1 = str_(self.type)
        if self.args:
            s1 += ": " + " ".join(map(str_, self.args))
        return s1

@lispfunc("silent")
def silent(*args, **kwargs):
    return None

@lispfunc("-")
def subtract(*args):
    if len(args) == 1:
        return -args[0]
    else:
        return foldable(operator.sub)(*args)

lispfunc("len")(len)
lispfunc("+")(foldable(operator.add))
lispfunc("*")(foldable(operator.mul))
lispfunc("/")(foldable(operator.truediv))
lispfunc("mod")(operator.mod)
lispfunc("^")(operator.pow) # TODO: foldRable ?
lispfunc("=")(operator.eq) # TODO: Rich comparisons
lispfunc("!=")(operator.ne)
lispfunc("<")(operator.lt)
lispfunc(">")(operator.gt)
lispfunc("<=")(operator.le)
lispfunc(">=")(operator.ge)
lispfunc("not")(operator.not_)
lispfunc("conj")(operator.invert)
lispfunc("::")(foldable(getattr))
lispfunc("slice")(slice)
lispfunc("range")(range)
lispfunc("dir")(dir)
lispfunc("[]")(foldable(operator.getitem))
lispfunc("help")(help)
lispfunc("abs")(abs)
lispfunc("list")(lambda *args: list(args))
lispfunc("static-method")(staticmethod)
lispfunc("class-method")(classmethod)
lispfunc("exit")(sys.exit)

def def_(name, args, *body):
    return ["set!", ["'", name], ["fn", args] + list(body)]

def def_static(name, args, *body):
    return ["set!", ["'", name], ["static-method", ["fn", args] + list(body)]]

def def_class(name, args, *body):
    return ["set!", ["'", name], ["class-method", ["fn", args] + list(body)]]

def def_macro(name, args, *body):
    return ["set!::macro", ["'", name], ["fn", args] + list(body)]

def class_(name, inheritsfrom, *body):
    return ["set!", ["'", name], ["cls", inheritsfrom] + list(body)]

def control(name, *args):
    return ["'", [name, list(args) or []]]

macros = {
        "def": def_, "def::macro": def_macro, "control": control, "class": class_, "def::class": def_class, "def::static": def_static,
    }
