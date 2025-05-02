"""
File: stepA.py
Author: Zeno
Date: Wed 31 May 2023
Description: the 10th and final step of the Make a Lisp language agnostic process tutorial
"""
import sys # outside libraries
import reader, printer, core, malTypes as mt # personally created files
from env import Env # env.Env is confusing

#this is the core enviroment for the program. It defines functions more or less
replenv = core.corenv() # env defined in core
# for if you run this as a launcher, this is how you pass in arguments.
replenv.set("*ARGV*", [] if len(sys.argv) < 2 else sys.argv[2:])
replenv.set("*host-language*", "Python")

# macros: functions with the macro label on them. This means that they are evaluated before anything else
# This just asks whether or not the [A]bstract [S]yntax [T]ree is a macro call, using a given enviroment
def ismacrocall(ast, env):
    # in list and mt.List because of laziness on something i don't care much about. 
    if type(ast) in (list, mt.List) and ast and type(ast[0]) is mt.Symbol:
        e = env.find(ast[0])
        if e: return hasattr(env.get(ast[0]), "ismacro") and env.get(ast[0]).ismacro
    return False

# This is how macros are evaluated. 
def macroexpand(ast, env):
    while ismacrocall(ast, env):
        if callable(env.get(ast[0])):
            ast = env.get(ast[0])(*ast[1:])
    return ast

# quasiquotes: more powerful versions of quotes, which delay evaluation until it's needed later.
# they also have more special tokens: splice-unquote which splices things together and then unquotes them
# and unquote, which marks a token to be evaluated
def quasiquoteqlist(seq): # quasiquote a quoted list basically
    ret = []
    for i in range(len(seq), 0, -1):
        elt = seq[i - 1]
        if type(elt) in (list, mt.List) and elt and elt[0] == mt.Symbol("splice-unquote"):
            return [mt.Symbol("concat"), elt[1], ret]
        else:
            ret =[mt.Symbol("cons"), quasiquote(elt), ret]
    return ret

# This is takes in a token and quasiquotes it
def quasiquote(ast):
    if type(ast) in (list, mt.List) and len(ast) > 0:
        if ast[0] == mt.Symbol("unquote"):
            return ast[1]
        else:
            return quasiquoteqlist(ast)
    elif type(ast) in (mt.Hashmap, mt.Symbol):
        return [mt.Symbol("quote"), ast]
    elif type(ast) is mt.Vector:
        return [mt.Symbol('vec'), quasiquoteqlist(ast)]
    else:
        # anything else doesn't need any special processing
        return ast

##### START OF MAIN FUNCTIONS
#### These make up the REPL loop, and stuff. They are no longer just helpers

# takes in a token, and figures out how to deal with them.
def evalast(ast, env):
    if type(ast) == mt.Symbol:
        return env.get(ast)
    elif type(ast) in (list, mt.List, mt.Vector):
        ret = []
        for e in ast: ret.append(EVAL(e, env))
        return mt.Vector(ret) if type(ast) is mt.Vector else ret
    elif type(ast) is mt.Hashmap:
        return mt.Hashmap((k, EVAL(v, env)) for k, v in ast.items())
    else: return ast

# hands parsing off to the reader file.
def READ(s):
    return reader.readstr(s)

# handles cases where the enviroment is being changed in some way, or the evaluation of functions.
def EVAL(s, env):
    # loop allows for Tail Call Optimization. reduces the recursion level of the function, turns functions that just call themselves at the end into loops
    while True:
        s = macroexpand(s, env)
        if type(s) is list and len(s) > 0:
            if s[0] == mt.Symbol("def!"): # basically just how to declare variables, except functions can be assigned to variables.
                a1, a2 = s[1], s[2]
                return env.set(a1, EVAL(a2, env))
            elif s[0] == mt.Symbol("defmacro!"): # similar to above, but for macros specifically.
                func = mt.clone(EVAL(s[2], env)) # this undoes pythons pass by reference.
                setattr(func, "ismacro", True) # all this does is set the attribute for the thing
                return env.set(s[1], func)
            elif s[0] == mt.Symbol("let*"): # defines a special enviroment for the rest of the list to execute in.
                tenv = Env(env)
                for i in range (0, len(s[1]), 2):
                    tenv.set(s[1][i], EVAL(s[1][i+1], tenv))
                s, env = s[2], tenv
            elif s[0] == mt.Symbol("do"): # evaluates everything in the list, and return only the last elements evaluation
                evalast(s[1:-1], env)
                s = s[-1]
            elif s[0] == mt.Symbol("if"): #if statement with optional else parameter
                s = (s[3] if len(s) >= 4 else None) if EVAL(s[1], env) in [0, None, False] else s[2]
            elif s[0] == mt.Symbol("fn*"): # how to declare functions. They are not named by default
            # returns a function, which makes use of the env functions to set parameters, which we use the evaluate the expression
                func = lambda *args: EVAL(s[2], Env(env, s[1], list(args)))
                func.ast = s[2] # cursed, assigning attributes to function so i can treat it as function first, object second
                func.ismacro = False
                func.params = s[1]
                func.env = env
                func.fn = func
                return func
            elif s[0] == mt.Symbol("quote"): # marks a token to not be evaluated
                return s[1]
            elif s[0] == mt.Symbol("quasiquoteexpand"): # mostly for debugging quasiquote.
                return quasiquote(s[1])
            elif s[0] == mt.Symbol("quasiquote"): # quasiquote, allows use of tokens to play with quoted lists
                s = quasiquote(s[1])
            elif s[0] == mt.Symbol('macroexpand'): # again, mostly for debugging macros.
                return macroexpand(s[1], env)
            elif s[0] == mt.Symbol('catch*'): # error messages :D
                raise Exception("unexpected catch for nonexistant try")
            elif s[0] == mt.Symbol('try*'): # for try catch statements.
                if len(s) > 2 and s[2][0] == mt.Symbol("catch*"):
                    try:
                        return EVAL(s[1], env)
                    except Exception as e:
                        tenv = env
                        tenv.set(s[2][1], str(e))
                        s, env = s[2][2], tenv
                else:
                    s = s[1]
            else: # if all else fails; search the enviroment for the first token
                l = evalast(s, env)
                if not l: return l
                if hasattr(l[0], 'ast') and hasattr(l[0], 'env'):
                    s = l[0].ast
                    env = Env(l[0].env, l[0].params, l[1:])
                else: return l[0](*l[1:])
        else: return evalast(s, env) if s else s # for non-list tokens.

def PRINT(s): # turns tokens into strings. handed off to the printer.
    return printer.prStr(s, True)

helpstring = """
Welcome to MaL!
To use a function, simply put it at the front of the list, with the rest of the list being the parameters. 
Data types:
numbers, strings, true, false, nil are all normal. Mean what they think you mean.
(list), [vector], {map}, :key
For better help with how to use MaL, look at the MaLHelp file!
"""
def rep(s, env): # this runs stuff.
    if s == "exit": sys.exit() # mainly for the repl, but can probably be used in programs as well. just exits when reads exit on a line by itself
    if s == "help": print(helpstring)
    else: return PRINT(EVAL(READ(s), env))

## defining core functions in mal itself. Slightly faster
replenv.set("eval", lambda ast: EVAL(ast, replenv)) # in language support for executing lists
#I tried actually implementing this in python, it's more trouble than it's worth when this works and is recommended
rep("""(def! load-file (fn* (f) (eval (read-string (str "(do " (slurp f) "\nnil)")))))""", replenv) # reads file name, loads file, and attempts to execute it as MaL.
rep("(defmacro! cond (fn* (& xs) (if (> (count xs) 0) (list 'if (first xs) (if (> (count xs) 1) (nth xs 1) (throw \"odd number of forms to cond\")) (cons 'cond (rest (rest xs)))))))", replenv)
# this takes pairs of arguments, the first of the pair evaluates to true or false, and the second is run if the first is true. Effectively, it's a switch statement

if len(sys.argv) > 1: # checks for arguments passed in, and try to interpret it was mal files
    rep(f'(load-file "{sys.argv[1]}")', replenv) # this is how you would load a file using mal. It's convenient.
    sys.exit()


def main():
    while True:
        try:
            print(rep(input("user> "), replenv))
        except EOFError :
            sys.exit()
#        except Exception as e:
#            print("Exception: " + str(e))
if __name__ == "__main__":
    print("If it's your first time, read the help file!\nIf you just need a quick refresh on the very basics, type help!")
    rep("(println (str \"Mal [\" *host-language* \"]\"))", replenv) # show off which language mal was implemented in.
    main()
