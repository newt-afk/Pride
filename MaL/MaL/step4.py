"""
File: step4.py
Author: Zeno
Date: Wed 31 May 2023
Description: the 4th step of the Make a Lisp language agnostic process tutorial
"""

import sys
import reader, printer, core
from env import Env
import malTypes as mt

replenv = Env()
replenv.data = core.ns

def evalast(ast, env):
    if type(ast) == mt.Symbol:
        return env.get(ast)
    elif type(ast) is list:
        ret = []
        for e in ast: ret.append(EVAL(e, env))
        return ret
    elif type(ast) is mt.Vector:
        ret = []
        for e in ast: ret.append(EVAL(e, env))
        return ret
    elif type(ast) is mt.Hashmap:
        return mt.Hashmap((k, EVAL(v, env)) for k, v in ast.items())
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
        elif s[0] == mt.Symbol("do"):
            return evalast(s[1:], env)[-1]
        elif s[0] == mt.Symbol("if"):
# checks the first parameter, and if it isn't false, returns the second. Otherwise, evaluate the third parameter
# evaluates None type if the third parameter doesn't exist
            return (EVAL(s[3], env) if len(s)==4 else None) if EVAL(s[1], env) in [None, False] else EVAL(s[2], env)
        elif s[0] == mt.Symbol("fn*"):
        # returns a function, which makes use of the env functions to set parameters, which we use the evaluate the expression
            return lambda *args: EVAL(s[2], Env(env, s[1], list(args)))
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
