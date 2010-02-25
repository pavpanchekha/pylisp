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
        print "\n".join(str_(v, breakline=True)),
    print
    return args[-1]

def str_(v, breakline=False, indent=0):
    if callable(v):
        if v.__name__:
            return ["{{fn %s}}" % v.__name__]
        else:
            return ["{{fn}}"]
    elif isinstance(v, list):
        if len(v) > 0 and v[0] in (",", ",@", "'", "`"):
            c = str_(v[1], breakline)
            c[0]  = v[0] + c[0]
            return c
        else:
            strs = sum(map(lambda x: str_(x, breakline, indent + 2), v), [])
            slen = len(" ".join(strs)) + indent*2
            if slen > 50 and breakline: # 75 == Max width
                indent = "  "
                w = map(lambda x: indent + x, strs)
                if len(w) > 0:
                    w[0] = "(" + w[0].strip()
                else:
                    w.append("(")
                w[-1] += ")"
                return w
            else:
                return ["(" + " ".join(strs) + ")"]
    else:
        return [str(v)]

@lispfunc("signal")
def throw_(type, *args):
    raise signal(type, *args)

class signal(Exception):
    def __init__(self, type, *args):
        self.type = type if isinstance(type, list) else [type]
        self.args = list(args) #ah, tuples are dumb

    def __str__(self):
        return "%s: %s" % (str_(self.type)[0], " ".join(map(lambda x: str_(x)[0], self.args[0])))

@lispfunc("silent")
def silent(*args, **kwargs):
    return None

lispfunc("len")(len)
lispfunc("+")(operator.add)
lispfunc("-")(operator.sub)
lispfunc("*")(operator.mul)
lispfunc("/")(operator.truediv)
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

def def_macro(name, args, *body):
    return ["set!::macro", name, ["fn", args, ["block"] + list(body)]]

def control(name, *args):
    return ["'", [name, list(args) or []]]

macros = {
        "def": def_, "def::macro": def_macro, "control": control,
    }
