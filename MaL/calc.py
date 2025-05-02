"""
File: proofOC.py
Author: Zeno
Date: Thu 25 May 2023
Description: proof of concept for smaller portions of the language
"""
import sys

INTEGER, ADD, SUB, DIV, MUL, LPAREN, RPAREN, EOF= 'INTEGER', 'ADD', 'SUB', 'DIV', 'MUL','(', ')', 'EOF' 

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(type=self.type,value=repr(self.value))
    def __repr__(self):
        return self.__str__()

class Lexer(object):
    def __init__(self, text):
        self.text = text
        if text == 'exit': sys.exit()
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):self.current_char =None
        else: self.current_char = self.text[self.pos]

    def skipspaces(self):
        while self.current_char is not None and self.current_char.isspace(): self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def nextToken(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skipspaces()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char == "+":
                self.advance()
                return Token(ADD, '+')
            if self.current_char == '-':
                self.advance()
                return Token(SUB, '-')
            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')
            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            self.error()
        return Token(EOF, None)

class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.nextToken()

    def error(self):
        raise Exception("Invalid Syntax")

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.nextToken()
        else:
            self.error()

    def factor(self):
        token = self.current_token
        if token.type == INTEGER:
            self.eat(INTEGER)
            return token.value
        elif token.type == LPAREN:
            self.eat(LPAREN)
            result = self.expr()
            self.eat(RPAREN)
            return result
        else:
            raise Exception("Bad arguments")

    def term(self):
        term = self.factor()
        while self.current_token.type in (MUL, DIV):
            if self.current_token.type == MUL:
                self.eat(MUL)
                term *= self.factor()
            else:
                self.eat(DIV)
                term /= self.factor()
        return term
                

    def expr(self):
        result = self.term()
        while self.current_token.type in (SUB,ADD):
            if self.current_token.type == ADD:
                self.eat(ADD)
                result += self.term()
            else:
                self.eat(SUB)
                result -= self.term()
        return result

def main():
    while True:
        try:
            text = input("calc> ")
        except EOFError:
            break
        if not text:
            continue
        intepreter = Interpreter(Lexer(text))
        result = intepreter.expr()
        print(result)

if __name__ == '__main__':
    main()
