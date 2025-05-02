"""
File: printer.py
Author: Zeno
Date: Thu 01 Jun 2023
Description: does the printing for the language agnostic tutorial make a lisp
"""
import malTypes as mt

def _escape(s: str) -> str: # sanitises stuff
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def prStr(stuff, readable: bool) -> str: # turns a token into a string
    if type(stuff) in (list, mt.List):
        return '(' + " ".join(map(lambda e: prStr(e, readable), stuff))+")"
    if type(stuff) is mt.Vector:
        return '[' + " ".join(map(lambda e: prStr(e, readable), stuff))+"]"
    if type(stuff) is mt.Hashmap:
        ret = []
        for k in stuff.keys():
            ret.extend((prStr(k, True), prStr(stuff[k], readable)))
        return "{" + " ".join(ret) + "}"
    if type(stuff) == str:
        if len(stuff) > 0 and stuff[0] == '\u029e': return ':' + stuff[1:]
        elif readable: return '"' + _escape(stuff) + '"'
        else: return stuff
    if stuff == None:
        return "nil"
    if type(stuff) == bool:
        return "true" if stuff else "false"
    if callable(stuff): return "#<function>"
    if type(stuff) is mt.Atom:
        return "(atom " + prStr(stuff.val, readable) + ")"
    else: # this includes things i haven't implemented, ints, and symbols.
        return str(stuff)
