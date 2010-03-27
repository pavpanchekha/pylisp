class idict:
    def __init__(self, parent=None, odict=None, **kwargs):
        if parent is None:
            parent = {}
        if kwargs: odict = kwargs

        self.parent = parent
        self.dict = odict
        self.stop = False

    def __getitem__(self, item):
        if item in self.dict:
            return self.dict[item]
        else:
            return self.parent[item]

    def __setitem__(self, item, value):
        if self.stop or item not in self.parent:
            self.dict[item] = value
        else:
            self.parent[item] = value

    def __delitem__(self, item):
        if item in self.dict:
            del self.dict[item]
        else:
            del self.parent[item]

    def __contains__(self, item):
        return item in self.dict or item in self.parent

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
