import bpy

from .ast import *
from .node_tree import NodeTree
from .Lexer import Literal
from .TokenTypes import *

from typing import List

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

    def evaluate(self, node, ntree: NodeTree):
        ty = type(node)
        if ty == Binary:
            return self.binary(node, ntree)
        elif ty == Literal:
            return node.value
        elif ty == Ident:
            return ntree.find_var(node.name)
        else:
            assert False, f"{node}: in evaluate()"

    def binary(self, node: Binary, ntree: NodeTree):
        left = self.evaluate(node.left, ntree)
        right = self.evaluate(node.right, ntree)

        return ntree.bin_op(left, right, node.op)

    def expression(self, node, ntree: NodeTree):
        ty = type(node)
        if ty == Binary:
            return self.binary(node, ntree)
        elif ty == Decl:
            assign = node.expr
            bl_node = self.expression(assign.init, ntree)
            bl_node.name = assign.name
            bl_node.label = assign.name
            return bl_node
        elif ty == Literal:
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
