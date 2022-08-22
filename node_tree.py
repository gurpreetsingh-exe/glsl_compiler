import bpy
from .TokenTypes import TokenKind, TypeKind
from .ast import FnArg

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
