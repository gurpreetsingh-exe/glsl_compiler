from .TokenTypes import LiteralKind
from .ast import *
from .Lexer import Literal, TokenKind

def constant_fold(ast):
    return walk(ast)

def walk(nodes):
    def binary(node: Binary):
        left = node.left
        right = node.right
        if isinstance(left, Binary):
            left = binary(left)

        if isinstance(right, Binary):
            right = binary(right)

        if type(left) == Literal and type(right) == Literal:
            if node.op.typ == TokenKind.PLUS:
                return Literal(LiteralKind.FLOAT, float(left.value) + float(right.value))
            elif node.op.typ == TokenKind.MINUS:
                return Literal(LiteralKind.FLOAT, float(left.value) - float(right.value))
            elif node.op.typ == TokenKind.STAR:
                return Literal(LiteralKind.FLOAT, float(left.value) * float(right.value))
            elif node.op.typ == TokenKind.SLASH:
                return Literal(LiteralKind.FLOAT, float(left.value) / float(right.value))
            else:
                assert False
        else:
            node.left = left
            node.right = right
            return node

    def assign(node):
        ty = type(node.init)
        if ty == Binary:
            node.init = binary(node.init)
        return node

    for i in range(len(nodes)):
        node = nodes[i]
        ty = type(node)
        if ty == FnDef:
            node.body = walk(node.body)
        elif ty == Binary:
            nodes[i] = binary(node)
        elif ty == Assign:
            nodes[i] = assign(node)
        elif ty == Decl:
            nodes[i].expr = assign(node.expr)

    return nodes
