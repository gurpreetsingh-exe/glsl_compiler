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

    def link_or_set_at(self, socket_index, value, node):
        if issubclass(type(value), bpy.types.Node):
            self._node_tree.links.new(value.outputs[0], node.inputs[socket_index])
        else:
            node.inputs[socket_index].default_value = float(value)

    def node_op_from_token(self, typ):
        match typ:
            case TokenKind.PLUS:  return "ADD"
            case TokenKind.MINUS: return "SUBTRACT"
            case TokenKind.STAR:  return "MULTIPLY"
            case TokenKind.SLASH: return "DIVIDE"

    def set_binary_operation(self, node, op):
        if node.type == "MATH":
            node.operation = self.node_op_from_token(op.typ)
        elif node.type == "VECT_MATH":
            assert False, "Not implemented"

    def bin_op(self, left, right, op):
        node = self._node_tree.nodes.new(type="ShaderNodeMath")
        self.set_binary_operation(node, op)
        self.link_or_set_at(0, left, node)
        self.link_or_set_at(1, right, node)
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
