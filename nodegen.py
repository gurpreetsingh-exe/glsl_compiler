import bpy

from .ast import *
from .TokenTypes import *


class NodeTree:
    def __init__(self, name, typ):
        self._node_tree = bpy.data.node_groups.new(type=typ, name=name)
        self._group_in = self._node_tree.nodes.new(type="NodeGroupInput")
        self._group_out = self._node_tree.nodes.new(type="NodeGroupOutput")
        self._inputs = self._node_tree.inputs
        self._outputs = self._node_tree.outputs

    def add_input(self, arg):
        if arg.typ in {TypeKind.VEC2, TypeKind.VEC3, TypeKind.VEC4}:
            self._inputs.new(type="NodeSocketVector", name=arg.name)
            if arg.props in {TokenKind.OUT, TokenKind.INOUT}:
                self._outputs.new(type="NodeSocketVector", name=arg.name)

class NodeGen:
    def __init__(self, ast, bl_context):
        self.ast = ast
        self.bl_context = bl_context

        self.tree_type = self.bl_context.space_data.tree_type
        self.node_tree = self.bl_context.space_data.node_tree

        self.stop = False

    def error(self, msg):
        self.stop = True
        print(msg)

    def clear(self):
        self.node_tree.nodes.clear()

    def start(self):
        self.clear()
        self.emit(self.ast)

    def emit(self, nodes):
        for node in nodes:
            if self.stop:
                break

            if isinstance(node, FnDef):
                sign = node.signature
                ntree = NodeTree(sign.name, self.tree_type)
                for arg in sign.args:
                    ntree.add_input(arg)
                self.emit(node.body)
            else:
                self.error(f"{node}: Not implemeneted")
