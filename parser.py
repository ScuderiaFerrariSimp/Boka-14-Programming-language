"""
Boka-14 Parser
Recursive-descent parser turning a token stream into an AST.

Grammar (informal):

program      := statement*
statement    := print_stmt | if_stmt | func_def | return_stmt
              | assign_stmt | expr_stmt
print_stmt   := DEKHAA expr NEWLINE
if_stmt      := JADI expr COLON block (NAHELE COLON block)?
func_def     := KARYA IDENT LPAREN params? RPAREN COLON block
return_stmt  := FIRAO expr? NEWLINE
assign_stmt  := IDENT EQ expr NEWLINE
expr_stmt    := expr NEWLINE
block        := NEWLINE INDENT statement* DEDENT

expr         := comparison
comparison   := additive ((EQEQ|NOTEQ|GT|LT|GTEQ|LTEQ) additive)*
additive     := term ((PLUS|MINUS) term)*
term         := unary ((STAR|SLASH|PERCENT) unary)*
unary        := (MINUS) unary | primary
primary      := INT | FLOAT | STRING | SATYA | MICHHA
              | IDENT | IDENT LPAREN args? RPAREN
              | INT_TYPE LPAREN expr RPAREN
              | FLOAT_TYPE LPAREN expr RPAREN
              | STRING_TYPE LPAREN expr RPAREN
              | PACHARA (LPAREN expr? RPAREN)?
              | LPAREN expr RPAREN
"""

from ast_nodes import (
    Program, PrintStmt, Assign, IfStmt, FuncDef, ReturnStmt, ExprStmt,
    ForStmt, WhileStmt,
    NumberLit, StringLit, BoolLit, VarRef, BinOp, UnaryOp, Compare,
    TypeCast, CallExpr, InputExpr,
)
from errors import BokaBakyaTruti


COMPARE_OPS = {"EQEQ", "NOTEQ", "GT", "LT", "GTEQ", "LTEQ"}
ADD_OPS = {"PLUS", "MINUS"}
MUL_OPS = {"STAR", "SLASH", "PERCENT"}
TYPE_KEYWORDS = {"INT_TYPE": "int", "FLOAT_TYPE": "float", "STRING_TYPE": "string"}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---- token helpers ----

    def peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def check(self, type_):
        return self.peek().type == type_

    def match(self, *types):
        if self.peek().type in types:
            return self.advance()
        return None

    def expect(self, type_, what):
        tok = self.peek()
        if tok.type != type_:
            raise BokaBakyaTruti(
                f"'{what}' asha karithila, kintu '{tok.value if tok.value is not None else tok.type}' milila.",
                tok.line,
            )
        return self.advance()

    def skip_newlines(self):
        while self.check("NEWLINE"):
            self.advance()

    # ---- entry point ----

    def parse_program(self):
        statements = []
        self.skip_newlines()
        while not self.check("EOF"):
            statements.append(self.parse_statement())
            self.skip_newlines()
        return Program(statements)

    # ---- statements ----

    def parse_block(self):
        """Expects NEWLINE INDENT statement* DEDENT"""
        self.expect("NEWLINE", "line ra sesha")
        self.skip_newlines()
        self.expect("INDENT", "indentation (block start)")
        statements = []
        self.skip_newlines()
        while not self.check("DEDENT") and not self.check("EOF"):
            statements.append(self.parse_statement())
            self.skip_newlines()
        self.expect("DEDENT", "indentation (block end)")
        return statements

    def parse_statement(self):
        tok = self.peek()

        if tok.type == "DEKHAA":
            return self.parse_print()
        if tok.type == "JADI":
            return self.parse_if()
        if tok.type == "PAIN":
            return self.parse_for()
        if tok.type == "JAYE":
            return self.parse_while()
        if tok.type == "KARYA":
            return self.parse_func_def()
        if tok.type == "PHERAI":
            return self.parse_return()
        if tok.type == "IDENT" and self.peek(1).type == "EQ":
            return self.parse_assign()

        # fallback: expression statement
        expr = self.parse_expr()
        self.expect("NEWLINE", "line ra sesha")
        return ExprStmt(expr, tok.line)

    def parse_print(self):
        tok = self.advance()  # DEKHAA
        expr = self.parse_expr()
        self.expect("NEWLINE", "line ra sesha")
        return PrintStmt(expr, tok.line)

    def parse_assign(self):
        name_tok = self.advance()  # IDENT
        self.expect("EQ", "=")
        expr = self.parse_expr()
        self.expect("NEWLINE", "line ra sesha")
        return Assign(name_tok.value, expr, name_tok.line)

    def parse_if(self):
        tok = self.advance()  # JADI
        condition = self.parse_expr()
        self.expect("COLON", ":")
        then_block = self.parse_block()
        else_block = None
        # allow blank lines between blocks before checking for NAHELE
        save_pos = self.pos
        self.skip_newlines()
        if self.check("NAHELE"):
            self.advance()
            self.expect("COLON", ":")
            else_block = self.parse_block()
        else:
            self.pos = save_pos
        return IfStmt(condition, then_block, else_block, tok.line)

    def parse_func_def(self):
        tok = self.advance()  # KARYA
        name_tok = self.expect("IDENT", "function naam")
        self.expect("LPAREN", "(")
        params = []
        if not self.check("RPAREN"):
            params.append(self.expect("IDENT", "parameter naam").value)
            while self.match("COMMA"):
                params.append(self.expect("IDENT", "parameter naam").value)
        self.expect("RPAREN", ")")
        self.expect("COLON", ":")
        body = self.parse_block()
        return FuncDef(name_tok.value, params, body, tok.line)

    def parse_return(self):
        tok = self.advance()  # PHERAI
        if self.check("NEWLINE"):
            expr = None
        else:
            expr = self.parse_expr()
        self.expect("NEWLINE", "line ra sesha")
        return ReturnStmt(expr, tok.line)

    def parse_for(self):
        tok = self.advance()  # PAIN
        var_tok = self.expect("IDENT", "loop variable naam")
        self.expect("EQ", "=")
        start = self.parse_expr()
        self.expect("DEKHI", "dekhi")
        end = self.parse_expr()
        self.expect("COLON", ":")
        body = self.parse_block()
        return ForStmt(var_tok.value, start, end, body, tok.line)

    def parse_while(self):
        tok = self.advance()  # JAYE
        condition = self.parse_expr()
        self.expect("COLON", ":")
        body = self.parse_block()
        return WhileStmt(condition, body, tok.line)

    # ---- expressions (precedence climbing) ----

    def parse_expr(self):
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_additive()
        while self.peek().type in COMPARE_OPS:
            op_tok = self.advance()
            right = self.parse_additive()
            left = Compare(op_tok.value, left, right, op_tok.line)
        return left

    def parse_additive(self):
        left = self.parse_term()
        while self.peek().type in ADD_OPS:
            op_tok = self.advance()
            right = self.parse_term()
            left = BinOp(op_tok.value, left, right, op_tok.line)
        return left

    def parse_term(self):
        left = self.parse_unary()
        while self.peek().type in MUL_OPS:
            op_tok = self.advance()
            right = self.parse_unary()
            left = BinOp(op_tok.value, left, right, op_tok.line)
        return left

    def parse_unary(self):
        if self.check("MINUS"):
            tok = self.advance()
            operand = self.parse_unary()
            return UnaryOp("-", operand, tok.line)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()

        if tok.type == "INT":
            self.advance()
            return NumberLit(tok.value, tok.line)

        if tok.type == "FLOAT":
            self.advance()
            return NumberLit(tok.value, tok.line)

        if tok.type == "STRING":
            self.advance()
            return StringLit(tok.value, tok.line)

        if tok.type == "SATYA":
            self.advance()
            return BoolLit(True, tok.line)

        if tok.type == "MICHHA":
            self.advance()
            return BoolLit(False, tok.line)

        if tok.type in TYPE_KEYWORDS:
            self.advance()
            self.expect("LPAREN", "(")
            expr = self.parse_expr()
            self.expect("RPAREN", ")")
            return TypeCast(TYPE_KEYWORDS[tok.type], expr, tok.line)

        if tok.type == "PACHARA":
            self.advance()
            prompt = None
            if self.match("LPAREN"):
                if not self.check("RPAREN"):
                    prompt = self.parse_expr()
                self.expect("RPAREN", ")")
            return InputExpr(prompt, tok.line)

        if tok.type == "IDENT":
            self.advance()
            if self.check("LPAREN"):
                self.advance()
                args = []
                if not self.check("RPAREN"):
                    args.append(self.parse_expr())
                    while self.match("COMMA"):
                        args.append(self.parse_expr())
                self.expect("RPAREN", ")")
                return CallExpr(tok.value, args, tok.line)
            return VarRef(tok.value, tok.line)

        if tok.type == "LPAREN":
            self.advance()
            expr = self.parse_expr()
            self.expect("RPAREN", ")")
            return expr

        raise BokaBakyaTruti(
            f"Ehi thare '{tok.value if tok.value is not None else tok.type}' asha kari nathila. "
            f"Boka confuse hei gala.",
            tok.line,
        )


def parse(tokens):
    return Parser(tokens).parse_program()
