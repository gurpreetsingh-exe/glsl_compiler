class FnDef:
    def __init__(self, signature, body):
        self.signature = signature
        self.body = body

class FnArg:
    def __init__(self, name, typ, props=None):
        self.name = name
        self.typ = typ
        # could be one of these 'in', 'out', 'inout' or unspecified 'None' by default
        self.props = props

class FnSig:
    def __init__(self, name, args, return_typ):
        self.name = name
        self.args = args
        self.return_typ = return_typ

class Binary:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class Unary:
    def __init__(self, op, right):
        self.op = op
        self.right = right

class Decl:
    def __init__(self, typ, expr):
        self.typ = typ
        self.expr = expr

class Assign:
    def __init__(self, name, init):
        self.name = name
        self.init = init

class Ident:
    def __init__(self, name):
        self.name = name

class Call:
    def __init__(self, name, args):
        self.name = name
        self.args = args

