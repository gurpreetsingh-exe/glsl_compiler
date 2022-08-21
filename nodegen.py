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

    def bin_op(self, left, right, op):
        node = self._node_tree.nodes.new(type="ShaderNodeMath")
        self._node_tree.links.new(left.outputs[0], node.inputs[0])
        self._node_tree.links.new(right.outputs[0], node.inputs[1])
        return node

    def find_var(self, name):
        node = self._node_tree.nodes.get(name)
        if not node:
            assert False, f"Undeclared identifier `{name}`"
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

        bl_node_left = None
        bl_node_right = None
        if type(left) == Ident:
            bl_node_left = ntree.find_var(left.name)
        if type(right) == Ident:
            bl_node_right = ntree.find_var(right.name)

        return ntree.bin_op(bl_node_left, bl_node_right, node.op)

    def expression(self, node, ntree: NodeTree):
        if isinstance(node, Binary):
            return self.binary(node, ntree)
        elif isinstance(node, Decl):
            assign = node.expr
            bl_node = self.expression(assign.init, ntree)
            bl_node.name = assign.name
            bl_node.label = assign.name
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
