r"""
The `sexp` module parses the special subset of sexps
that pylisp supports. Where by subset I mean sorta-related
set. There is only one function you should be using: parse.

>>> parse('''(+ "Hello, " 'World (* '! ({x: {{x + 2}}} 3)))''')
[['+', ["'", 'Hello, '], ["'", 'World'], ['*', ["'", '!'], [['fn', ['x'], ['pyeval', ["'", 'x + 2']]], 3]]]]

Note that the code returns a list of sexps. This might
eventually change to a generator-based approach, but for now
this provides a simple way to deal with code examples.

All other functions in this module follow the "eat" protocol,
wherein they are fed in a string, and return a (value, rest)
pair, where `rest` is the rest of the string not yet
processed. It's perhaps best to think of this as a
continuation of sorts. All of the eating functions are
prefixed with "eat_". If the input passed to such a function
is invalid, it by convention returns "" and eats nothing
(that is, it returns `("", s)` if passed an invalid `s`.
"""

def eat_name(s):
    """
    Eat a name, following the eat protocol.

    >>> eat_name("xyz stuff")
    ('xyz', ' stuff')
    >>> eat_name("xyz(")
    ('xyz', '(')
    >>> eat_name("xyz;comment")
    ('xyz', ';comment')
    >>> eat_name("0")
    ('', '0')
    """

    i = 0
    if s[0] in "0123456789(){}; \t\n\v\f":
        return "", s
    while i < len(s) and s[i] not in "(){}; \t\n\v\f":
        i += 1
    n = s[:i]
    if "." not in (n, n[0], n[-1]) and "." in n:
        nexp = n.split(".")
        n = ["::", nexp[0]] + map(lambda x: ["'", x], nexp[1:])
    return n, s[i:]

def eat_number(s):
    """
    Eat a float or integer.

    >>> eat_number("0")
    (0, '')
    >>> eat_number(".5")
    (0.5, '')
    >>> eat_number("1.5 ;comment")
    (1.5, ' ;comment')
    >>> eat_number("five")
    ('', 'five')
    """
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
    """
    Eat a double-quoted string.

    >>> eat_str('''"asdf"''')
    (["'", 'asdf'], '')
    >>> eat_str('''"" ;adsf''')
    (["'", ''], ' ;adsf')
    >>> eat_str("asdf")
    ('', 'asdf')
    """

    if s[0] != '"': return "", s

    i = 1
    while i < len(s) and s[i] != '"':
        if s[i] == "\\": i += 2
        else: i += 1

    return ["'", eval(s[:i+1])], s[i+1:]

def eat_sexp(s):
    """
    Eat a full s-expression.

    >>> eat_sexp("(+ 1 2)")
    (['+', 1, 2], '')
    >>> eat_sexp("((1 2) (2 3) (4 (1 2) (3 4)))")
    ([[1, 2], [2, 3], [4, [1, 2], [3, 4]]], '')
    >>> eat_sexp("+ 1 2")
    ('', '+ 1 2')
    """

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
    """
    Eat a comment (comments are semicolons and then to the
    end of the line).

    >>> eat_comment("; adsf\\n; asdf")
    ('', '\\n; asdf')
    >>> eat_comment("a")
    ('', 'a')
    """

    if s[0] != ";": return "", s
    
    i = 0
    while i < len(s) and s[i] != "\n": i += 1
    return "", s[i:]

def eat_pyeval(s):
    """
    Double-curly-braces denote inline Python.

    >>> eat_pyeval("{{2 + 2}} ;comment")
    (['pyeval', ["'", '2 + 2']], ' ;comment')
    >>> eat_pyeval("not-python")
    ('', 'not-python')
    """

    if not s.startswith("{{"): return "", s
    
    i = 2
    while i+1 < len(s) and (s[i] != '}' or s[i+1] != "}"):
        i += 1
    
    return ["pyeval", ["'", s[2:i]]], s[i+2:]

def eat_pyexec(s):
    """
    Triple-curly-braces denote inline Python.

    >>> eat_pyexec("{{{print a}}} ;comment")
    (['pyexec', ["'", 'print a']], ' ;comment')
    >>> eat_pyexec("not-python")
    ('', 'not-python')
    """

    if not s.startswith("{{{"): return "", s
    
    i = 3
    while i < len(s) and (s[i] != '}' or s[i+1] != "}" or s[i+2] != "}"):
        i += 1
    
    return ["pyexec", ["'", s[3:i]]], s[i+3:]

def eat_function(s):
    r"""
    Syntax of inline function: {x y z: (* x y x z)}

    >>> eat_function("{x y z: (* x y x z) 'a}; comment")
    (['fn', ['x', 'y', 'z'], ['*', 'x', 'y', 'x', 'z'], ["'", 'a']], '; comment')
    >>> eat_function("{:}")
    (['fn', []], '')
    >>> eat_function("{:\nstuff}")
    (['fn', [], 'stuff'], '')
    >>> eat_function("{,a:}")
    (['fn', [[',', 'a']]], '')
    """

    if s[0] != "{": return "", s

    i = s.find(":")
    if not i: raise SyntaxError("No end to function definition")

    vars = map(lambda x: eat_value(x)[0], s[1:i].split())
    body = []

    s = s[i+1:].strip()
    while s[0] != "}":
        sexp, s = eat_value(s)
        if sexp:
            s = s.strip()
            body.append(sexp)

    return ["fn", vars] + body, s[1:]

def eat_value(s):
    """
    Eat a value in general. Will choose from other "eat_x"
    functions.
    """

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
    elif s.startswith("{"):
        return eat_function(s)
    else:
        sexp, s = eat_name(s)
        if sexp in ("#t", "#f", "#0"):
            sexp = {"#t": True, "#f": False, "#0": None}[sexp]
        return sexp, s

def parse(s):
    tree = []
    while s != "":
        sexp, s = eat_value(s)
        if sexp is not "":
            s = s.strip()
            tree.append(sexp)
    return tree

if __name__ == "__main__":
    import doctest
    doctest.testmod()
