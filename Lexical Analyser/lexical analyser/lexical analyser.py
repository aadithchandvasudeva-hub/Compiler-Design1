# Phase 1: Lexical Analyzer in Python
# This program breaks input into tokens like keywords, identifiers, numbers, and operators

import re

KEYWORDS = {"int", "float", "if", "else", "return", "while"}

OPERATORS = {"+", "-", "*", "/", "=", "=="}

SEPARATORS = {";", "(", ")", "{", "}"}

def lexical_analyzer(code):
    tokens = re.findall(r"[A-Za-z_]\w*|\d+|==|=|\+|\-|\*|/|[();{}]", code)

    for token in tokens:
        if token in KEYWORDS:
            print(f"KEYWORD     : {token}")
        elif token in OPERATORS:
            print(f"OPERATOR    : {token}")
        elif token in SEPARATORS:
            print(f"SEPARATOR   : {token}")
        elif token.isdigit():
            print(f"NUMBER      : {token}")
        else:
            print(f"IDENTIFIER  : {token}")

# Read input from file
with open("input.txt", "r") as file:
    code = file.read()

print("Lexical Analysis Output:\n")
lexical_analyzer(code)