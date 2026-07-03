"""
Boka-14 Interpreter
Tree-walking evaluator over the AST produced by parser.py.
"""

from ast_nodes import (
    Program, PrintStmt, Assign, IfStmt, FuncDef, ReturnStmt, ExprStmt,
    ForStmt, WhileStmt,
    NumberLit, StringLit, BoolLit, VarRef, BinOp, UnaryOp, Compare,
    TypeCast, CallExpr, InputExpr,
)
from errors import BokaRuntimeTruti, BokaAapatkal


class BokaFunction:
    """A user-defined Boka-14 function (via 'karya')."""
    def __init__(self, name, params, body, closure_env):
        self.name = name
        self.params = params
        self.body = body
        self.closure_env = closure_env


class ReturnSignal(Exception):
    """Internal control-flow signal for 'firao' (return)."""
    def __init__(self, value):
        self.value = value


class Environment:
    def __init__(self, parent=None, is_function_scope=False):
        self.vars = {}
        self.parent = parent
        # True only for the top-level environment of a function call.
        # Assignment stops climbing past this boundary, so functions
        # can't silently mutate outer/global variables (no accidental
        # 'nonlocal'-style leakage into enclosing scopes).
        self.is_function_scope = is_function_scope

    def get(self, name, line):
        env = self
        while env is not None:
            if name in env.vars:
                return env.vars[name]
            env = env.parent
        raise BokaRuntimeTruti(
            f"Variable '{name}' nijara parichaya bhuli jaichi. "
            f"(Eitha aage kebe define heini.)",
            line,
        )

    def set(self, name, value):
        """Assign in the nearest scope where it already exists, without
        crossing a function-call boundary; otherwise define locally."""
        env = self
        while env is not None:
            if name in env.vars:
                env.vars[name] = value
                return
            if env.is_function_scope:
                break
            env = env.parent
        self.vars[name] = value

    def define(self, name, value):
        self.vars[name] = value


class Interpreter:
    def __init__(self):
        self.global_env = Environment()

    def run(self, program: Program):
        for stmt in program.statements:
            self.exec_stmt(stmt, self.global_env)

    # ---- statement execution ----

    def exec_stmt(self, node, env):
        method_name = f"exec_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise BokaAapatkal(
                f"Interpreter ta '{type(node).__name__}' statement bujhi parila nahin. "
                f"Eitha ek internal bug.",
                getattr(node, "line", None),
            )
        method(node, env)

    def exec_PrintStmt(self, node: PrintStmt, env):
        value = self.eval_expr(node.expr, env)
        print(self.stringify(value))

    def exec_Assign(self, node: Assign, env):
        value = self.eval_expr(node.expr, env)
        env.set(node.name, value)

    def exec_IfStmt(self, node: IfStmt, env):
        condition = self.eval_expr(node.condition, env)
        if self.truthy(condition):
            block_env = Environment(parent=env)
            for stmt in node.then_block:
                self.exec_stmt(stmt, block_env)
        elif node.else_block is not None:
            block_env = Environment(parent=env)
            for stmt in node.else_block:
                self.exec_stmt(stmt, block_env)

    def exec_FuncDef(self, node: FuncDef, env):
        func = BokaFunction(node.name, node.params, node.body, env)
        env.define(node.name, func)

    def exec_ReturnStmt(self, node: ReturnStmt, env):
        value = self.eval_expr(node.expr, env) if node.expr is not None else None
        raise ReturnSignal(value)

    def exec_ForStmt(self, node: ForStmt, env):
        start = self.eval_expr(node.start, env)
        end = self.eval_expr(node.end, env)
        if not isinstance(start, (int, float)) or isinstance(start, bool) or \
           not isinstance(end, (int, float)) or isinstance(end, bool):
            raise BokaRuntimeTruti(
                "'pain' loop ra range kebala sankhya re hoi paribe.",
                node.line,
            )
        i = start
        # inclusive range, step +1 if end >= start else -1
        step = 1 if end >= start else -1
        loop_env = Environment(parent=env)
        while (step > 0 and i <= end) or (step < 0 and i >= end):
            loop_env.define(node.var_name, i)
            for stmt in node.body:
                self.exec_stmt(stmt, loop_env)
            i += step

    def exec_WhileStmt(self, node: WhileStmt, env):
        loop_env = Environment(parent=env)
        while self.truthy(self.eval_expr(node.condition, env)):
            for stmt in node.body:
                self.exec_stmt(stmt, loop_env)

    def exec_ExprStmt(self, node: ExprStmt, env):
        self.eval_expr(node.expr, env)

    # ---- expression evaluation ----

    def eval_expr(self, node, env):
        method_name = f"eval_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise BokaAapatkal(
                f"Interpreter ta '{type(node).__name__}' expression bujhi parila nahin. "
                f"Eitha ek internal bug.",
                getattr(node, "line", None),
            )
        return method(node, env)

    def eval_NumberLit(self, node: NumberLit, env):
        return node.value

    def eval_StringLit(self, node: StringLit, env):
        return node.value

    def eval_BoolLit(self, node: BoolLit, env):
        return node.value

    def eval_VarRef(self, node: VarRef, env):
        return env.get(node.name, node.line)

    def eval_UnaryOp(self, node: UnaryOp, env):
        val = self.eval_expr(node.operand, env)
        if node.op == "-":
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                raise BokaRuntimeTruti(
                    f"'-' chinha ta sankhya upare kama kare, kintu eitha sankhya nuhen.",
                    node.line,
                )
            return -val
        raise BokaAapatkal(f"Unknown unary operator '{node.op}'.", node.line)

    def eval_BinOp(self, node: BinOp, env):
        left = self.eval_expr(node.left, env)
        right = self.eval_expr(node.right, env)
        op = node.op

        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return self.stringify(left) + self.stringify(right)
            self._check_numeric(left, right, node.line)
            return left + right

        if op == "-":
            self._check_numeric(left, right, node.line)
            return left - right

        if op == "*":
            if isinstance(left, str) and isinstance(right, int) and not isinstance(right, bool):
                return left * right
            if isinstance(right, str) and isinstance(left, int) and not isinstance(left, bool):
                return right * left
            self._check_numeric(left, right, node.line)
            return left * right

        if op == "/":
            self._check_numeric(left, right, node.line)
            if right == 0:
                raise BokaRuntimeTruti(
                    "Sankhya badale bhagya saha bhaga karibaku chesta kara gala.",
                    node.line,
                )
            result = left / right
            return result

        if op == "%":
            self._check_numeric(left, right, node.line)
            if right == 0:
                raise BokaRuntimeTruti(
                    "Sankhya badale bhagya saha bhaga karibaku chesta kara gala.",
                    node.line,
                )
            return left % right

        raise BokaAapatkal(f"Unknown binary operator '{op}'.", node.line)

    def eval_Compare(self, node: Compare, env):
        left = self.eval_expr(node.left, env)
        right = self.eval_expr(node.right, env)
        op = node.op
        try:
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
            if op == ">":
                return left > right
            if op == "<":
                return left < right
            if op == ">=":
                return left >= right
            if op == "<=":
                return left <= right
        except TypeError:
            raise BokaRuntimeTruti(
                f"'{self.stringify(left)}' ebam '{self.stringify(right)}' ku tulana kariba asambhaba.",
                node.line,
            )
        raise BokaAapatkal(f"Unknown comparison operator '{op}'.", node.line)

    def eval_TypeCast(self, node: TypeCast, env):
        value = self.eval_expr(node.expr, env)
        try:
            if node.target_type == "int":
                if isinstance(value, str):
                    return int(value.strip())
                return int(value)
            if node.target_type == "float":
                if isinstance(value, str):
                    return float(value.strip())
                return float(value)
            if node.target_type == "string":
                return self.stringify(value)
        except (ValueError, TypeError):
            raise BokaRuntimeTruti(
                f"'{self.stringify(value)}' ku '{node.target_type}' re badaliba asambhaba.",
                node.line,
            )
        raise BokaAapatkal(f"Unknown type cast '{node.target_type}'.", node.line)

    def eval_InputExpr(self, node: InputExpr, env):
        prompt = ""
        if node.prompt is not None:
            prompt = self.stringify(self.eval_expr(node.prompt, env))
        return input(prompt)

    def eval_CallExpr(self, node: CallExpr, env):
        func = env.get(node.name, node.line)
        if not isinstance(func, BokaFunction):
            raise BokaRuntimeTruti(
                f"'{node.name}' ta ek function nuhen, eitha call kariba asambhaba.",
                node.line,
            )
        if len(node.args) != len(func.params):
            raise BokaRuntimeTruti(
                f"Function '{func.name}' ku {len(func.params)}ta argument chahin thila, "
                f"kintu {len(node.args)}ta dela gala.",
                node.line,
            )

        arg_values = [self.eval_expr(arg, env) for arg in node.args]
        call_env = Environment(parent=func.closure_env, is_function_scope=True)
        for param, value in zip(func.params, arg_values):
            call_env.define(param, value)

        try:
            for stmt in func.body:
                self.exec_stmt(stmt, call_env)
        except ReturnSignal as ret:
            return ret.value
        return None  # function fell off the end without 'firao'

    # ---- helpers ----

    def _check_numeric(self, left, right, line):
        if isinstance(left, bool) or isinstance(right, bool) or \
           not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise BokaRuntimeTruti(
                f"Ganita ta kebala sankhya upare kama kare "
                f"('{self.stringify(left)}' ebam '{self.stringify(right)}' re nuhen).",
                line,
            )

    def truthy(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return True

    def stringify(self, value):
        if value is None:
            return "michha_kichi"  # "nothing"-ish placeholder for None
        if isinstance(value, bool):
            return "satya" if value else "michha"
        if isinstance(value, float):
            if value == int(value):
                return f"{value:.1f}"
            # Round to 10 significant decimal places to avoid ugly
            # floating point artifacts like 3.3333333333333335
            rounded = round(value, 10)
            return f"{rounded:g}" if abs(rounded) >= 1e-4 or rounded == 0 else str(rounded)
        return str(value)
