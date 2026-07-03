# Boka-14

**"Serious technology does not require a serious personality."**

Boka-14 is an experimental programming language built around Romanized Odia keywords instead of traditional English syntax. It's not trying to be the next big language — it's an exploration of what programming feels like when expressed through familiar local language patterns, wrapped in a compiler that has a genuine sense of humor.

`.b14` is the file extension. `dekhaa "Namaskar Dunia!"` is where it all starts.

---

## Credits

**Boka-14 was designed by [ScuderiaFerrariSimp](https://github.com/ScuderiaFerrariSimp)** — the language concept, the philosophy, every keyword, the error-message personality, and the loop/function syntax decisions are theirs. This was a **vibecoded project**: ScuderiaFerrariSimp directed the design and iterated on it conversationally, and **Claude (Anthropic) wrote the Python implementation** — the lexer, parser, interpreter, and error system — based on that direction, testing it along the way to make sure it actually behaved the way it was designed to.

---

## Philosophy

- Romanized Odia keywords instead of English keywords
- Simple, beginner-friendly syntax
- Humorous compiler and runtime messages
- A lightweight interpreter, written in Python
- A language that doesn't take itself too seriously — while still being technically capable

---

## Installation / Requirements

- Python 3 (no external packages — pure standard library)

```bash
git clone https://github.com/ScuderiaFerrariSimp/Boka-14-Programming-language.git
cd Boka-14-Programming-language
python3 boka14.py examples/hello.b14
```

---

## Quick Start

```
dekhaa "Namaskar Dunia!"
```

Output:
```
Namaskar Dunia!
```

Run any `.b14` file with:
```bash
python3 boka14.py path/to/yourfile.b14
```

---

## Syntax Guide

### Comments
```
# this is a comment
```

### Variables
No declaration keyword — type is inferred from the value.
```
x = 10
pi = 3.14
name = "Boka"
```

### Print — `dekhaa`
```
dekhaa "Hello!"
dekhaa 42
dekhaa x + y
```

### Input — `pachara`
```
name = pachara("Enter your name: ")
age = int(pachara("Enter your age: "))
```

### If / Else — `jadi` / `nahele`
```
jadi age >= 18:
    dekhaa "Adult"
nahele:
    dekhaa "Minor"
```
Nesting is supported.

### For loops — `pain` ... `dekhi`
Runs the loop variable from `start` to `end`, inclusive, forwards or backwards automatically.
```
pain i = 1 dekhi 5:
    dekhaa i
```
```
pain i = 5 dekhi 1:
    dekhaa i
```

### While loops — `jaye`
```
i = 1
jaye i <= 5:
    dekhaa i
    i = i + 1
```

### Functions — `karya` / `pherai`
```
karya add(a, b):
    pherai a + b

dekhaa add(3, 4)
```
Recursion works:
```
karya factorial(n):
    jadi n <= 1:
        pherai 1
    nahele:
        pherai n * factorial(n - 1)

dekhaa factorial(5)
```
Functions have their own local scope — assigning to a variable inside a function never silently overwrites a variable of the same name outside it.

### Booleans — `satya` / `michha`
```
dekhaa satya
dekhaa michha
```

### Type casting — `int()`, `float()`, `string()`
```
a = int("42")
b = float("3.5")
c = string(99)
```

### Operators
| Operator | Meaning |
|---|---|
| `+ - * /` | arithmetic |
| `%` | modulo |
| `==` `!=` | equality |
| `>` `<` `>=` `<=` | comparison |
| `-x` | unary negation |

Strings support `+` (concatenation) and `*` (repetition, e.g. `"ha" * 3` → `hahaha`).

### Indentation
Blocks are defined by indentation, Python-style — use spaces, and be consistent. Every block-opening line ends with `:`.

---

## Full Keyword Reference

| Boka-14 | Meaning |
|---|---|
| `dekhaa` | print |
| `pachara` | input |
| `jadi` | if |
| `nahele` | else |
| `pain` | for |
| `dekhi` | "to" — used in for-loop ranges |
| `jaye` | while |
| `karya` | function |
| `pherai` | return |
| `satya` | true |
| `michha` | false |
| `int` / `float` / `string` | type casting |

---

## Error System — The Boka Personality

Boka-14 doesn't do dry stack traces. Every diagnostic falls into one of five tiers, each with its own tone:

**Boka Satarka** *(warning — non-fatal)*
```
Boka Satarka:
Variable 'x' nijara parichaya bhuli jaichi.
```

**Boka Bakya Truti** *(syntax error)*
```
Boka Bakya Truti:
Compiler line 14 ku 3 second dhari chahin rahila ebam sesare haar mani gala.
```

**Boka Runtime Truti** *(runtime error)*
```
Boka Runtime Truti:
Sankhya badale bhagya saha bhaga karibaku chesta kara gala.
```
This one fires on division/modulo by zero, undefined variables, invalid type casts, and other mid-execution problems.

**Boka Aapatkal** *(emergency — unexpected internal failure, e.g. missing file)*
```
Boka Aapatkal:
Program chetana paijaichi ebam ebe kama karibaku mana karuchhi.
```

**Atiadhika Boka Star** *(max chaos — the file broke something structurally, e.g. infinite recursion)*
```
Atiadhika Boka Star:
Dayakari ehi file re thiba ajatha katha ra matra kama karantu.
```

Every error also reports the line number it happened on.

---

## Project Structure

```
boka14/
├── boka14.py        # CLI entry point — run a .b14 file
├── lexer.py          # source text -> tokens
├── parser.py          # tokens -> AST (recursive descent)
├── ast_nodes.py       # AST node definitions
├── interpreter.py     # tree-walking evaluator over the AST
├── errors.py           # the five Boka error tiers
└── examples/            # sample .b14 programs
    ├── hello.b14
    ├── variables.b14
    ├── conditionals.b14
    ├── functions.b14
    ├── for_loop.b14
    ├── while_loop.b14
    ├── input_test.b14
    ├── edge_cases.b14
    └── stress_test.b14
```

**How it works, roughly:** `lexer.py` turns raw `.b14` text into a token stream (handling strings, numbers, keywords, indentation blocks). `parser.py` walks that token stream and builds an AST using recursive-descent parsing with standard operator precedence. `interpreter.py` walks the AST and executes it directly (a tree-walking interpreter — no bytecode, no compilation step, kept intentionally simple). `errors.py` defines the five-tier error hierarchy every diagnostic routes through.

---

## Current State

Implemented and tested:
- Variables (int, float, string, bool — type-inferred)
- `dekhaa` (print) and `pachara` (input)
- Arithmetic, comparison, and string operators
- `jadi` / `nahele` conditionals, including nesting
- `pain` (for) and `jaye` (while) loops
- `karya` / `pherai` functions, including recursion and proper local scoping
- Type casting via `int()`, `float()`, `string()`
- Full five-tier error system with Boka-14's signature humor

---

## Future Scope / Long-Term Vision

Boka-14 is still early. Planned directions:

- **Loop control** — `break`/`continue`-equivalent keywords (not yet decided)
- **Lists / arrays** — a Boka-flavored collection type
- **More operators** — logical `and`/`or`/`not` equivalents (currently no boolean combinators exist)
- **Modules** — importing one `.b14` file into another
- **Standard library** — math helpers, string utilities, maybe basic file I/O
- **Better error recovery** — currently the interpreter stops at the first error; multi-error reporting could help beginners more
- **Syntax highlighting** — a VS Code / Antigravity extension so `.b14` files aren't just plain text
- **REPL mode** — an interactive Boka-14 shell, not just file execution

None of this is committed yet — it's a running list of what would make sense next given where the language is today.

---

## Motto

**"Serious technology does not require a serious personality."**
