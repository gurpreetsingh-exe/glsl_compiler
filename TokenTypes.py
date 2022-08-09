from enum import Enum, auto

class TypeKind(Enum):
    VOID = auto()

    INT = auto()
    FLOAT = auto()
    BOOL = auto()

    VEC2 = auto()
    VEC3 = auto()
    VEC4 = auto() # vec4 and color are same

    MAT2 = auto()
    MAT3= auto()
    MAT4 = auto()

Types = {
    "void" : TypeKind.VOID,
    "int"  : TypeKind.INT,
    "float": TypeKind.FLOAT,
    "bool" : TypeKind.BOOL,
    "vec2" : TypeKind.VEC2,
    "vec3" : TypeKind.VEC3,
    "vec4" : TypeKind.VEC4,
    "mat2" : TypeKind.MAT2,
    "mat3" : TypeKind.MAT3,
    "mat4" : TypeKind.MAT4,
}

class LiteralKind(Enum):
    INT = auto()
    FLOAT = auto()
    BOOL = auto()

class TokenKind(Enum):
    LITERAL     = auto()
    INTRINSIC   = auto()
    IDENT       = auto()
    TYPE        = auto()

    IN          = auto()
    OUT         = auto()
    INOUT       = auto()
    IF          = auto()
    ELSE        = auto()
    DO          = auto()
    WHILE       = auto()
    CONST       = auto()
    RETURN      = auto()

    PLUS        = auto()  # `+`
    MINUS       = auto()  # `-`
    STAR        = auto()  # `*`
    SLASH       = auto()  # `/`
    EQ          = auto()  # `=`
    SEMI        = auto()  # `;`
    LT          = auto()  # `<`
    GT          = auto()  # `>`
    COLON       = auto()  # `:`
    LPAREN      = auto()  # `(`
    RPAREN      = auto()  # `)`
    LCURLY      = auto()  # `{`
    RCURLY      = auto()  # `}`
    LBRACKET    = auto()  # `[`
    RBRACKET    = auto()  # `]`
    COMMA       = auto()  # `,`
    DOUBLEQUOTE = auto()  # `"`
    POUND       = auto()  # `#`
    AT          = auto()  # `@`
    AMPERSAND   = auto()  # `&`
    PIPE        = auto()  # `|`
    TILDE       = auto()  # `~`
    BANG        = auto()  # `!`
    PERCENT     = auto()  # `%`

    LT2         = auto()  # `<<`
    GT2         = auto()  # `>>`
    PIPE2       = auto()  # `||`
    AMPERSAND2  = auto()  # `&&`
    EQ2         = auto()  # `==`
    BANGEQ      = auto()  # `!=`

    EOF         = auto()
    UNDEFINED   = auto()

Keywords = {
    "if"    : TokenKind.IF,
    "else"  : TokenKind.ELSE,
    "do"    : TokenKind.DO,
    "while" : TokenKind.WHILE,
    "const" : TokenKind.CONST,
    "return": TokenKind.RETURN,
    "in"    : TokenKind.IN,
    "out"   : TokenKind.OUT,
    "inout" : TokenKind.INOUT,
}

Punctuators = {
    '+' : TokenKind.PLUS,
    '-' : TokenKind.MINUS,
    '*' : TokenKind.STAR,
    '/' : TokenKind.SLASH,
    '=' : TokenKind.EQ,
    ';' : TokenKind.SEMI,
    '<' : TokenKind.LT,
    '>' : TokenKind.GT,
    ':' : TokenKind.COLON,
    '(' : TokenKind.LPAREN,
    ')' : TokenKind.RPAREN,
    '{' : TokenKind.LCURLY,
    '}' : TokenKind.RCURLY,
    '[' : TokenKind.LBRACKET,
    ']' : TokenKind.RBRACKET,
    ',' : TokenKind.COMMA,
    '"' : TokenKind.DOUBLEQUOTE,
    '#' : TokenKind.POUND,
    '@' : TokenKind.AT,
    '&' : TokenKind.AMPERSAND,
    '|' : TokenKind.PIPE,
    '~' : TokenKind.TILDE,
    '!' : TokenKind.BANG,
    '%' : TokenKind.PERCENT,
    '<<': TokenKind.LT2,
    '>>': TokenKind.GT2,
    '&&': TokenKind.AMPERSAND2,
    '||': TokenKind.PIPE2,
    '==': TokenKind.EQ2,
    '!=': TokenKind.BANGEQ,
}
