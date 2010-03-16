def eat_name(s):
    i = 0
    if s[0] in "0123456789":
        return "", s
    while i < len(s) and s[i] not in "(); \t\n\v\f":
        i += 1
    n = s[:i]
    if "." not in (n, n[0], n[-1]) and "." in n:
        nexp = n.split(".")
        n = ["::", nexp[0]] + map(lambda x: ["'", x], nexp[1:])
    return n, s[i:]

def eat_number(s):
    if s[0] not in "0123456789.": return "", s

    i = 0
    while i < len(s) and s[i] in "0123456789.": i += 1

    mys = s[:i]

    if mys == ".":
        return ".", s[1:]
    elif "." in mys:
        return float(mys), s[i:]
    else:
        return int(mys), s[i:]

def eat_str(s):
    if s[0] != '"': return "", s

    i = 1
    while i < len(s) and s[i] != '"':
        if s[i] == "\\": i += 2
        else: i += 1

    return ["'", eval(s[:i+1])], s[i+1:]

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

def eat_pyeval(s):
    if not s.startswith("{{"): return "", s
    
    i = 2
    while i+1 < len(s) and (s[i] != '}' or s[i+1] != "}"):
        i += 1
    
    return ["pyeval", ["'", s[2:i]]], s[i+2:]

def eat_pyexec(s):
    if not s.startswith("{{{"): return "", s
    
    i = 3
    while i < len(s) and (s[i] != '}' or s[i+1] != "}" or s[i+2] != "}"):
        i += 1
    
    return ["pyexec", ["'", s[3:i]]], s[i+3:]
    
def eat_value(s):
    s = s.strip()
    if len(s) == 0:
        return None, ""
    elif s[0] == ";":
        s = eat_comment(s)[1]
        return eat_value(s)
    elif s[0] == "(":
        return eat_sexp(s)
    elif s[0] in "0123456789.":
        return eat_number(s)
    elif s[0] in "'`,":
        c = s[0]
        s = s[1:]
        if c == "," and s[0] == "@":
            c = ",@"
            s = s[1:]
        sexp, s = eat_value(s)
        return [c, sexp], s
    elif s[0] == '"':
        return eat_str(s)
    elif s.startswith("{{{"):
        return eat_pyexec(s)
    elif s.startswith("{{"):
        return eat_pyeval(s)
    else:
        sexp, s = eat_name(s)
        if sexp in ("#t", "#f"):
            sexp = {"#t": True, "#f": False}[sexp]
        return sexp, s

def parse(s):
    tree = []
    while s != "":
        sexp, s = eat_value(s)
        if sexp :
            s = s.strip()
            tree.append(sexp)
    return tree
