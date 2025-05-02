"""
File: env.py
Author: Zeno
Date: Wed 07 Jun 2023
Description: holds functions and classes related to the enviroment of execution for the Make a Lisp tutorial
"""
import malTypes as mt

class Env():
    def __init__(self, outer=None, binds=None, exprs=None) -> None: # outer is the enviroment it inherits from. binds is a list of symbols. exprs is the things the symbols are bound to.
        self.data = {}
        self.outer = outer
        if binds:
            for i in range(len(binds)):
                if binds[i] == "&": # from clojure, the & token indicates that you wish to compile the rest of the arguments into a list, and put them in the next bind.
                    self.data[binds[i+1]] = exprs[i:] # this may throw a warning, it runs fine. Python doesn't trust me; i do.
                    break
                else:
                    self.data[binds[i]] = exprs[i] # as above

    def set(self, symbol, value): # takes a symbol, a value, and binds them together in the enviroment
        self.data[symbol] = value
        return value

    def find(self, symbol): # finds the enviroment in which the symbol passed in belongs to.
        if symbol in self.data.keys(): return self
        if self.outer: return self.outer.find(symbol)
        else: return None

    def get(self, symbol): # returns the value of a symbol
        e = self.find(symbol)
        if e:
            return e.data.get(symbol)
        raise Exception(symbol + " was not found.")
