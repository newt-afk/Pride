"""
File: reader.py
Author: Zeno
Date: Wed 31 May 2023
Description: Make a Lisp language agnostic tutorial file to contain reader functions
"""

import re
import malTypes as mt

class Reader: # container to slowly deal with tokens. Not for use outside
    def __init__(self, tokens):
        self.pointer, self.tokens = 0, tokens

    def next(self) -> str: # advances the pointer
        if self.pointer < len(self.tokens):
            self.pointer += 1
            return self.tokens[self.pointer - 1]
        else:
            return ""

    def peek(self) -> str: # returns token under pointer
        return self.tokens[self.pointer] if self.pointer < len(self.tokens) else ""

def readstr(text: str): # main function other modules use.
    tokens= tokenize(text)
    if tokens == []: return None
    return readForm(Reader(tokens))

def tokenize(text: str): # tokenises the input, using regex
    tre = re.compile(r"""[\s,]*(~@|[\[\]{}()'`~^@]|"(?:[\\].|[^\\"])*"?|;.*|[^\s\[\]{}()'"`@,;]+)""") # Regex from Make a Lisp tutorial
    return [t for t in re.findall(tre, text) if t[0] != ';'] 

def readForm(reader: Reader): # main function doing any work
    token = reader.next()
    if token[0] == ';': # ; denotes comments
        reader.next()
        return

    # short forms for lengthy tokens. This just expands them
    if token == '@': return [mt.Symbol('deref'), readForm(reader)]
    if token == "'": return [mt.Symbol('quote'), readForm(reader)]
    if token == '`': return [mt.Symbol('quasiquote'), readForm(reader)]
    if token == '~': return [mt.Symbol('unquote'), readForm(reader)]
    if token == '~@': return [mt.Symbol('splice-unquote'), readForm(reader)]
    if token == "^": 
        t1, t2 = readForm(reader), readForm(reader)
        return [mt.Symbol("with-meta"), t2, t1]

    # actual things to return
    # These are just for the sequentials
    if token in ') ] }'.split(): raise Exception(f"unexpected '{token}'")
    if token == "(": return readList(reader, ")")
    if token == "[": return mt.Vector(readList(reader, "]"))
    if token == "{": return mt.makeMap(*readList(reader, "}"))
    # this is for anything other than lists and small stuff
    return readAtom(token)

def readList(reader: Reader, end: str) -> list: # sole purpose is to read lists and similar
    ret = []
    while reader.peek() != end : 
        if not reader.peek(): raise Exception(f"expected '{end}', got EOF")
        ret.append(readForm(reader))
    reader.next()
    return ret

def _unescape(s: str) -> str:
    # only for use on input strings
    return s.replace('\\\\', '\u029e').replace('\\"', '"').replace('\\n', '\n').replace( '\u029e', '\\')

def readAtom(token: str): # for tokens that don't have other tokens in them
    if not token: raise Exception("EOF")
    inttype = re.compile(r"-?[0-9]+$")
    stringtype = re.compile(r'"(?:[\\].|[^\\"])*"')
    if re.match(inttype, token): return int(token)
    if re.match(stringtype, token): return _unescape(token[1:-1])
    if token == "true": return True
    if token == "false": return False
    if token == "nil": return None
    if token[0] == ":": return mt.keyword(token[1:])
    return mt.Symbol(token)
