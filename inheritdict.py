class idict:
    def __init__(self, parent=None, odict=None, **kwargs):
        if parent is None:
            parent = {}
        
        if not kwargs and odict:
            kwargs = odict

        self.parent = parent
        self.dict = kwargs

    def __getitem__(self, item):
        if item in self.dict:
            return self.dict[item]
        else:
            return self.parent[item]

    def __setitem__(self, item, value):
        if item in self.dict:
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

    def push(self, **kwargs):
        return idict(self, **kwargs)

    def pop(self):
        return self.parent

    def depth(self):
        if isinstance(self.parent, idict):
            return 1 + self.parent.depth()
        else:
            return 1
