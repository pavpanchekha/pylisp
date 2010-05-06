class link(object):
    __slots__ = ["dict", "var"]

    def __init__(self, dict, var):
        self.var = var
        self.dict = dict

    def get(self):
        return self.dict[self.var]

    def set(self, value):
        self.dict[self.var] = value

    def delete(self, value):
        del self.dict[self.var]

    def exists(self):
        return self.var in self.dict

    @classmethod
    def new(cls, dict, var):
        if isinstance(dict[var], cls):
            return dict[var]
        else:
            return cls(dict, var)

class idict(object):
    def __init__(self, parent=None, odict=None, **kwargs):
        if parent is None:
            parent = {}
        if kwargs: odict = kwargs

        self.parent = parent
        self.dict = odict
        self.stop = False
        self.cache = {}

    def __getitem__(self, item):
        if item in self.dict:
            return self.dict[item]
        elif item in self.cache:
            try:
                l = self.cache[item]
                return l.dict[l.var]
            except KeyError:
                del self.cache[item]
                return self[item]
        else:
            v = self.parent[item]
            self.cache[item] = link.new(self.parent, item)
            return v

    def __setitem__(self, item, value):
        if item in self.cache and not self.cache[item].dict.stop:
            try:
                return self.cache[item].set(value)
            except KeyError:
                del self.cache[item]
                self.dict[item] = value
        if isinstance(self.parent, dict) or self.parent.stop or item not in self.parent:
            self.dict[item] = value
        else:
            self.parent[item] = value
            self.cache[item] = link.new(self.parent, item)

    def __delitem__(self, item):
        if item in self.cache:
            try:
                self.cache[item].delete()
            except KeyError:
                pass
            del self.cache[item]
        elif item in self.dict:
            del self.dict[item]
        else:
            del self.parent[item]

    def __contains__(self, item):
        try: self[item]
        except KeyError: return False
        else: return True

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
