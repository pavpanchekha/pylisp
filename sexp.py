def eat_name(s):
    i = 0
    if s[0] in "0123456789":
        return "", s
    while i < len(s) and s[i] not in "()'# \t\n\v\f":
        i += 1
    return s[:i], s[i:]

def eat_number(s):
    if s[0] not in "0123456789": return "", s

    i = 0
    while i < len(s) and s[i] in "0123456789": i += 1
    return  int(s[:i]), s[i:]

def eat_sexp(s):
    if s[0] != "(": return "", s

    retval = []
    i = 1
    while s[i] != ")":
        if s[i] in " \t\n\v":
            i += 1
        else:
            sexp, s = eat_value(s[i:])
            s = s.strip()
            retval.append(sexp)
            i = 0
    return retval, s[i+1:]

def eat_comment(s):
    if s[0] != ";": return "", s
    
    i = 0
    while i < len(s) and s[i] != "\n": i += 1
    return "", s[i:]

def eat_value(s):
    s = s.strip()
    if len(s) == 0:
        return None, ""
    elif s[0] == ";":
        s = eat_comment(s)[1]
        return eat_value(s)
    elif s[0] == "(":
        return eat_sexp(s)
    elif s[0] in "0123456789":
        return eat_number(s)
    elif s[0] in "'`,":
        c = s[0]
        s = s[1:]
        if c == "," and s[0] == "@":
            c = ",@"
            s = s[1:]
        sexp, s = eat_value(s)
        return [c, sexp], s
    else:
        sexp, s = eat_name(s)
        if sexp in ("True", "False"):
            sexp = {"True": True, "False": False}[sexp]
        return sexp, s

def parse(s):
    tree = []
    while s != "":
        sexp, s = eat_value(s)
        if sexp :
            s = s.strip()
            tree.append(sexp)
    return tree
