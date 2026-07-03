"""
Boka-14 Lexer
Converts raw .b14 source text into a stream of tokens.
"""

from errors import BokaBakyaTruti


KEYWORDS = {
    "dekhaa": "DEKHAA",       # print
    "pachara": "PACHARA",     # input
    "jadi": "JADI",           # if
    "nahele": "NAHELE",       # else
    "pain": "PAIN",           # for
    "dekhi": "DEKHI",         # to/until (for-loop range word)
    "jaye": "JAYE",           # while
    "karya": "KARYA",         # function def
    "satya": "SATYA",         # true
    "michha": "MICHHA",       # false
    "pherai": "PHERAI",       # return
    "int": "INT_TYPE",        # int type cast/keyword
    "float": "FLOAT_TYPE",    # float type cast/keyword
    "string": "STRING_TYPE",  # string type cast/keyword
}

# Multi-character operators must be listed before their single-char prefixes
SYMBOLS = [
    ("==", "EQEQ"),
    ("!=", "NOTEQ"),
    (">=", "GTEQ"),
    ("<=", "LTEQ"),
    ("+", "PLUS"),
    ("-", "MINUS"),
    ("*", "STAR"),
    ("/", "SLASH"),
    ("%", "PERCENT"),
    ("=", "EQ"),
    (">", "GT"),
    ("<", "LT"),
    ("(", "LPAREN"),
    (")", "RPAREN"),
    (":", "COLON"),
    (",", "COMMA"),
]


class Token:
    __slots__ = ("type", "value", "line")

    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"


def tokenize(source):
    """Turn source text into a flat list of tokens, including
    INDENT/DEDENT/NEWLINE tokens for block structure (Python-style)."""
    tokens = []
    indent_stack = [0]
    lines = source.split("\n")

    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line

        # Strip comments (# to end of line), but not inside string literals
        line = _strip_comment(line)

        # Skip fully blank (post-comment-strip) lines: no NEWLINE emitted
        if line.strip() == "":
            continue

        # Compute indentation (spaces only; tabs treated as error to avoid ambiguity)
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)

        if indent > indent_stack[-1]:
            indent_stack.append(indent)
            tokens.append(Token("INDENT", indent, line_no))
        elif indent < indent_stack[-1]:
            while indent < indent_stack[-1]:
                indent_stack.pop()
                tokens.append(Token("DEDENT", indent, line_no))
            if indent != indent_stack[-1]:
                raise BokaBakyaTruti(
                    f"Indentation ku milaiba re asubidha hela (line {line_no}). "
                    f"Boka bujhi parila nahin kete space chahin thila.",
                    line_no,
                )

        # Tokenize the rest of this line
        pos = 0
        length = len(stripped)
        while pos < length:
            ch = stripped[pos]

            if ch == " ":
                pos += 1
                continue

            # String literal
            if ch == '"':
                end = stripped.find('"', pos + 1)
                if end == -1:
                    raise BokaBakyaTruti(
                        f"Line {line_no} re '\"' bandha hela nahin. "
                        f"String ta adha re chhadi dela!",
                        line_no,
                    )
                value = stripped[pos + 1:end]
                tokens.append(Token("STRING", value, line_no))
                pos = end + 1
                continue

            # Number literal (int or float)
            if ch.isdigit():
                start = pos
                is_float = False
                while pos < length and (stripped[pos].isdigit() or stripped[pos] == "."):
                    if stripped[pos] == ".":
                        if is_float:
                            break
                        is_float = True
                    pos += 1
                num_str = stripped[start:pos]
                if is_float:
                    tokens.append(Token("FLOAT", float(num_str), line_no))
                else:
                    tokens.append(Token("INT", int(num_str), line_no))
                continue

            # Identifier or keyword
            if ch.isalpha() or ch == "_":
                start = pos
                while pos < length and (stripped[pos].isalnum() or stripped[pos] == "_"):
                    pos += 1
                word = stripped[start:pos]
                if word in KEYWORDS:
                    tokens.append(Token(KEYWORDS[word], word, line_no))
                else:
                    tokens.append(Token("IDENT", word, line_no))
                continue

            # Symbols / operators
            matched = False
            for sym, name in SYMBOLS:
                if stripped.startswith(sym, pos):
                    tokens.append(Token(name, sym, line_no))
                    pos += len(sym)
                    matched = True
                    break
            if matched:
                continue

            raise BokaBakyaTruti(
                f"Line {line_no} re '{ch}' chinha ta Boka-14 bujhena.",
                line_no,
            )

        tokens.append(Token("NEWLINE", None, line_no))

    # Close any remaining open indents
    final_line = len(lines) + 1
    while indent_stack[-1] != 0:
        indent_stack.pop()
        tokens.append(Token("DEDENT", 0, final_line))

    tokens.append(Token("EOF", None, final_line))
    return tokens


def _strip_comment(line):
    """Remove a # comment from a line, respecting string literals."""
    in_string = False
    for i, ch in enumerate(line):
        if ch == '"':
            in_string = not in_string
        elif ch == "#" and not in_string:
            return line[:i]
    return line
