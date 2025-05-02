"""
File: step9.py
Author: Zeno
Date: Wed 31 May 2023
Description: the 9th step of the Make a Lisp language agnostic process tutorial
"""
import sys, traceback # outside libraries
import reader, printer, core, malTypes as mt # personally created files
from env import Env # env.Env is confusing

replenv = core.corenv() # env defined in core
replenv.set("eval", lambda ast: EVAL(ast, replenv)) # in language support for executing lists
replenv.set("*ARGV*", [] if len(sys.argv) < 2 else sys.argv[2:])

def ismacrocall(ast, env):
    if type(ast) == list and ast and type(ast[0]) is mt.Symbol:
        e = env.find(ast[0])
        if e: return hasattr(env.get(ast[0]), "ismacro") and env.get(ast[0]).ismacro
    return False

def macroexpand(ast, env):
    while ismacrocall(ast, env):
        if callable(env.get(ast[0])):
            ast = env.get(ast[0])(*ast[1:])
    return ast

def quasiquoteqlist(seq): # quasiquote a quoted list basically
    ret = []
    for i in range(len(seq), 0, -1):
        elt = seq[i - 1]
        if type(elt) is list and elt and elt[0] == mt.Symbol("splice-unquote"):
            return [mt.Symbol("concat"), elt[1], ret]
        else:
            ret =[mt.Symbol("cons"), quasiquote(elt), ret]
    return ret

def quasiquote(ast):
    if type(ast) is list and len(ast) > 0:
        if ast[0] == mt.Symbol("unquote"):
            return ast[1]
        else:
            return quasiquoteqlist(ast)
    elif type(ast) in (mt.Hashmap, mt.Symbol):
        return [mt.Symbol("quote"), ast]
    elif type(ast) is mt.Vector:
        return [mt.Symbol('vec'), quasiquoteqlist(ast)]
    else:
        return ast

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
        return mt.Vector(ret)
    elif type(ast) is mt.Hashmap:
        return mt.Hashmap((k, EVAL(v, env)) for k, v in ast.items())
    else: return ast
def READ(s):
    return reader.readstr(s)

def EVAL(s, env):
    while True:
        s = macroexpand(s, env)
        if type(s) is list and len(s) > 0:
            if s[0] == mt.Symbol("def!"):
                a1, a2 = s[1], s[2]
                return env.set(a1, EVAL(a2, env))
            elif s[0] == mt.Symbol("defmacro!"):
                func = EVAL(s[2], env)
                if hasattr(func, "ismacro"): func.ismacro = True
                return env.set(s[1], func)
            elif s[0] == mt.Symbol("let*"):
                tenv = Env(env)
                for i in range (0, len(s[1]), 2):
                    tenv.set(s[1][i], EVAL(s[1][i+1], tenv))
                s, env = s[2], tenv
            elif s[0] == mt.Symbol("do"):
                evalast(s[1:-1], env)
                s = s[-1]
            elif s[0] == mt.Symbol("if"):
    # checks the first parameter, and if it isn't false, uses the second param. Otherwise, evaluate the third parameter
    # evaluates None type if the third parameter doesn't exist. This is basically an if else statement that chains for else if
                s = (s[3] if len(s) >= 4 else None) if EVAL(s[1], env) in [None, False] else s[2]
            elif s[0] == mt.Symbol("fn*"):
            # returns a function, which makes use of the env functions to set parameters, which we use the evaluate the expression
                func = lambda *args: EVAL(s[2], Env(env, s[1], list(args)))
                func.ast = s[2] # cursed, assigning attributes to function so i can treat it as function first, object second
                func.ismacro = False
                func.params = s[1]
                func.env = env
                func.fn = func
                return func
            elif s[0] == mt.Symbol("quote"):
                return s[1]
            elif s[0] == mt.Symbol("quasiquoteexpand"):
                return quasiquote(s[1])
            elif s[0] == mt.Symbol("quasiquote"):
                s = quasiquote(s[1])
            elif s[0] == mt.Symbol('macroexpand'):
                return macroexpand(s[1], env)
            elif s[0] == mt.Symbol('catch*'):
                raise Exception("unexpected catch for nonexistant try")
            elif s[0] == mt.Symbol('try*'):
                if len(s) > 2 and s[2][0] == mt.Symbol("catch*"):
                    try:
                        return EVAL(s[1], env)
                    except Exception as e:
                        tenv = env
                        tenv.set(s[2][1], str(e))
                        return EVAL(s[2][2], tenv)
                else:
                    EVAL(s[1], env)
            else:
                l = evalast(s, env)
                if not l: return l
                if hasattr(l[0], 'ast') and hasattr(l[0], 'env'):
                    s = l[0].ast
                    env = Env(l[0].env, l[0].params, l[1:])
                else: return l[0](*l[1:])
        else: return evalast(s, env) if s else s

def PRINT(s):
    return printer.prStr(s, True)

def rep(s, env):
    if s == "exit": sys.exit()
    return PRINT(EVAL(READ(s), env))
rep("""(def! load-file (fn* (f) (eval (read-string (str "(do " (slurp f) "\nnil)")))))""", replenv) #defining a function for Mal in MaL
rep("(defmacro! cond (fn* (& xs) (if (> (count xs) 0) (list 'if (first xs) (if (> (count xs) 1) (nth xs 1) (throw \"odd number of forms to cond\")) (cons 'cond (rest (rest xs)))))))", replenv)
#I tried actually implementing this in python, it's more trouble than it's worth when this works.
if len(sys.argv) > 1:
    rep(f'(load-file "{sys.argv[1]}")', replenv)
    sys.exit()

def main():
    while True:
        try:
            print(rep(input("user> "), replenv))
        except EOFError :
            sys.exit()
        except Exception as e:
            print("Exception: " + str(e))
if __name__ == "__main__":
    main()
