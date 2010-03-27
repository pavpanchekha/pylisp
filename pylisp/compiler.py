import sexp as parser
import lisp
import ast
import dis
import sys

debug = -1

binops = {
        "+": ast.Add, "-": ast.Sub, "*": ast.Mult, "/": ast.Div,
        "mod": ast.Mod, "^": ast.Pow}

unops = {
        "+": ast.UAdd, "-": ast.USub, "not": ast.Not}

class Compiler(object):
    def __init__(self, interactive=False):
        self.intp = lisp.Lisp()
        del self.intp.macros["while"]
        del self.intp.macros["for"]
        del self.intp.macros["def"]
        self.context = self.intp.vars
        self.interactive = interactive

    def run(self, s):
        return self.compile(s)()

    def compile(self, s):
        c = self._compile(s)
        if debug > -1: dis.dis(c)
        return Environment(c, self.context)

    def _compile(self, s):
        if isinstance(s, str): s = parser.parse(s)
        s = self.intp.preprocess(s)
        a = map(self._tostmt, s)
        
        if self.interactive:
            a = ast.Interactive(a)
            t = "single"
        elif len(a) == 1 and isinstance(a[0], ast.Expr):
            a = ast.Expression(a[0].value)
            t = "eval"
        else:
            a = ast.Module(a)
            t = "exec"
        ast.fix_missing_locations(a)

        try:
            return compile(a, "<pylisp>", t)
        except ValueError:
            if debug > -1:
                print "Error Compiling Code!"
                print ast.dump(a)
            raise Exception

    def _tostmt(self, tree):
        if not isinstance(tree, list) or not tree:
            return ast.Expr(self._toexpr(tree))
        elif tree[0] == "if":
            return ast.If(self._toexpr(tree[1]),
                    [self._tostmt(tree[2])],
                    [self._tostmt(tree[3])] if len(tree) > 3 else [])
        elif tree[0] == "block":
            return ast.Suite(map(self._tostmt, tree[1:]))
        elif tree[0] == "set!":
            value = self._toexpr(tree[2])
            if tree[1][0] == "'":
                return ast.Assign([ast.Name(tree[1][1], ast.Store())], value)
            else:
                raise NotImplementedError("Can't set! `%s`" % tree[1][0])
        elif tree[0] == "while":
            test = self._toexpr(tree[1])
            body = map(self._tostmt, tree[2:])
            return ast.While(test, body, [])
        elif tree[0] == "for":
            target = self._toexpr(tree[1][0])
            assert isinstance(target, ast.Name), "For-looping over non-idents not supported"
            target.ctx = ast.Store()
            iter = self._toexpr(tree[1][1])
            body = map(self._tostmt, tree[2:])
            return ast.For(target, iter, body, [])
        #elif tree[0] == "print":
            #return ast.Print(None, map(self._toexpr, tree[1:]), True)
        elif tree[0] == "def":
            name = tree[1]
            args = tree[2]
            if "." in args:
                stargs = args[args.index(".")+1]
                args = args[:args.index(".")]
            else:
                stargs = None
            body = map(self._tostmt, tree[3:])
            return ast.FunctionDef(name, ast.arguments(map(lambda x: ast.Name(x, ast.Param()), args), stargs, None, []), body, [])

        else:
            return ast.Expr(self._toexpr(tree))

    def _tonode(self, tree):
        if isinstance(tree, str):
            return ast.Str(tree)
        elif type(tree) in map(type, [1, 1.0, True, None]):
            return ast.Num(tree)
        elif isinstance(tree, list):
            return ast.List(map(self._tonode, tree), ast.Load())
        else:
            print "COULD NOT MAKE NODE"
            print tree

    def _toexpr(self, tree):
        if isinstance(tree, str):
            return ast.Name(tree, ast.Load())
        elif type(tree) in map(type, [1, 1.0, True, None]):
            return ast.Num(n=tree)
        elif tree[0] == "if":
            if len(tree) == 3:
                tree.append("nil")
            test = self._toexpr(tree[1])
            ifyes = self.toexpr(tree[2])
            ifno = self._toexpr(tree[3]) if len(tree) > 3 else []
            return ast.IfExp(test, ifyes, ifno)
        elif tree[0] == "block":
            return ast.Subscript(ast.List(map(self._toexpr, tree[1:]), ast.Load()), ast.Index(ast.Num(-1)), ast.Load())
        elif tree[0] == "fn":
            args = tree[1]
            if "." in args:
                stargs = args[args.index(".")+1]
                args = args[:args.index(".")]
            else:
                stargs = None

            if len(tree) > 3:
                body = self._toexpr(["block"] + tree[2:])
            else:
                body = self._toexpr(tree[2])

            return ast.Lambda(ast.arguments(map(lambda x: ast.Name(x, ast.Param()), args), stargs, None, []), body)
        elif tree[0] == "'":
            if isinstance(tree[1], list):
                return ast.List(map(self._tonode, tree[1]), ast.Load())
            elif type(tree[1]) in map(type, [1, 1.0, True, None]):
                return self._toexpr(tree[1])
            elif isinstance(tree[1], str):
                return ast.Str(tree[1])
        elif tree[0] == "for":
            return self._toexpr(["map", ["fn", [tree[1][0]]] + tree[2:], tree[1][1]])
        elif isinstance(tree[0], str) and tree[0] in binops and len(tree) == 3:
            return ast.BinOp(self._toexpr(tree[1]), binops[tree[0]](), self._toexpr(tree[2]))
        elif isinstance(tree[0], str) and tree[0] in unops and len(tree) == 2:
            return ast.UnaryOp(unops[tree[0]](), self._toexpr(tree[1]))
        elif tree[0] == "::" and tree[2][0] == "'":
            return ast.Attribute(self._toexpr(tree[1]), tree[2][1], ast.Load())
        elif tree[0] == "[]":
            if isinstance(tree[1], list) and tree[1][0] == "slice":
                start = self._toexpr(tree[1][1]) if len(tree[1]) > 1 else None
                stop = self._toexpr(tree[1][2]) if len(tree[1]) > 2 else None
                step = self._toexpr(tree[1][3]) if len(tree[1]) > 3 else None
                return ast.Subscript(self._toexpr(tree[1]), ast.Subscript(start, stop, step), ast.Load())
            else:
                return ast.Subscript(self._toexpr(tree[1]), ast.Index(self._toexpr(tree[2])), ast.Load())
        elif isinstance(tree, list) and tree:
            return ast.Call(self._toexpr(tree[0]),
                    map(self._toexpr, tree[1:]), [],
                        None, None)
        else:
            print "FAILED TO COMPILE"
            print tree

class Environment(object):
    def __init__(self, code, context):
        self.context = context
        self.code = code

    def __call__(self):
        exec self.code in {}, self.context

if __name__ == "__main__":
    import readline
    if "-d" in sys.argv:
        debug = 1
    c = Compiler(True) # interactive
    while True:
        try:
            s = raw_input("compile> ")
        except:
            break
        c.run(s)
 
