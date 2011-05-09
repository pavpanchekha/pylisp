
arglengths = {
        "if": 1, "def": 2, "def::method": 2,
        "def::static": 2, "def::class": 2,
        "def::macro": 2, "class::simple": 2,
        "class": 2, "fn": 1, "set!": 1, "handle": 1
    }

def str_(v, breakline=False, indent=0):
    import types
    
    if hasattr(v, "_lispprint"):
        return [v._lispprint()]
    elif isinstance(v, list):
        if len(v) > 0 and v[0] in (",", ",@", "'", "`"):
            c = str_(v[1], breakline)
            c[0]  = v[0] + c[0]
            return c
        else:
            strs = sum(map(lambda x: str_(x, breakline, indent + 1), v), [])
            slen = len(" ".join(strs)) + indent*2
            if slen > 65 and breakline: # 75 == Max width
                w = map(lambda x: "  "*indent + x, strs)
                w[0] = w[0].strip()
                if w[0] in arglengths:
                    args = " ".join(map(str.strip, w[:arglengths[w[0]] + 1]))
                    if len(args) + indent * 2 < 65:
                        w[:arglengths[w[0]] + 1] = [args.strip()]
                
                w[0] = "(" + (w[0] if len(w) > 0 else "")
                w[-1] += ")"
                return w
            else:
                return ["(" + " ".join(strs) + ")"]
    elif v is True or v is False:
        return ["#t" if v else "#f"]
    elif v is None:
        return ["#0"]
    else:
        return [str(v)]
