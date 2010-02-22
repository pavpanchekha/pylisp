import operator

builtins = {"nil": [], "True": True, "False": False}
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

@lispfunc("car")
def car(l):
    return l[0]

@lispfunc("cdr")
def cdr(l):
    return l[1:]

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
        print str_(v),
    print

def str_(v):
    if callable(v):
        if v.__name__:
            return "{{fn %s}}" % v.__name__
        else:
            return "{{fn}}"
    elif isinstance(v, list):
        if len(v) > 0 and v[0] in (",", ",@", "'", "`"):
            return v[0] + str_(v[1])
        else:
            return "(" + " ".join(map(str_, v)) + ")"
    else:
        return str(v)

@lispfunc("throw")
def throw_(thing):
    raise thing

@lispfunc("error")
class error(Exception):
    def __init__(self, type, *args):
        assert isinstance(type, basestring), "Type must be symbol"
        self.type = type
        self.args = list(args) #ah, tuples are dumb

    def __str__(self):
        return "%s: %s" % (self.type, str_(list(self.args)))

lispfunc("len")(len)
lispfunc("+")(operator.add)
lispfunc("-")(operator.sub)
lispfunc("*")(operator.mul)
lispfunc("/")(operator.floordiv)
lispfunc("mod")(operator.mod)
lispfunc("^")(operator.pow)
lispfunc("=")(operator.eq)
lispfunc("!=")(operator.ne)
lispfunc("<")(operator.lt)
lispfunc(">")(operator.gt)
lispfunc("<=")(operator.le)
lispfunc(">=")(operator.ge)
lispfunc("not")(operator.not_)

def def_(name, args, *body):
    return ["set!", name, ["fn", args, ["block"] + list(body)]]

macros = {
    "def": def_,
    }
