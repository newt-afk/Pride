"""
File: step1.py
Author: Zeno
Date: Wed 31 May 2023
Description: the 1st step of the Make a Lisp language agnostic process tutorial
"""

import sys
import reader
import printer
import malTypes

def READ(s):
    return reader.readstr(s)

def EVAL(s):
    return s

def PRINT(s):
    return printer.prStr(s)

def rep(s):
    if s == "exit": sys.exit()
    return PRINT(EVAL(READ(s)))

def main():
    while True:
        try:
            print(rep(input("user> ")))
        except EOFError :
            sys.exit()

if __name__ == "__main__":
    main()
