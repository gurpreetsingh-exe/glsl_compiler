from copy import deepcopy
from .TokenTypes import *

class Literal:
    def __init__(self, typ, value):
        self.typ = typ
        self.value = value

class Location:
    def __init__(self):
        self.line = 0
        self.col = 0

    def __repr__(self):
        return f"{self.line}:{self.col}"

    def bump_line_reset(self):
        self.line += 1
        self.col = 0

    def bump_col(self):
        self.col += 1

class Token:
    def __init__(self, typ, value, loc=Location()):
        self.typ = typ
        self.value = value
        self.raw = str(self.value)
        self.loc = loc

    def __repr__(self):
        return f"{self.loc}: {str(self.typ).ljust(16)}\t=> `{str(self.value)}`"

class Lexer:
    def __init__(self, program):
        self.program = program
        self.id = 0
        self.curr_char = self.program[self.id]
        self.loc = Location()

    def advance(self):
        self.id += 1
        self.curr_char = self.program[self.id] if self.id < len(self.program) else None
        if self.curr_char == "\n":
            self.loc.bump_line_reset()
        else:
            self.loc.bump_col()

    def lex_word(self, method):
        buffer = ''

        while self.curr_char != None and method(self) and (not self.curr_char.isspace()):
            buffer += self.curr_char
            self.advance()

        return buffer

    def lexfile(self):
        while self.curr_char != None:
            loc = deepcopy(self.loc)
            if self.curr_char.isspace():
                self.advance()
                continue

            elif self.curr_char.isdigit():
                word = self.lex_word(lambda self: self.curr_char.isdigit() or self.curr_char == ".")
                try:
                    int(word)
                    typ = LiteralKind.INT
                except ValueError:
                    float(word)
                    typ = LiteralKind.FLOAT

                lit = Literal(typ, str(word))
                yield Token(TokenKind.LITERAL, lit, loc)

            elif self.curr_char.isalpha() or self.curr_char == "_":
                word = self.lex_word(lambda self: self.curr_char.isalnum() or self.curr_char == "_")

                if word in Keywords:
                    yield Token(Keywords[word], word, loc)
                elif word in Types:
                    yield Token(TokenKind.TYPE, Types[word], loc)
                elif word in {'true', 'false'}:
                    lit = Literal(LiteralKind.BOOL, word)
                    yield Token(TokenKind.LITERAL, lit, loc)
                else:
                    yield Token(TokenKind.IDENT, word, loc)

            elif self.curr_char in Punctuators:
                prev = self.curr_char
                self.advance()
                compound = prev + self.curr_char
                if compound == "//":
                    while self.curr_char != "\n":
                        self.advance()
                    continue

                if compound in Punctuators:
                    yield Token(Punctuators[compound], compound, loc)
                    self.advance()
                else:
                    yield Token(Punctuators[prev], prev, loc)

            else:
                assert False, "unreachable"
