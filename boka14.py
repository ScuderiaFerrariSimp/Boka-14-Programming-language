#!/usr/bin/env python3
"""
Boka-14 - "Serious technology does not require a serious personality."

Usage:
    python3 boka14.py <file.b14>
"""

import sys

from lexer import tokenize
from parser import parse
from interpreter import Interpreter
from errors import BokaError, AtiadhikaBokaStar


def run_file(path):
    if not path.endswith(".b14"):
        print("Boka Satarka:")
        print(f"'{path}' ta '.b14' file nuhen. Tathapi chesta karuchi...")

    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print("Boka Aapatkal:")
        print(f"'{path}' file ta khunja nathila. Kouthi harai gala?")
        sys.exit(1)
    except OSError as e:
        print("Boka Aapatkal:")
        print(f"'{path}' padhibaku asubidha hela: {e}")
        sys.exit(1)

    try:
        tokens = tokenize(source)
        program = parse(tokens)
        interpreter = Interpreter()
        interpreter.run(program)
    except BokaError as e:
        print(e.render())
        sys.exit(1)
    except RecursionError:
        err = AtiadhikaBokaStar(
            "Dayakari ehi file re thiba ajatha katha ra matra kama karantu. "
            "(Program ta bahuta gabhira re chali gala - infinite recursion?)"
        )
        print(err.render())
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nBoka Satarka:\nProgram ta manda re bandha hela (Ctrl+C).")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Boka Bakya Truti:")
        print("Kemiti chalaibe eitha bhulijaicha? Chesta karantu: python3 boka14.py <file.b14>")
        sys.exit(1)
    run_file(sys.argv[1])


if __name__ == "__main__":
    main()
