"""
File: step5.py
Author: Zeno
Date: Wed 31 May 2023
Description: the 5th step of the Make a Lisp language agnostic process tutorial
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
    while type(s) is list and len(s) > 0:
        if s[0] == mt.Symbol("def!"):
            a1, a2 = s[1], s[2]
            return env.set(a1, EVAL(a2, env))
        elif s[0] == mt.Symbol("let*"):
            env = Env(env, s[::2], s[1::2]) # uses list splicing to create bind and expr lists, creating a new env
            s = s[2] 
        elif s[0] == mt.Symbol("do"):
            evalast(s[1:-1], env)
            s = s[-1]
        elif s[0] == mt.Symbol("if"):
# checks the first parameter, and if it isn't false, uses the second param. Otherwise, evaluate the third parameter
# evaluates None type if the third parameter doesn't exist. This is basically an if else statement that chains for else if
            s = (s[3] if len(s) == 4 else None) if EVAL(s[1], env) in [None, False] else s[2]
        elif s[0] == mt.Symbol("fn*"):
        # returns a function, which makes use of the env functions to set parameters, which we use the evaluate the expression
            func = lambda *args: EVAL(s[2], Env(env, s[1], list(args)))
            func.ast = s[2]
            func.params = s[1]
            func.env = env
            func.fn = func
            return func
        else:
            l = evalast(s, env)
            if not l: return l
            if hasattr(l[0], 'ast') and hasattr(l[0], 'env'):
                s = l[0].ast
                env = Env(l[0].env, l[0].params, l[1:])
            else: return l[0](*l[1:])
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
