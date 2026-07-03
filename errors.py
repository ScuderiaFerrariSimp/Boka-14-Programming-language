"""
Boka-14 Error Hierarchy
Every diagnostic in Boka-14 routes through one of these five tiers.
"""


class BokaError(Exception):
    """Base class for all Boka-14 diagnostics."""
    tag = "Boka Truti"

    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(message)

    def render(self):
        loc = f" (line {self.line})" if self.line is not None else ""
        return f"{self.tag}:\n{self.message}{loc}"


class BokaSatarka(BokaError):
    """Warning tier - non-fatal, e.g. unused variable."""
    tag = "Boka Satarka"


class BokaBakyaTruti(BokaError):
    """Syntax error tier - fatal, raised by lexer/parser."""
    tag = "Boka Bakya Truti"


class BokaRuntimeTruti(BokaError):
    """Runtime error tier - fatal, raised during evaluation
    (e.g. divide by zero, undefined variable)."""
    tag = "Boka Runtime Truti"


class BokaAapatkal(BokaError):
    """Emergency tier - fatal, unexpected internal interpreter failure."""
    tag = "Boka Aapatkal"


class AtiadhikaBokaStar(BokaError):
    """Max-boka tier - file is too chaotic to even attempt running
    (e.g. too many syntax errors, absurd nesting)."""
    tag = "Atiadhika Boka Star"
