"""
Boka-14 AST Node Definitions
Plain data classes representing the parsed program structure.
"""


class Node:
    pass


# ---- Expressions ----

class NumberLit(Node):
    def __init__(self, value, line):
        self.value = value  # int or float
        self.line = line


class StringLit(Node):
    def __init__(self, value, line):
        self.value = value
        self.line = line


class BoolLit(Node):
    def __init__(self, value, line):
        self.value = value  # True/False
        self.line = line


class VarRef(Node):
    def __init__(self, name, line):
        self.name = name
        self.line = line


class BinOp(Node):
    def __init__(self, op, left, right, line):
        self.op = op
        self.left = left
        self.right = right
        self.line = line


class UnaryOp(Node):
    def __init__(self, op, operand, line):
        self.op = op
        self.operand = operand
        self.line = line


class Compare(Node):
    def __init__(self, op, left, right, line):
        self.op = op
        self.left = left
        self.right = right
        self.line = line


class TypeCast(Node):
    """int(x), float(x), string(x)"""
    def __init__(self, target_type, expr, line):
        self.target_type = target_type  # "int" | "float" | "string"
        self.expr = expr
        self.line = line


class CallExpr(Node):
    def __init__(self, name, args, line):
        self.name = name
        self.args = args  # list of Node
        self.line = line


class InputExpr(Node):
    """pachara "prompt" """
    def __init__(self, prompt, line):
        self.prompt = prompt  # Node or None
        self.line = line


# ---- Statements ----

class PrintStmt(Node):
    def __init__(self, expr, line):
        self.expr = expr
        self.line = line


class Assign(Node):
    def __init__(self, name, expr, line):
        self.name = name
        self.expr = expr
        self.line = line


class IfStmt(Node):
    def __init__(self, condition, then_block, else_block, line):
        self.condition = condition
        self.then_block = then_block  # list of statements
        self.else_block = else_block  # list of statements or None
        self.line = line


class FuncDef(Node):
    def __init__(self, name, params, body, line):
        self.name = name
        self.params = params  # list of str
        self.body = body      # list of statements
        self.line = line


class ReturnStmt(Node):
    def __init__(self, expr, line):
        self.expr = expr
        self.line = line


class ForStmt(Node):
    """pain i = start dekhi end: block"""
    def __init__(self, var_name, start, end, body, line):
        self.var_name = var_name
        self.start = start
        self.end = end
        self.body = body
        self.line = line


class WhileStmt(Node):
    """jaye condition: block"""
    def __init__(self, condition, body, line):
        self.condition = condition
        self.body = body
        self.line = line


class ExprStmt(Node):
    """An expression evaluated for its side effect (e.g. a bare function call)."""
    def __init__(self, expr, line):
        self.expr = expr
        self.line = line


class Program(Node):
    def __init__(self, statements):
        self.statements = statements
