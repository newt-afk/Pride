"""
File: step2.py
Author: Zeno
Date: Wed 31 May 2023
Description: the 2st step of the Make a Lisp language agnostic process tutorial
"""

import sys
import reader
import printer
import malTypes as mt

replenv = {
        '+': lambda a,b:a+b,
        '-': lambda a,b:a-b,
        '*':lambda a,b:a*b,
        '/':lambda a,b: int(a/b)
}
def evalast(ast, env):
    if type(ast) == mt.Symbol:
        if ast in env.keys():
            return env.get(ast)
        else: raise Exception("Unrecognised Symbol")
    elif type(ast) is list:
        ret = []
        for e in ast: ret.append(EVAL(e, env))
        return ret
    elif type(ast) is mt.Vector:
        ret = []
        for e in ast: ret.append(EVAL(e, env))
        return mt.Vector(ret)
    elif type(ast) is mt.Hashmap:
        return mt.Hashmap((k, EVAL(v, env)) for k, v in ast.items())
    else: return ast
def READ(s):
    return reader.readstr(s)

def EVAL(s, env):
    if type(s) is list and len(s) > 0:
        l = evalast(s, env)
        return l[0](*l[1:])
    return evalast(s, env) if s else s

def PRINT(s):
    return printer.prStr(s, True)

def rep(s, env):
    if s == "exit": sys.exit()
    return PRINT(EVAL(READ(s), env))

def main():
    while True:
        try:
            print(rep(input("user> "), replenv))
        except EOFError :
            sys.exit()

if __name__ == "__main__":
    main()
