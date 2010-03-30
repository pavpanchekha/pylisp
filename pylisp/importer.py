import sys
import os

preprocess_only = False
Module = type(sys)

class Finder(object):
    def __init__(self, interpreter_cls):
        self.l_cls = interpreter_cls

    def find_module(self, name, paths):
        if paths is None:
            paths = sys.path

        for i in paths:
            if os.path.isdir(i) and name + ".lsp" in os.listdir(i) and (
                    os.path.isfile(os.path.join(i, name + ".lsp")) or
                    (
                        os.path.isdir(os.path.join(i, name + ".lsp")) and
                        os.path.isfile(os.path.join(i, name, "__init__.lsp")))):
                return Loader(i, self.l_cls)

        return None

class Loader(object):
    def __init__(self, path, interpreter_cls):
        self.path = path
        self.l = interpreter_cls()

    def load_module(self, name):
        if name in sys.modules:
            return sys.modules[name]
        mod = Module(name, "")
        sys.modules[name] = mod
        mod.__loader__ = self
        mod.__dict__["#macros"] = self.l.macros

        try:
            if os.path.isdir(os.path.join(self.path, name)):
                self.load_package(name, mod)
            else:
                self.load_simple(name, mod)
        except:
            del sys.modules[name]
            raise

        if preprocess_only:
            mod.__dict__["#preprocess-only"] = True
        self.correct_parent_pkg(mod)
        return mod

    def load_package(self, name, mod):
        mod.__path__ = self.path # TODO: adding paths?
        self.eval(os.path.join(self.path, name, "__init__.lsp"))
        mod.__dict__.update(self.l.vars.dict)

    def load_simple(self, name, mod):
        self.eval(os.path.join(self.path, name + ".lsp"))
        mod.__dict__.update(self.l.vars.dict)
        mod.__file__ = os.path.join(self.path, name + ".lsp")

    def eval(self, path):
        if preprocess_only:
            import sexp
            self.l.preprocess(sexp.parse(open(path).read()))
        else:
            self.l.run(open(path).read())

    def correct_parent_pkg(self, module):
        path = self.path
        ppath = None
        while path and (os.path.isfile(os.path.join(path, "__init__.py")) or \
                os.path.isfile(os.path.join(path, "__init__.lsp"))):
            ppath = path
            path = os.path.split(path)[0]
        module.__package__ = ppath
