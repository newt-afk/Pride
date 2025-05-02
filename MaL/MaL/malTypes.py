"""
File: types.py
Author: Zeno
Date: Fri 02 Jun 2023
Description: Holds definitions and redefinitions of types based on the Make a Lisp tutorial
"""
import types, copy
class Symbol(str): pass # symbols are just fancy strings
def _symbol(s: str) -> Symbol: return Symbol(s) # turns a string into a symbol

def keyword(s: str) -> str: return s if s[0] == "\u029e" else "\u029e"+s

class List(list): pass # basically no difference, except thjs can hold attributes.

class Vector(list): pass # basically just a list. Treated differently in lisp

class Hashmap(dict): pass # basically just a dict. 
def makeMap(*vals) -> Hashmap: # compiles values into a map
    hashmap = Hashmap()
    if len(vals) % 2 != 0: raise Exception("Unmatched key in map")
    for i in range(0, len(vals), 2): hashmap[vals[i]] = vals[i+1]
    return hashmap

class Atom: # basically just a pointer, but without memory
    def __init__(self, val):
        self.val = val

def clone(t): #need this to not pass by reference
    if callable(t):
        f = types.FunctionType(
                    t.__code__, t.__globals__, name = t.__name__,
                    argdefs = t.__defaults__, closure = t.__closure__)
        f.__dict__ = copy.copy(t.__dict__)
        return f
    else:
        return copy.copy(t)

def pythontolisp(t):
    if type(t) in (list, tuple):
        return Vector(t)
    if type(t) is dict:
        return Hashmap(t)
    if type(t) not in (int, str, None, type(True)):
        raise Exception("invalid type for lisp: " + type(t))
    return t
