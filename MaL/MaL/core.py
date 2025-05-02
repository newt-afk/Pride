"""
File: core.py
Author: Zeno
Date: Thu 08 Jun 2023
Description: Defines the core functions for the Make a Lisp tutorial
"""
from datetime import datetime, timezone
import malTypes as mt, printer as prt, reader, env

### functions too complex for a simple lambda.
def __equal(a,b): # compares 2 values
    if type(a) != type(b): return False
    if type(a) in (mt.Vector, list, mt.List):
        if len(a) != len(b): return False
        for i in a: 
            if a[i] != b[i]:return False
        return True
    if type(a) == mt.Hashmap:
        #map[key] is the same as map.get(key), and map[key]=val, as map.update({key,val})
        akeys, bkeys = sorted(a.keys()), sorted(b.keys())
        if len(akeys) != len(bkeys): return False
        for i in range (0, len(akeys)):
            if akeys[i] != bkeys[i] or not __equal(a[akeys[i]], b[bkeys[i]]): return False
        return True
    return a==b
            
def __reset(a:mt.Atom, b): # set the value for existing atoms
    a.val = b
    return b

def __swap(a: mt.Atom, f, *args): # set the value of atoms to the output of a function
    a.val = f(a.val, *args)
    return a.val

def __concat(*args: list) -> list: # concatanates elements into a list
    ret = []
    for lt in args: ret.extend(lt)
    return ret

def __nth(l, n: int): # gets the nth term out of a list or vector
    if len(l) > n and n >= 0:
        return l[n]
    else: raise Exception(f"Index {n} out of bounds for list {str(l)}")

def __throw(msg): # throws exceptions
    raise Exception(msg)

def __assoc(m, *args): # puts new key-value pairs into a map. associate them
    for i in range(0, len(args), 2):
        m[args[i]] = args[i+1]
    return m        

def __dissoc(m, *keys): # removes key-value pairs from a list. dissociate them.
    for key in keys: m.pop(key)
    return m

def __readline(msg: str): # allows for input in mal programs
    try:
        return input(msg)
    except EOFError:
        return None

def __wmeta(m, v): # creates meta attribute in m and associates it with v
    if callable(m):
        m = mt.clone(m)
        setattr(m, "meta", v)
    elif type(m) in (list, mt.Vector, mt.List, mt.Hashmap):
        if type(m) is list: m = mt.List(m) # because the normal list doesn't hold attributes. This does functionally nothing though.
        m = mt.clone(m)
        setattr(m, "meta", v)
    else:
        raise Exception(str(m), "is not a valid target for meta attributes")
    return m

def __conj(l, *args): # appends elements to vectors, prepends them to lists.
    if type(l) in (list, mt.List):
        return list(reversed(args)) + l
    elif type(l) is mt.Vector:
        return mt.Vector(l + mt.Vector(args))
    else:
        raise Exception(type(l) + " isn't supported by conj")

###MAIN PART OF PROGRAM
# where the symbols are associated with the corresponding values (all functions)
# ns stands for [n]ame[s]pace
ns = {
        # math
        "+": lambda a,b:a+b,
        "-": lambda a,b:a-b,
        "*": lambda a,b:a*b,
        "/": lambda a,b:a//b,
        "%": lambda a,b:a%b,
        "count": len,
        # conditionals
        "=": __equal,
        "<": lambda a,b:a<b,
        ">": lambda a,b:a>b,
        "<=": lambda a,b:a<=b,
        ">=": lambda a,b:a>=b,
        "list?": lambda l: type(l) in (list, mt.List),
        "vector?": lambda l: type(l) is mt.Vector,
        "sequential?": lambda l: type(l) in (list, mt.Vector),
        "atom?": lambda a: type(a) is mt.Atom,
        "map?": lambda m: type(m) is mt.Hashmap,
        "keyword?": lambda k: k[0] == '\u029e' if k else False,
        "symbol?": lambda s: type(s) is mt.Symbol,
        "string?": lambda s: type(s) is str and not (s and s[0] == '\u029e'),
        "number?": lambda n: type(n) in (int, float),
        "macro?": lambda m: hasattr(m, "ismacro") and m.ismacro,
        "fn?": lambda f: callable(f) and not (hasattr(f, "ismacro") and f.ismacro),
        "nil?": lambda a: a== None,
        "true?": lambda a: type(a) is type(True) and a,
        "false?": lambda a: type(a) is type(False) and not a,
        "contains?": lambda m, k: k in m.keys(),
        "empty?": lambda l: len(l) == 0,
        "not": lambda t: not t,
        # conversions
        "vector": lambda *args: mt.Vector(args), # this takes in a variable amount instead of just a list
        "list": lambda *args: list(args),
        "vec": lambda l: mt.Vector(l),
        "seq": lambda l: list(l) if l else None,
        "hash-map": mt.makeMap,
        "symbol": lambda s: mt.Symbol(s),
        "keyword": mt.keyword,
        "atom": lambda a: mt.Atom(a), # returns an atom (reference)
        "deref": lambda a: a.val, # given an atom, return its value
        "reset!": __reset,
        "swap!": __swap,
        # fun list operators
        "cons": lambda x, l: [x] + l,
        "concat": __concat,
        "nth": lambda l, n: __nth(l, n),
        "first": lambda l: l[0] if l else None,
        "rest": lambda l: l[1:] if l else [],
        "apply": lambda f, *args: f(*(list(args[:-1]) + args[-1])),
        "map": lambda f, l: list(map(f, l)),
        "conj": __conj,
        # fun map operators
        "assoc": __assoc,
        "dissoc": __dissoc,
        "get": lambda m, k: m[k] if m and k in m.keys() else None,
        "keys": lambda m: list(m.keys()),
        "vals": lambda m: list(m.values()),
        # string and file functions
# " ".join(*str) uses the string to join multiple other strings.
# map uses a function, applies it on a list, and returns the result of applying it to the elements
        # convert stuff into strings
        "pr-str": lambda *args: " ".join(map(lambda s: prt.prStr(s, True), args)),
        "str": lambda *args: "".join(map(lambda s: prt.prStr(s, False), args)),
        # input output operators
        "prn": lambda *args: print(" ".join(map(lambda s: prt.prStr(s, True), args))),
        "println": lambda *args: print(" ".join(map(lambda s: prt.prStr(s, False), args))),
        "read-string": reader.readstr,
        "slurp": lambda file: open(file).read(),
        "spit!": lambda file, msg: open(file, "w").write(msg),
        # meta funcs
        "meta": lambda m: m.meta if hasattr(m, "meta") else None,
        "with-meta": __wmeta,
        #error handling functions
        "throw": __throw,
        # generals
        "readline": __readline,
        "time-ms": lambda : datetime.now(timezone.utc).timestamp() * 1000,
        "python-eval": lambda s: mt.pythontolisp(eval(s))
        }

def corenv(): # returns an enviroment using ns
    e = env.Env()
    e.data = ns
    return e
