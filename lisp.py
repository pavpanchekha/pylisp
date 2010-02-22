import sexp
import inheritdict
import builtin

class Lisp(object):
    def __init__(self, debug=False):
        self.vars = inheritdict.idict(None, **builtin.builtins)
        self.macros = builtin.macros
        self.call_stack = []
        self.debug = debug

    def run(self, s):
        global sexp

        if isinstance(s, basestring):
            sexps = sexp.parse(s)
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
        if not isinstance(tree, list) or len(tree) == 0:
            pass
        elif tree[0] == "def::macro":
            if any(not isinstance(x, basestring) for x in tree[2]) or not isinstance(tree[1], basestring):
                raise SyntaxError("Arguments to macro and its name must just be identifiers")
            bob = tree[:]
            def mmacro(*args):
                vars = dict(zip(bob[2], args))
                self.vars = inheritdict.idict(self.vars, mmacro._vars).push(**vars)
                body = ["block"] + self.preprocess(bob[3:])
                self.call_stack.append(mmacro)
                try:
                    out = self.eval(body)
                except builtin.error._orig, e:
                    if e.type not in mmacro._catches:
                        raise
                    mmacro._catches[e.type](*e.args)
                self.call_stack.pop()
                self.vars = self.vars.pop()
                return out
            mmacro._vars = self.vars
            self.macros[tree[1]] = mmacro
            self.preprocess_flag = True
            tree[:] = []
        else:
            if isinstance(tree[0], basestring):
                if tree[0] in self.macros:
                    tree[:] = self.macros[tree[0]](*tree[1:])
            
                elif tree[0] in "'`": # Don't macro-expand inside literals
                    return
            for i in tree:
                self.preprocess_(i)

    def eval(self, tree):
        if isinstance(tree, int):
            return tree
        elif isinstance(tree, basestring):
            if tree in self.vars:
                return self.vars[tree]
            else:
                raise NameError("Lisp: Name `%s` does not exist" % tree)
        elif len(tree) == 0:
            return None
        elif tree[0] == "atom?":
            return isinstance(tree[1], basestring)
        elif tree[0] == "if":
            if self.eval(tree[1]):
                return self.eval(tree[2])
            elif len(tree) > 3:
                return self.eval(tree[3])
        elif tree[0] == "fn":
            if any(not isinstance(x, basestring) for x in tree[1]):
                raise SyntaxError("Arguments to function must just be identifiers")
            def llambda(*args):
                vars = dict(zip(tree[1], args))
                self.vars = inheritdict.idict(self.vars, llambda._vars).push(**vars)
                self.call_stack.append(llambda)
                
                try:
                    out = self.eval(tree[2])
                except builtin.error._orig, e:
                    if e.type not in llambda._catches:
                        raise
                    return llambda._catches[e.type](*e.args)
                else:
                    self.vars = self.vars.pop()
                    return out
                finally:
                    self.call_stack.pop()
            llambda._vars = self.vars
            llambda._catches = {}
            llambda.__name__ = ""
            return llambda
        elif tree[0] == "set!":
            self.vars[tree[1]] = self.eval(tree[2])
            if callable(self.vars[tree[1]]):
                self.vars[tree[1]].__name__ = tree[1]
            return self.vars[tree[1]]
        elif tree[0] == "'":
            return tree[1]
        elif tree[0] == "`":
            return self.quasieval(tree[1])[0]
        elif tree[0] == "block":
            return map(self.eval, tree[1:])[-1]
        elif tree[0] == "catch":
            f = self.call_stack[-1]
            f._catches[self.eval(tree[1])] = self.eval(tree[2])
        else:
            tree2 = map(self.eval, tree)
            return tree2[0](*tree2[1:])

    def quasieval(self, tree):
        if not isinstance(tree, list):
            return [tree]
        elif tree[0] == ",":
            c = [self.eval(tree[1])]
            return c
        elif tree[0] == ",@":
            return self.eval(tree[1])
        else:
            return [sum(map(self.quasieval, tree), [])]

def main():
    import traceback
    import os
    import readline

    l = Lisp()
    if os.path.isfile("stdlib.lsp"):
        l.run(open("stdlib.lsp").read())
    while 1:
        try:
            s = raw_input("lisp> ") + "\n"
        except (EOFError, SystemExit):
            return

        while True:
            try:
                sexps = sexp.parse(s)
            except IndexError:
                try:
                    s += raw_input("... > ") + "\n"
                except (EOFError, SystemExit):
                    return
                continue
            else:
                break

        try:
            v = l.run(s)
        except builtin.error._orig, e:
            if l.call_stack:
                print "Call stack:"
                for i in l.call_stack:
                    print "\t%s" % builtin.str_(i)
            print "Error:", e
        except Exception, e:
            traceback.print_exc()
        else:
            if v is not None:
                builtin.print_(v)

if __name__ == "__main__":
    import sys
    import os
    
    if len(sys.argv) > 1:
        for f in sys.argv[1:]:
            l = Lisp()
            if os.path.isfile("stdlib.lsp"):
                l.run(open("stdlib.lsp").read())
            l.run(open(f).read())
    else:
        main()
