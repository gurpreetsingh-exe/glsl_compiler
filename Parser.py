from .Lexer import TokenKind, Token
from .ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.id = 0
        self.curr_tok = self.tokens[self.id]

        self.state = True

    def advance(self):
        if self.id < len(self.tokens) - 1:
            self.id += 1
            self.curr_tok = self.tokens[self.id]
        else:
            self.curr_tok = Token(TokenKind.EOF, None)

    def error(self, msg):
        self.state = False
        print(msg)

    @property
    def keepParsing(self):
        return self.curr_tok != TokenKind.EOF and self.state

    def peek(self):
        if self.id < len(self.tokens) - 1:
            return self.tokens[self.id + 1]
        else:
            return Token(TokenKind.EOF, None)

    def expect(self, typ):
        self.advance()
        if self.curr_tok.typ != typ:
            self.error(f"Expected `{typ}` but got `{self.curr_tok.typ}` ({self.curr_tok.value})")
        return self.curr_tok

    def expect_curr(self, typ):
        tok = self.curr_tok
        if tok.typ != typ:
            self.error(f"Expected `{typ}` but got `{tok.typ}` ({tok.value})")
        self.advance()
        return tok

    def func_arg(self):
        """
        Parses only one function arg in a function signature
        """
        prop = None
        if self.curr_tok.typ not in {TokenKind.IN, TokenKind.OUT, TokenKind.INOUT, TokenKind.TYPE}:
            self.error(f"Expected `in`, `out`, `inout`, or a type but got `{self.curr_tok.value}`")
            return

        if self.curr_tok.typ == TokenKind.TYPE:
            typ = self.curr_tok.value
        else:
            prop = self.curr_tok.typ
            typ = self.expect(TokenKind.TYPE).value

        name = self.expect(TokenKind.IDENT).value
        self.advance()
        return FnArg(name, typ, prop)

    def func_args(self):
        """
        Parses all function args for a function definition

        this method expects curr_tok to be `(` and parses
        the args till it reaches the end of file or a `)`
        """
        self.advance()
        args = []
        while self.keepParsing and self.curr_tok.typ != TokenKind.RPAREN:
            args.append(self.func_arg())
            if self.curr_tok.typ == TokenKind.RPAREN:
                break
            elif self.curr_tok.typ == TokenKind.COMMA:
                self.advance()
        self.advance()
        return args

    def block(self):
        self.expect_curr(TokenKind.LCURLY)
        while self.keepParsing and self.curr_tok.typ != TokenKind.RCURLY:
            yield from self.statement()
        self.expect_curr(TokenKind.RCURLY)

    def declaration(self):
        print(self.curr_tok)
        self.error("Stop in declaration")

    def item(self):
        """NOTE:
        might be:
        1. a function definition => `void function_name() {}`
        2. a var definition => `float a;`
        3. function params => `void function_name(int a, int b) {}`
        4. a function call => `vec3(1.0f);`
        5. or a type cast? (don't know if that's even possible in glsl)
            though in that case the expression starts with `(` => (int)var_name

        either way the type is followed by an identifier
        """
        typ = self.curr_tok.value
        self.advance()
        if self.curr_tok.typ == TokenKind.IDENT:
            # it could be 1, 2 or 3
            ident = self.curr_tok.value
            next_ = self.peek()
            if next_.typ == TokenKind.LPAREN:
                # it's a function definition
                self.advance()
                args = self.func_args()
                fn_sig = FnSig(ident, args, typ)
                body = list(self.block())
                yield FnDef(fn_sig, body)
            else:
                yield self.declaration()
        elif self.curr_tok.typ == TokenKind.LPAREN:
            # it's 4
            # this function expects an identifier so L
            return self.fn_call()
        else:
            # hmmmm this should be unreachable
            pass
        self.advance()

    def compound(self, tok_list, callback):
        left = callback()
        while self.keepParsing and self.curr_tok.typ in tok_list:
            op = self.curr_tok
            self.advance()
            right = callback()
            left = Binary(op, left, right)

        return left

    def assignment_expr(self):
        ident = self.expect_curr(TokenKind.IDENT).value
        self.expect_curr(TokenKind.EQ)
        init = self.expression()
        return Assign(ident, init)

    def fn_call(self):
        name = self.expect_curr(TokenKind.IDENT).value
        self.expect_curr(TokenKind.LPAREN)
        args = []
        while self.keepParsing and self.curr_tok.typ != TokenKind.RPAREN:
            args.append(self.expression())
            if self.curr_tok.typ == TokenKind.RPAREN:
                break
            self.expect_curr(TokenKind.COMMA)
        self.expect_curr(TokenKind.RPAREN)
        return Call(name, args)

    def primary(self):
        if self.curr_tok.typ == TokenKind.IDENT:
            next_ = self.peek()
            if next_.typ == TokenKind.LPAREN:
                return self.fn_call()
            else:
                curr = self.curr_tok
                self.advance()
                return Ident(curr.value)
        elif self.curr_tok.typ == TokenKind.LITERAL:
            return self.expect_curr(TokenKind.LITERAL).value

    def unary(self):
        if self.curr_tok.typ in [TokenKind.MINUS, TokenKind.BANG]:
            op = self.curr_tok
            self.advance()
            right = self.unary()
            return Unary(op, right)

        return self.primary()

    def factor(self):
        return self.compound([TokenKind.STAR, TokenKind.SLASH], self.unary)

    def term(self):
        return self.compound([TokenKind.PLUS, TokenKind.MINUS], self.factor)

    def comparison(self):
        return self.compound([TokenKind.LT, TokenKind.GT], self.term)

    def assign(self):
        left = self.comparison()
        if self.curr_tok.typ == TokenKind.EQ:
            self.advance()
            init = self.assign()
            if isinstance(left, Ident):
                return Assign(left.name, init)
            else:
                self.error(f"Assignment expression expected `Ident` but got `{left}`")
        return left

    def expression(self):
        return self.compound([TokenKind.BANGEQ, TokenKind.EQ2], self.assign)

    def expr_stmt(self):
        while self.keepParsing and True:
            yield self.expression()
            if self.curr_tok.typ == TokenKind.SEMI:
                break
            elif self.curr_tok.typ == TokenKind.COMMA:
                self.advance()
        self.expect_curr(TokenKind.SEMI)

    def statement(self):
        if self.curr_tok.typ in {TokenKind.IDENT, TokenKind.LITERAL}:
            yield from self.expr_stmt()
        else:
            # Should hit this for EOF in some cases
            self.error("Not implemented")
            return

    def parse(self):
        while self.keepParsing:
            if self.curr_tok.typ == TokenKind.TYPE:
                yield from self.item()
            else:
                yield from self.statement()
