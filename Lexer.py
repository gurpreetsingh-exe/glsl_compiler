from .TokenTypes import *

class Literal:
    def __init__(self, typ, value):
        self.typ = typ
        self.value = value

class Token:
    def __init__(self, typ, value):
        self.typ = typ
        self.value = value
        self.raw = str(self.value)

    def __repr__(self):
        return f"{str(self.typ).ljust(16)}\t=> `{str(self.value)}`"

class Lexer:
    def __init__(self, program):
        self.program = program
        self.id = 0
        self.curr_char = self.program[self.id]

    def advance(self):
        self.id += 1
        self.curr_char = self.program[self.id] if self.id < len(self.program) else None

    def lex_word(self, method):
        buffer = ''

        while self.curr_char != None and method(self) and (not self.curr_char.isspace()):
            buffer += self.curr_char
            self.advance()

        return buffer

    def lexfile(self):
        while self.curr_char != None:
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
                yield Token(TokenKind.LITERAL, lit)

            elif self.curr_char.isalpha() or self.curr_char == "_":
                word = self.lex_word(lambda self: self.curr_char.isalnum() or self.curr_char == "_")

                if word in Keywords:
                    yield Token(Keywords[word], word)
                elif word in Types:
                    yield Token(TokenKind.TYPE, Types[word])
                elif word in {'true', 'false'}:
                    lit = Literal(LiteralKind.BOOL, word)
                    yield Token(TokenKind.LITERAL, lit)
                else:
                    yield Token(TokenKind.IDENT, word)

            elif self.curr_char in Punctuators:
                prev = self.curr_char
                self.advance()
                compound = prev + self.curr_char
                if compound == "//":
                    while self.curr_char != "\n":
                        self.advance()
                    continue

                if compound in Punctuators:
                    yield Token(Punctuators[compound], compound)
                    self.advance()
                else:
                    yield Token(Punctuators[prev], prev)

            else:
                assert False, "unreachable"
