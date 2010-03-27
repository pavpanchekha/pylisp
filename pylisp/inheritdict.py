class _link(object):
    __slots__ = ["var", "dict"]

    def __init__(self, var, dict):
        self.var = var
        self.dict = dict

    def value(self):
        return self.dict[self.var]

    @classmethod
    def new(cls, var, dict):
        if isinstance(dict[var], cls):
            return dict[var]
        else:
            return cls(var, dict)

class idict(object):
    def __init__(self, parent=None, odict=None, **kwargs):
        if parent is None:
            parent = {}
        if odict: kwargs = odict

        self.parent = parent
        self.dict = kwargs
        self.stop = False

    def __getitem__(self, item):
        if item in self.dict:
            k = self.dict[item]
            if isinstance(k, _link):
                k = k.value()
        else:
            k = self.parent[item]
            self.dict[item] = _link.new(item, self.parent)
        return k

    def __setitem__(self, item, value):
        if self.stop:
            self.dict[item] = value
        elif item in self.dict and isinstance(self.dict[item], _link):
            self.dict[item].dict.dict[item] = value
        elif item not in self.parent:
            self.dict[item] = value
        else:
            self.parent[item] = value
            self.dict[item] = _link.new(item, self.parent)

    def __delitem__(self, item):
        if item in self.dict:
            if isinstance(self.dict[item], _link):
                del self.dict[item].dict[item]
            del self.dict[item]
        else:
            del self.parent[item]

    def __contains__(self, item):
        k = item in self.dict
        if k: return _link.new(item, self.dict)
        k = item in self.parent
        if k: return k
        return False

    def push(self, kwargs=None):
        if kwargs is None: kwargs = {}
        return idict(self, kwargs)

    def pop(self):
        return self.parent

    def depth(self):
        if isinstance(self.parent, idict):
            return 1 + self.parent.depth()
        else:
            return 1

    def stack(self):
        if isinstance(self.parent, idict):
            return self.parent.stack() + [id(self)]
        else:
            return [id(self)]
