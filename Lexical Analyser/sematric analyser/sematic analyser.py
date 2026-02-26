symbol_table = {}

def semantic_analyzer(lines):
    errors = []

    for line_no, line in enumerate(lines, start=1):
        tokens = line.strip().split()

        if not tokens:
            continue

        # Variable declaration: int a
        if tokens[0] == "int":
            if len(tokens) != 2:
                errors.append(f"Line {line_no}: Invalid declaration syntax")
            else:
                var = tokens[1]
                if var in symbol_table:
                    errors.append(f"Line {line_no}: Variable '{var}' redeclared")
                else:
                    symbol_table[var] = "int"

        # Assignment: a = 10 or a = b
        elif "=" in tokens:
            var = tokens[0]

            if var not in symbol_table:
                errors.append(f"Line {line_no}: Variable '{var}' used before declaration")

            value = tokens[2]
            if value.isalpha() and value not in symbol_table:
                errors.append(f"Line {line_no}: Variable '{value}' used before declaration")

        else:
            errors.append(f"Line {line_no}: Invalid statement")

    return errors


# -------- MAIN --------
with open("semantic_input.txt", "r") as f:
    lines = f.readlines()

errors = semantic_analyzer(lines)

with open("semantic_output.txt", "w") as f:
    if errors:
        f.write("Semantic Analysis Failed\n")
        for error in errors:
            f.write(error + "\n")
        print("Semantic Analysis Failed")
    else:
        f.write("Semantic Analysis Successful\n")
        print("Semantic Analysis Successful")