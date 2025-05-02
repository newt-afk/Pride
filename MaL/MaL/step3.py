"""
File: step3.py
Author: Zeno
Date: Wed 31 May 2023
Description: the 3rd step of the Make a Lisp language agnostic process tutorial
"""

import sys
import reader
import printer
from env import Env
import malTypes as mt

replenv = Env(None)

replenv.set("+", lambda a,b:a+b)
replenv.set("-", lambda a,b:a-b)
replenv.set('*', lambda a,b:a*b)
replenv.set('/', lambda a,b: int(a/b))

def evalast(ast, env):
    if type(ast) == mt.Symbol:
        return env.get(ast)
    elif type(ast) is list:
        ret = []
        for e in ast: ret.append(EVAL(e, env))
        return ret
    else: return ast
def READ(s):
    return reader.readstr(s)

def EVAL(s, env):
    if type(s) is list and len(s) > 0:
        if s[0] == mt.Symbol("def!"):
            a1, a2 = s[1], s[2]
            return env.set(a1, EVAL(a2, env))
        elif s[0] == mt.Symbol("let*"):
# explanation of let keyword: you create 2 lists, the first defining the special enviroment, and the second to run in the enviroment
            retenv = Env(env)
            a1, a2 = s[1], s[2]
            for i in range(0, len(a1), 2): retenv.set(a1[i], EVAL(a1[i+1], retenv))
            return EVAL(a2, retenv)
        else:
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
