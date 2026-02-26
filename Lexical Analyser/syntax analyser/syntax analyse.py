import re


def syntax_analyzer(expression):
    # Grammar: identifier = identifier operator identifier
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[+\-*/]\s*[a-zA-Z_][a-zA-Z0-9_]*$'

    if re.match(pattern, expression):
        return "Syntax is VALID"
    else:
        return "Syntax is INVALID"


# Read input
with open("input.txt", "r") as f:
    expr = f.read().strip()

result = syntax_analyzer(expr)

# Write output
with open("output.txt", "w") as f:
    f.write(result)

print(result)