
class Instruction(Exception):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        args = map(str, self.args) + ["%s=%s" % (key, value) for key, value in self.dict.items()]
        cls = self.__class__.__name__
        return "<%s%s%s>" % (cls, " " if args else "", ", ".join(args))

class ReturnI(Instruction): pass
class BeReturnedI(Instruction): pass

def exc2sig_name(cls):
    """
    In Python, exceptions are defined by inheritance chains of named classes.
    In Pylisp, they're instead defined by lists. We should convert between
    them.
    """

    def pyname2lname(cls):
        name = cls.__name__

        if name == "Exception": return "error"
        elif name == "Warning": return "warning"
        # Special cases out of the way

        uppers = [i for i, v in enumerate(name) if v.isupper()]
        pos = []
        for i in uppers:
            if i + 1 not in uppers or i - 1 not in pos:
                pos.append(i)
        name_parts = []
        for i, inext in zip(pos, pos[1:]): # Note: automatically kills last word
            name_parts.append(name[i:inext].lower())
        return "-".join(name_parts)

    if hasattr(cls, "__mro__"):
        names = map(pyname2lname, cls.__mro__)

        if "warning" in names: names = names[:names.index("warning") + 1]
        elif "error" in names: names = names[:names.index("error") + 1]

        return reversed(names)
    else:
        return ["error", pyname2lname(cls)]
