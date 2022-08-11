import bpy

from .ast import *
from .Lexer import Literal
from .TokenTypes import *

from typing import List

class NodeTree:
    def __init__(self, name, typ, _global=False):
        if _global:
            return
        self._node_tree = bpy.data.node_groups.new(type=typ, name=name)
        self._group_in = self._node_tree.nodes.new(type="NodeGroupInput")
        self._group_out = self._node_tree.nodes.new(type="NodeGroupOutput")
        self._inputs = self._node_tree.inputs
        self._outputs = self._node_tree.outputs

    def add_input(self, arg: FnArg):
        if arg.typ in {TypeKind.VEC2, TypeKind.VEC3, TypeKind.VEC4}:
            self._inputs.new(type="NodeSocketVector", name=arg.name)
            if arg.props in {TokenKind.OUT, TokenKind.INOUT}:
                self._outputs.new(type="NodeSocketVector", name=arg.name)

    def add_var(self, val):
        node = self._node_tree.nodes.new(type="ShaderNodeValue")
        node.outputs[0].default_value = val
        return node

class NodeGen:
    def __init__(self, ast: List[object], bl_context: bpy.types.Context):
        self.ast = ast
        self.bl_context = bl_context

        self.tree_type = self.bl_context.space_data.tree_type
        self.node_tree = self.bl_context.space_data.node_tree

        self.scope = [NodeTree(self.node_tree.name, self.tree_type, _global=True)]
        self.stop = False

    def error(self, msg):
        self.stop = True
        print(msg)

    def clear(self):
        self.node_tree.nodes.clear()

    def start(self):
        self.clear()
        self.emit(self.ast)

    def binary(self, node: Binary, ntree: NodeTree):
        left = node.left
        right = node.right
        if isinstance(node.left, Binary):
            left = self.binary(node.left, ntree)
        elif isinstance(node.left, Literal):
            left = node.left.value

        if isinstance(node.right, Binary):
            right = self.binary(node.right, ntree)
        elif isinstance(node.right, Literal):
            right = node.right.value

        if node.op.typ == TokenKind.PLUS:
            return float(left) + float(right)
        elif node.op.typ == TokenKind.MINUS:
            return float(left) - float(right)
        elif node.op.typ == TokenKind.STAR:
            return float(left) * float(right)
        elif node.op.typ == TokenKind.SLASH:
            return float(left) / float(right)
        else:
            self.error(f"{node.op} Not implemented")

    def expression(self, node, ntree: NodeTree):
        if isinstance(node, Binary):
            val = self.binary(node, ntree)
            return ntree.add_var(val)
        elif isinstance(node, Decl):
            assing = node.expr
            bl_node = self.expression(assing.init, ntree)
            bl_node.name = assing.name
            bl_node.label = assing.name
            return bl_node
        elif isinstance(node, Literal):
            return ntree.add_var(float(node.value))
        else:
            self.error(f"{node}: Not implemeneted")

    def emit(self, nodes: List[object]):
        curr_ntree = self.scope[-1]
        for node in nodes:
            if self.stop:
                break

            if isinstance(node, FnDef):
                sign = node.signature
                ntree = NodeTree(sign.name, self.tree_type)
                self.scope.append(ntree)
                for arg in sign.args:
                    ntree.add_input(arg)
                self.emit(node.body)
            else:
                self.expression(node, curr_ntree)
        self.scope.pop()
